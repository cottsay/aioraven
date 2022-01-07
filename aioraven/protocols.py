# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from asyncio.protocols import Protocol
from xml.etree.ElementTree import ParseError
from xml.etree.ElementTree import XMLPullParser


class RAVEnReaderProtocol(Protocol):
    """Deserialize data fragments from a RAVEn device."""

    def __init__(self, raven_reader):
        self._raven_reader = raven_reader
        self._parser = None

    def _reset(self):
        self._parser = XMLPullParser(events=('end',))
        self._parser.feed(b'<?xml version="1.0" encoding="ASCII"?><root>')

    def connection_made(self, transport):
        self._reset()

    def connection_lost(self, exc):
        if self._raven_reader is not None:
            if exc is None:
                self._raven_reader.feed_eof()
            else:
                self._raven_reader.set_exception(exc)
        self._raven_reader = None
        self._parser = None

    def data_received(self, data):
        self._parser.feed(data)

        events = self._parser.read_events()
        while True:
            try:
                _, element = next(events)
            except StopIteration:
                return
            except ParseError as e:
                self._raven_reader.set_exception(e)
                self._reset()
            else:
                self._raven_reader.feed_element(element)

    def eof_received(self):
        self._parser.feed(b'</root>')

        try:
            self._parser.close()
        except ParseError as e:
            if self._raven_reader:
                self._raven_reader.set_exception(e)
        finally:
            self._raven_reader.feed_eof()
