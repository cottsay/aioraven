# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from asyncio.protocols import Protocol
import warnings
import xml.etree.ElementTree as ET


class DeviceWarning(Warning):
    """The device has generated a warning message."""

    def __init__(self, message):
        super().__init__('Warning from RAVEn device: ' + message)


class UnknownCommandWarning(DeviceWarning):
    """A recently executed command is not supported by the device."""

    MESSAGE = 'Unknown command'

    def __init__(self):
        super().__init__(self.MESSAGE)


class RAVEnReaderProtocol(Protocol):
    """Deserialize data fragments from a RAVEn device."""

    def __init__(self, reader):
        self._reader = reader
        self._parser = None

    def _reset(self):
        self._parser = ET.XMLPullParser(events=('end',))
        self._parser.feed(b'<?xml version="1.0" encoding="ASCII"?><root>')

    def connection_made(self, transport):
        self._reset()

    def connection_lost(self, exc):
        if self._reader is not None:
            if exc is None:
                self._reader.feed_eof()
            else:
                self._reader.set_exception(exc)
        self._reader = None
        self._parser = None

    def data_received(self, data):
        self._parser.feed(data)

        events = self._parser.read_events()
        while True:
            try:
                _, element = next(events)
            except StopIteration:
                return
            except ET.ParseError as e:
                self._reader.set_exception(e)
                self._reset()
            else:
                if element.tag == 'Warning':
                    try:
                        e = next(iter(element), None)
                        text = e.text if e is not None else 'Unknown warning'
                        if text == UnknownCommandWarning.MESSAGE:
                            warnings.warn(UnknownCommandWarning())
                        else:
                            warnings.warn(DeviceWarning(text))
                    except Warning as e:
                        self._reader.set_exception(e)
                else:
                    self._reader.feed_element(element)

    def eof_received(self):
        self._parser.feed(b'</root>')

        try:
            self._parser.close()
        except ET.ParseError as e:
            self._reader.set_exception(e)
        finally:
            self._reader.feed_eof()
