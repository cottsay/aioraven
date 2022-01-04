# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import asyncio

from aioraven.protocols import RAVEnReaderProtocol
from aioraven.streams import RAVEnReader
import pytest


@pytest.mark.asyncio
async def test_single_element():
    reader = RAVEnReader()
    protocol = RAVEnReaderProtocol(reader)
    protocol.connection_made(None)

    waiter = asyncio.create_task(reader.read_tag('FooBar'))
    await asyncio.sleep(0)
    protocol.data_received(b'<FooBar/>')
    result = await waiter
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_multiple_elements():
    reader = RAVEnReader()
    protocol = RAVEnReaderProtocol(reader)
    protocol.connection_made(None)

    waiter = asyncio.create_task(reader.read_tag('FooBar'))
    await asyncio.sleep(0)
    protocol.data_received(b'<FooBar/>')
    result = await waiter
    assert isinstance(result, dict)

    waiter = asyncio.create_task(reader.read_tag('Baz'))
    await asyncio.sleep(0)
    protocol.data_received(b'<Baz/>')
    result = await waiter
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_other_element():
    reader = RAVEnReader()
    protocol = RAVEnReaderProtocol(reader)
    protocol.connection_made(None)

    waiter = asyncio.create_task(reader.read_tag('FooBar'))
    await asyncio.sleep(0)
    protocol.data_received(b'<Baz/>')
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(waiter, timeout=0.05)
