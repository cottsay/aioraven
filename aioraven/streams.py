# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import asyncio
from asyncio.events import get_event_loop
from contextlib import AbstractAsyncContextManager
import xml.etree.ElementTree as ET

from aioraven.device import RAVEnBaseDevice
from aioraven.protocols import RAVEnReaderProtocol


async def open_connection(host=None, port=None, *, loop=None, **kwargs):
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
    protocol = RAVEnReaderProtocol(reader)
    transport, _ = await loop.create_connection(
        lambda: protocol, host=host, port=port, **kwargs)
    writer = RAVEnWriter(transport)
    return reader, writer


class RAVEnReader:
    """Read stanzas from a RAVEn device."""

    def __init__(self, loop=None):
        """
        Construct a RAVEnReader.

        :param loop: The event loop instance to use.
        """
        if loop is None:
            self._loop = get_event_loop()
        else:
            self._loop = loop
        self._eof = False
        self._waiters = {None: []}
        self._exception = None

    def __repr__(self):
        info = [self.__class__.__name__]
        if self._eof:
            info.append('eof')
        if self._exception:
            info.append('e=%r' % self._exception)
        num_waiters = sum(len(w) for w in self._waiters.values())
        if num_waiters:
            info.append('w=%d' % num_waiters)
        return '<%s>' % ' '.join(info)

    def exception(self):
        return self._exception

    def set_exception(self, exc):
        # Only ParseError is recoverable
        if not isinstance(exc, ET.ParseError):
            self._exception = exc
        for waiters in self._waiters.values():
            while waiters:
                waiter = waiters.pop(0)
                if not waiter.cancelled():
                    waiter.set_exception(exc)

    def feed_eof(self):
        self._eof = True
        for waiters in self._waiters.values():
            while waiters:
                waiter = waiters.pop(0)
                if not waiter.cancelled():
                    waiter.set_result(None)

    def feed_element(self, data):
        self._waiters.setdefault(data.tag, [])
        waiters = self._waiters.get(data.tag, [])
        res = {}
        for e in data:
            if e.tag in res:
                if not isinstance(res[e.tag], list):
                    res[e.tag] = [res[e.tag]]
                res[e.tag].append(e.text)
            else:
                res[e.tag] = e.text
        while waiters:
            waiter = waiters.pop(0)
            if not waiter.cancelled():
                waiter.set_result(res)
                break
        else:
            waiters = self._waiters[None]
            if waiters:
                waiters.pop(0).set_result(res)

    async def read_tag(self, tag=None):
        if self._eof:
            return None
        if self._exception is not None:
            raise self._exception
        self._waiters.setdefault(tag, [])
        waiter = self._loop.create_future()
        self._waiters[tag].append(waiter)
        return await waiter


class RAVEnWriter:
    """Write commands to a RAVEn device."""

    def __init__(self, transport):
        """
        Construct a RAVEnWriter.

        :param transport: The transport instace to wrap.
        """
        self._transport = transport

    def __repr__(self):
        info = [self.__class__.__name__]
        info.append('transport=%r' % self._transport)
        return '<%s>' % ' '.join(info)

    def write_cmd(self, cmd_name, args=None):
        element_cmd = ET.Element('Command')
        element_name = ET.SubElement(element_cmd, 'Name')
        element_name.text = cmd_name
        for k, v in (args or {}).items():
            element_arg = ET.SubElement(element_cmd, k)
            element_arg.text = v
        tree = ET.ElementTree(element_cmd)
        tree.write(self._transport, encoding='ASCII', xml_declaration=False)

    def close(self):
        return self._transport.close()


class RAVEnStreamDevice(RAVEnBaseDevice, AbstractAsyncContextManager):
    """Read and write coordination for stream-based RAVEn devices."""

    _reader = None
    _writer = None

    async def open(self):
        raise NotImplementedError()

    async def close(self):
        if self._writer:
            self._writer.close()
            self._reader = None
            self._writer = None

    async def _query(self, cmd_name, res_name=None, args=None):
        if not self._reader or not self._writer:
            raise RuntimeError('Device is not open')
        waiter = None
        if res_name:
            waiter = asyncio.create_task(self._reader.read_tag(res_name))
            await asyncio.sleep(0)
        self._writer.write_cmd(cmd_name, args)
        return await waiter if waiter else None

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


class RAVEnNetworkDevice(RAVEnStreamDevice):
    """A network-connected RAVEn device."""

    def __init__(self, host=None, port=None, *, loop=None, **kwargs):
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
        self._kwargs = kwargs

    def __repr__(self):
        info = [self.__class__.__name__]
        info.append('host=%s' % self._host)
        info.append('port=%s' % self._port)
        return '<%s>' % ' '.join(info)

    async def open(self):
        """Open the connection to the RAVEn device."""
        if self._reader or self._writer:
            return
        self._reader, self._writer = await open_connection(
            host=self._host, port=self._port, loop=self._loop, **self._kwargs)
