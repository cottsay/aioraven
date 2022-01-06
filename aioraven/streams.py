# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import asyncio
from asyncio.events import get_event_loop
import xml.etree.ElementTree as ET

from aioraven.device import RAVEnBaseDevice
from aioraven.protocols import RAVEnReaderProtocol


async def open_connection(host=None, port=None, *, loop=None, **kwargs):
    if loop is None:
        loop = get_event_loop()
    reader = RAVEnReader(loop=loop)
    protocol = RAVEnReaderProtocol(reader, loop=loop)
    transport, _ = await loop.create_connection(
        lambda: protocol, host=host, port=port, **kwargs)
    writer = RAVEnWriter(transport)
    return reader, writer


class RAVEnReader:
    """Read stanzas from a RAVEn device."""

    def __init__(self, loop=None):
        if loop is None:
            self._loop = get_event_loop()
        else:
            self._loop = loop
        self._eof = False
        self._waiters = {}
        self._exception = None

    def __repr__(self):
        info = [self.__class__.__name__]
        if self._eof:
            info.append('eof')
        if self._exception:
            info.append('e=%r' % self._exception)
        num_waiters = len(w for t in self._waiters for w in t)
        if num_waiters:
            info.append('w=%d' % num_waiters)
        return '<%s>' % ' '.join(info)

    def exception(self):
        return self._exception

    def set_exception(self, exc):
        self._exception = exc
        for waiters in self._waiters.values():
            while waiters:
                waiters.pop(0).set_exception(exc)

    def set_transport(self, transport):
        self._transport = transport

    def feed_eof(self):
        self._eof = True
        for waiters in self._waiters.values():
            while waiters:
                waiters.pop(0).set_result(None)

    def feed_element(self, data):
        self._waiters.setdefault(data.tag, [])
        waiters = self._waiters.get(data.tag, [])
        if waiters:
            waiters.pop(0).set_result({e.tag: e.text for e in data})

    async def read_tag(self, tag):
        if self._eof:
            return None
        # if self._exception is not None:
        #     raise self._exception
        self._waiters.setdefault(tag, [])
        waiter = self._loop.create_future()
        self._waiters[tag].append(waiter)
        return await waiter


class RAVEnWriter:
    """Write commands to a RAVEn device."""

    def __init__(self, transport):
        self._transport = transport

    def __repr__(self):
        info = [self.__class__.__name__, 'transport=%r' % self._transport]
        return '<%s>' % ' '.join(info)

    def write_cmd(self, cmd_name, args=None):
        element_cmd = ET.Element('Command')
        element_name = ET.SubElement(element_cmd, 'Name')
        element_name.text = cmd_name
        for k, v in args or iter(()):
            element_arg = ET.SubElement(element_cmd, k)
            element_arg.text = v
        tree = ET.ElementTree(element_cmd)
        tree.write(self._transport, encoding='ASCII', xml_declaration=False)

    def close(self):
        return self._transport.close()


class RAVEnNetworkDevice(RAVEnBaseDevice):

    async def open(self, host=None, port=None, *, loop=None, **kwargs):
        self._reader, self._writer = await open_connection(
            host=host, port=port, loop=loop, **kwargs)

    async def close(self):
        if self._writer:
            self._writer.close()
            self._reader = None
            self._writer = None

    async def _query(self, cmd_name, res_name=None, args=None):
        if not self._reader or not self._writer:
            raise RuntimeError('TODO: Not connected')
        waiter = None
        if res_name:
            waiter = asyncio.create_task(self._reader.read_tag(res_name))
            await asyncio.sleep(0)
        self._writer.write_cmd(cmd_name, args)
        return await waiter if waiter else None
