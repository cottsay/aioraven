# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from xml.etree import ElementTree as ET

from aioraven.data import MeterList
from aioraven.streams import RAVEnNetworkDevice
import pytest

from .mock_device import mock_device


@pytest.mark.asyncio
async def test_tcp_data():
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
        device_mac_id=b'0123456789ABCDEF',
        meter_mac_ids=[])


@pytest.mark.asyncio
async def test_tcp_disconnect():
    async with mock_device() as (host, port):
        dut = RAVEnNetworkDevice(host, port)
        await dut.open()
    async with dut:
        assert not await dut.get_meter_list()
        assert not await dut.get_meter_list()


@pytest.mark.asyncio
async def test_tcp_incomplete():
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
    async with dut:
        with pytest.raises(ET.ParseError):
            await dut.get_meter_list()
        assert not await dut.get_meter_list()


@pytest.mark.asyncio
async def test_tcp_parse_error():
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
            with pytest.raises(ET.ParseError):
                await dut.get_device_info()
            actual = await dut.get_meter_list()

    assert actual == MeterList(
        device_mac_id=b'0123456789ABCDEF',
        meter_mac_ids=[])
