# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import xml.etree.ElementTree as ET

from aioraven.data import MeterList
from aioraven.serial import RAVEnSerialDevice
import pytest
from serial import SerialException

from .mock_device import mock_device


@pytest.mark.asyncio
async def test_serial_data():
    responses = {
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'</MeterList>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnSerialDevice(f'socket://{host}:{port}') as dut:
            actual = await dut.get_meter_list()

    assert actual == MeterList(
        device_mac_id=b'0123456789ABCDEF',
        meter_mac_ids=[])


@pytest.mark.asyncio
async def test_serial_disconnect():
    async with mock_device() as (host, port):
        dut = RAVEnSerialDevice(f'socket://{host}:{port}')
        await dut.open()
    async with dut:
        with pytest.raises(SerialException):
            await dut.get_device_info()
        with pytest.raises(SerialException):
            await dut.get_device_info()


@pytest.mark.asyncio
async def test_serial_incomplete():
    responses = {
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'</MeterList>'
            b'<DeviceInfo>'
    }

    async with mock_device(responses) as (host, port):
        dut = RAVEnSerialDevice(f'socket://{host}:{port}')
        await dut.open()
        assert await dut.get_meter_list()
    async with dut:
        # Serial ports don't get EOF, so we won't see the incomplete
        # XML element here.
        assert not await dut.get_meter_list()


@pytest.mark.asyncio
async def test_serial_not_open():
    async with mock_device() as (host, port):
        dut = RAVEnSerialDevice(f'socket://{host}:{port}')
        with pytest.raises(RuntimeError):
            await dut.get_device_info()


@pytest.mark.asyncio
async def test_serial_parse_error():
    responses = {
        b'<Command><Name>get_device_info</Name></Command>':
            b'</DeviceInfo>',
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'</MeterList>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnSerialDevice(f'socket://{host}:{port}') as dut:
            with pytest.raises(ET.ParseError):
                await dut.get_device_info()
            actual = await dut.get_meter_list()

    assert actual == MeterList(
        device_mac_id=b'0123456789ABCDEF',
        meter_mac_ids=[])


@pytest.mark.asyncio
async def test_serial_repr():
    async with mock_device({}) as (host, port):
        async with RAVEnSerialDevice(f'socket://{host}:{port}') as dut:
            assert 'RAVEnSerialDevice' in str(dut)
