# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import asyncio

from aioraven.data import MeterList
from aioraven.device import RAVEnConnectionError
from aioraven.device import RAVEnNotOpenError
from aioraven.streams import open_connection
from aioraven.streams import RAVEnNetworkDevice
import pytest

from .mock_device import mock_device


@pytest.mark.asyncio
async def test_tcp_data():
    """Verify simple device query behavior."""
    responses = {
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'</MeterList>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_meter_list()

    assert actual == MeterList(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_ids=[])


@pytest.mark.asyncio
async def test_tcp_disconnect():
    """Verify behavior when a device is unexpectedly disconnected."""
    responses = {
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'</MeterList>',
    }

    async with mock_device(responses) as (host, port):
        dut = RAVEnNetworkDevice(host, port)
        await dut.open()
        assert await dut.get_meter_list()
    async with dut:
        assert not await dut.get_meter_list()
        assert not await dut.get_meter_list()


@pytest.mark.asyncio
async def test_tcp_incomplete():
    """Verify behavior when a partial fragment is received."""
    responses = {
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'</MeterList>'
            b'<DeviceInfo>'
    }

    async with mock_device(responses) as (host, port):
        dut = RAVEnNetworkDevice(host, port)
        await dut.open()
        assert await dut.get_meter_list()

        task = asyncio.create_task(dut.get_meter_list())
        await asyncio.wait((task,), timeout=0.05)
    async with dut:
        with pytest.raises(RAVEnConnectionError):
            await task
        assert not await dut.get_meter_list()


@pytest.mark.asyncio
async def test_tcp_not_open():
    """Verify behavior when reading from an unopened device."""
    async with mock_device() as (host, port):
        dut = RAVEnNetworkDevice(host, port)
        with pytest.raises(RAVEnNotOpenError):
            await dut.get_device_info()


@pytest.mark.asyncio
async def test_tcp_parse_error():
    """Verify behavior when invalid syntax is received."""
    responses = {
        b'<Command><Name>get_device_info</Name></Command>':
            b'</DeviceInfo>',
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'</MeterList>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            with pytest.raises(RAVEnConnectionError):
                await dut.get_device_info()
            actual = await dut.get_meter_list()

    assert actual == MeterList(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_ids=[])


@pytest.mark.asyncio
async def test_tcp_repr():
    """Verify representation of a network device."""
    async with mock_device() as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            assert 'RAVEnNetworkDevice' in str(dut)

        reader, writer = await open_connection(host, port)
        try:
            assert 'RAVEnReader' in str(reader)
            assert 'RAVEnWriter' in str(writer)
        finally:
            writer.close()
