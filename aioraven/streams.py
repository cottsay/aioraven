# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import asyncio
from asyncio.events import AbstractEventLoop
from asyncio.events import get_event_loop
from asyncio.tasks import Task
from asyncio.transports import BaseTransport
from contextlib import AbstractAsyncContextManager
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
import xml.etree.ElementTree as Et

from aioraven.data import RAVEnData
from aioraven.device import RAVEnBaseDevice
from aioraven.device import RAVEnConnectionError
from aioraven.device import RAVEnNotOpenError
from aioraven.protocols import RAVEnReaderProtocol
from aioraven.reader import RAVEnReader


class RAVEnWriter:
    """Write commands to a RAVEn device."""

    # TODO(cottsay): Deal with BaseTransport vs IO types
    _transport: Any

    def __init__(
        self,
        transport: BaseTransport,
        protocol: RAVEnReaderProtocol
    ) -> None:
        """
        Construct a RAVEnWriter.

        :param transport: The transport instance to wrap.
        :param protocol: The reader protocol for the connection.
        """
        self._transport = transport
        self._protocol = protocol

    def __repr__(self) -> str:
        info = [self.__class__.__name__]
        info.append('transport=%r' % self._transport)
        return '<%s>' % ' '.join(info)

    def write_cmd(
        self,
        cmd_name: str,
        args: Optional[Dict[str, str]] = None,
    ) -> None:
        element_cmd = Et.Element('Command')
        element_name = Et.SubElement(element_cmd, 'Name')
        element_name.text = cmd_name
        for k, v in (args or {}).items():
            element_arg = Et.SubElement(element_cmd, k)
            element_arg.text = v
        tree = Et.ElementTree(element_cmd)
        tree.write(self._transport, encoding='ASCII', xml_declaration=False)

    def close(self) -> None:
        self._transport.close()

    async def wait_closed(self) -> None:
        await self._protocol._get_close_waiter(self)


async def open_connection(
    host: str,
    port: int,
    *,
    loop: Optional[AbstractEventLoop] = None,
) -> Tuple[RAVEnReader, RAVEnWriter]:
    """
    Establish a network connection to a RAVEn device.

    Additional optional keyword arguments are passed to
    `AbstractEventLoop.create_connection()`.

    :param host: The hostname or IP address to connect to.
    :param port: The TCP port number to connect to.
    :param loop: The event loop instance to use.
    """
    if loop is None:
        loop = get_event_loop()
    reader = RAVEnReader(loop=loop)
    protocol = RAVEnReaderProtocol(reader, loop=loop)
    try:
        transport, _ = await loop.create_connection(
            lambda: protocol, host=host, port=port)
    except OSError as ex:
        raise RAVEnConnectionError(f'{ex}') from ex
    writer = RAVEnWriter(transport, protocol)
    return reader, writer


class RAVEnStreamDevice(
    RAVEnBaseDevice,
    AbstractAsyncContextManager['RAVEnStreamDevice']
):
    """Read and write coordination for stream-based RAVEn devices."""

    _reader: Optional[RAVEnReader] = None
    _writer: Optional[RAVEnWriter] = None

    async def open(self) -> None:
        raise NotImplementedError()

    async def close(self) -> None:
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except IOError:
                pass
            self._reader = None
            self._writer = None

    async def synchronize(self, *, retries: int = 2) -> None:
        await asyncio.sleep(0.05)
        for _try in range(retries, -1, -1):
            try:
                # Try a few times to communicate with the device,
                # allowing any data already in the buffer to flush.
                await self.get_meter_list()
            except RAVEnConnectionError:
                if not _try:
                    raise
            else:
                break

    async def _query(
        self,
        cmd_name: str,
        res_name: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
    ) -> Optional[RAVEnData]:
        if not self._reader or not self._writer:
            raise RAVEnNotOpenError()
        waiter: Optional[Task[Optional[RAVEnData]]] = None
        if res_name:
            waiter = asyncio.create_task(self._reader.read_tag(res_name))
            await asyncio.sleep(0)
        try:
            self._writer.write_cmd(cmd_name, args)
            return await waiter if waiter is not None else None
        except (Et.ParseError, IOError) as ex:
            raise RAVEnConnectionError(f'{ex}') from ex

    async def __aenter__(self) -> 'RAVEnStreamDevice':
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any
    ) -> None:
        await self.close()


class RAVEnNetworkDevice(RAVEnStreamDevice):
    """A network-connected RAVEn device."""

    def __init__(
        self,
        host: str,
        port: int,
        *,
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        """
        Construct a RAVEnNetworkDevice.

        Additional optional keyword arguments are passed to
        `AbstractEventLoop.create_connection()`.

        :param host: The hostname or IP address to connect to.
        :param port: The TCP port number to connect to.
        :param loop: The event loop instance to use.
        """
        self._host = host
        self._port = port
        self._loop = loop

    def __repr__(self) -> str:
        info = [self.__class__.__name__]
        info.append('host=%s' % self._host)
        info.append('port=%s' % self._port)
        return '<%s>' % ' '.join(info)

    async def open(self) -> None:
        """Open the connection to the RAVEn device."""
        if self._reader or self._writer:
            return
        self._reader, self._writer = await open_connection(
            host=self._host, port=self._port, loop=self._loop)
