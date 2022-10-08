# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from asyncio.events import AbstractEventLoop
from asyncio.events import get_event_loop
from asyncio.futures import Future
from asyncio.protocols import Protocol
from asyncio.transports import BaseTransport
from typing import Any
from typing import Optional
import warnings
import xml.etree.ElementTree as ET

from aioraven.reader import RAVEnReader


class DeviceWarning(Warning):
    """The device has generated a warning message."""

    def __init__(self, message: str) -> None:
        """
        Construct a DeviceWarning.

        :param message: The reason for which the device is warning us.
        """
        super().__init__('Warning from RAVEn device: ' + message)


class UnknownCommandWarning(DeviceWarning):
    """A recently executed command is not supported by the device."""

    MESSAGE = 'Unknown command'

    def __init__(self) -> None:
        """Construct a UnknownCommandWarning."""
        super().__init__(self.MESSAGE)


class RAVEnReaderProtocol(Protocol):
    """Deserialize data fragments from a RAVEn device."""

    _closed: Future[None]
    _reader: Optional[RAVEnReader]

    def __init__(
        self,
        reader: RAVEnReader,
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        """
        Construct a RAVEnRaderProtocol.

        :param reader: The `RAVEnReader` instance to which deserialized
          fragments are passed.
        :param loop: The event loop instance to use.
        """
        if loop is None:
            self._loop = get_event_loop()
        else:
            self._loop = loop
        self._reader = reader
        self._closed = self._loop.create_future()

    def _reset(self) -> None:
        self._parser = ET.XMLPullParser(events=('end',))
        self._parser.feed(b'<?xml version="1.0" encoding="ASCII"?><root>')

    def _get_close_waiter(self, stream: Any) -> Future[None]:
        return self._closed

    def connection_made(self, transport: BaseTransport) -> None:
        self._reset()

    def connection_lost(self, exc: Optional[Exception]) -> None:
        if self._reader is not None:
            if exc is None:
                self._reader.feed_eof()
            else:
                self._reader.set_exception(exc)
        if not self._closed.done():
            if exc is None:
                self._closed.set_result(None)
            else:
                self._closed.set_exception(exc)
        self._reader = None

    def data_received(self, data: bytes) -> None:
        if not self._reader:
            return

        self._parser.feed(data)

        events = self._parser.read_events()
        while True:
            try:
                _, element = next(events)
            except StopIteration:
                return
            except ET.ParseError as err:
                self._reader.set_exception(err)
                self._reset()
            else:
                if element.tag == 'Warning':
                    try:
                        e = next(iter(element), None)
                        if e is not None and e.text is not None:
                            if e.text == UnknownCommandWarning.MESSAGE:
                                warnings.warn(UnknownCommandWarning())
                            else:
                                warnings.warn(DeviceWarning(e.text))
                        else:
                            warnings.warn(DeviceWarning('Unknown warning'))
                    except Warning as err:
                        self._reader.set_exception(err)
                else:
                    self._reader.feed_element(element)

    def eof_received(self) -> None:
        if not self._reader:
            return

        self._parser.feed(b'</root>')

        try:
            self._parser.close()
        except ET.ParseError as err:
            self._reader.set_exception(err)
        finally:
            self._reader.feed_eof()

    def __del__(self) -> None:
        try:
            closed = self._closed
        except AttributeError:
            pass
        else:
            if closed.done() and not closed.cancelled():
                closed.exception()
