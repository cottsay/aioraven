# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from asyncio.events import get_event_loop

from aioraven.protocols import RAVEnReaderProtocol
from aioraven.streams import RAVEnReader
from aioraven.streams import RAVEnWriter
from serial_asyncio import create_serial_connection \
    as create_pyserial_connection


async def create_serial_connection(*args, loop=None, **kwargs):
    if loop is None:
        loop = get_event_loop()
    reader = RAVEnReader(loop=loop)
    protocol = RAVEnReaderProtocol(reader, loop=loop)
    kwargs.setdefault('baudrate', 115200)
    transport, _ = await create_pyserial_connection(
        loop, lambda: protocol, *args, **kwargs)
    writer = RAVEnWriter(transport)
    return reader, writer
