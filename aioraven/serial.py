# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from asyncio.events import get_event_loop

from aioraven.protocols import RAVEnReaderProtocol
from aioraven.streams import RAVEnReader
from aioraven.streams import RAVEnStreamDevice
from aioraven.streams import RAVEnWriter
from serial_asyncio import create_serial_connection


async def open_serial_connection(*args, loop=None, **kwargs):
    if loop is None:
        loop = get_event_loop()
    reader = RAVEnReader(loop=loop)
    protocol = RAVEnReaderProtocol(reader)
    kwargs.setdefault('baudrate', 115200)
    transport, _ = await create_serial_connection(
        loop, lambda: protocol, *args, **kwargs)
    writer = RAVEnWriter(transport)
    return reader, writer


class RAVEnSerialDevice(RAVEnStreamDevice):

    def __init__(self, url, *args, loop=None, **kwargs):
        self._url = url
        self._args = args
        self._loop = loop
        self._kwargs = kwargs

    def __repr__(self):
        info = [self.__class__.__name__]
        info.append('url=%s' % self._url)
        return '<%s>' % ' '.join(info)

    async def open(self):
        if self._reader or self._writer:
            return
        self._reader, self._writer = await open_serial_connection(
            url=self._url, *self._args, loop=self._loop, **self._kwargs)
