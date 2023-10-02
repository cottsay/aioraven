# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from asyncio.events import AbstractEventLoop
from asyncio.events import get_event_loop
from asyncio.futures import Future
from typing import Dict
from typing import List
from typing import Optional
import xml.etree.ElementTree as Et

from aioraven.data import RAVEnData


class RAVEnReader:
    """Read stanzas from a RAVEn device."""

    _exception: Optional[Exception]
    _waiters: Dict[Optional[str], List[Future[Optional[RAVEnData]]]]

    def __init__(self, loop: Optional[AbstractEventLoop] = None) -> None:
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

    def __repr__(self) -> str:
        info = [self.__class__.__name__]
        if self._eof:
            info.append('eof')
        if self._exception:
            info.append('e=%r' % self._exception)
        num_waiters = sum(len(w) for w in self._waiters.values())
        if num_waiters:
            info.append('w=%d' % num_waiters)
        return '<%s>' % ' '.join(info)

    def exception(self) -> Optional[Exception]:
        return self._exception

    def set_exception(self, exc: Exception) -> None:
        # Only ParseError is recoverable
        if not isinstance(exc, Et.ParseError):
            self._exception = exc
        for waiters in self._waiters.values():
            while waiters:
                waiter = waiters.pop(0)
                if not waiter.cancelled():
                    waiter.set_exception(exc)

    def feed_eof(self) -> None:
        self._eof = True
        for waiters in self._waiters.values():
            while waiters:
                waiter = waiters.pop(0)
                if not waiter.cancelled():
                    waiter.set_result(None)

    def feed_element(self, data: Et.Element) -> None:
        self._waiters.setdefault(data.tag, [])
        waiters = self._waiters.get(data.tag, [])
        res: RAVEnData = {}
        for e in data:
            if e.tag in res:
                orig = res[e.tag]
                if not isinstance(orig, list):
                    res[e.tag] = [orig, e.text]
                else:
                    orig.append(e.text)
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

    async def read_tag(
        self,
        tag: Optional[str] = None,
    ) -> Optional[RAVEnData]:
        if self._eof:
            return None
        if self._exception is not None:
            raise self._exception
        self._waiters.setdefault(tag, [])
        waiter: Future[Optional[RAVEnData]] = self._loop.create_future()
        self._waiters[tag].append(waiter)
        return await waiter
