# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from asyncio.events import AbstractEventLoop
from asyncio.events import get_event_loop
from typing import Optional
from typing import Tuple

from aioraven.device import RAVEnConnectionError
from aioraven.protocols import RAVEnReaderProtocol
from aioraven.reader import RAVEnReader
from aioraven.streams import RAVEnStreamDevice
from aioraven.streams import RAVEnWriter
from serial import SerialException
from serial_asyncio import create_serial_connection


async def open_serial_connection(
    url: str,
    *args: int,
    loop: Optional[AbstractEventLoop] = None,
    **kwargs: int,
) -> Tuple[RAVEnReader, RAVEnWriter]:
    """
    Establish a serial connection to a RAVEn device.

    Positional and keyword arguments are passed to
    `serial_asyncio.create_serial_connection()`.

    :param loop: The event loop instance to use.
    """
    if loop is None:
        loop = get_event_loop()
    reader = RAVEnReader(loop=loop)
    protocol = RAVEnReaderProtocol(reader, loop=loop)
    kwargs.setdefault('baudrate', 115200)
    try:
        transport, _ = await create_serial_connection(
            loop, lambda: protocol, url, *args, **kwargs)
    except SerialException as ex:
        raise RAVEnConnectionError(f'{ex}') from ex
    writer = RAVEnWriter(transport, protocol)
    return reader, writer


class RAVEnSerialDevice(RAVEnStreamDevice):
    """A serial-connected RAVEn device."""

    def __init__(
        self,
        url: str,
        *args: int,
        loop: Optional[AbstractEventLoop] = None,
        **kwargs: int
    ) -> None:
        """
        Construct a RAVEnSerialDevice.

        Additional positional and keyword arguments are passed to
        `serial_asyncio.create_serial_connection()`.

        :param url: The pyserial URL of the device to connect to.
        :param loop: The event loop instance to use.
        """
        self._url = url
        self._args = args
        self._loop = loop
        self._kwargs = kwargs

    def __repr__(self) -> str:
        info = [self.__class__.__name__]
        info.append('url=%s' % self._url)
        return '<%s>' % ' '.join(info)

    async def open(self) -> None:
        """Open the connection to the RAVEn device."""
        if self._reader or self._writer:
            return
        self._reader, self._writer = await open_serial_connection(
            self._url, *self._args, loop=self._loop, **self._kwargs)
