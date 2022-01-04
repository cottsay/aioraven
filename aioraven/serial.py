# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from asyncio.events import get_event_loop

from aioraven.protocols import RAVEnReaderProtocol
from aioraven.streams import RAVEnReader
from aioraven.streams import RAVEnWriter
import serial
from serial_asyncio import connection_for_serial


async def open_serial_connection(*, loop=None, **kwargs):
    if loop is None:
        loop = get_event_loop()
    reader = RAVEnReader(loop=loop)
    protocol = RAVEnReaderProtocol(reader, loop=loop)
    serial_instance = serial.serial_for_url(**kwargs)
    transport, _ = await connection_for_serial(
        loop, lambda: protocol, serial_instance)
    writer = RAVEnWriter(transport)
    return reader, writer
