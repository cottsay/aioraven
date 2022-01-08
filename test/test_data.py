# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from datetime import date
from datetime import datetime
from datetime import timezone

from aioraven.data import DeviceInfo
from aioraven.data import MeterList
from aioraven.data import PriceCluster
from aioraven.streams import RAVEnNetworkDevice
from iso4217 import Currency
import pytest

from .mock_device import mock_device


@pytest.mark.asyncio
async def test_get_device_info():
    responses = {
        b'<Command><Name>get_device_info</Name></Command>':
            b'<DeviceInfo>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <InstallCode>0xabcdef0123456789</InstallCode>'
            b'    <LinkKey>0xabcdef0123456789abcdef0123456789</LinkKey>'
            b'    <FWVersion>1.21g</FWVersion>'
            b'    <HWVersion>5.55 rev 2</HWVersion>'
            b'    <ImageType>Mocked</ImageType>'
            b'    <Manufacturer>aioraven</Manufacturer>'
            b'    <ModelId>Python</ModelId>'
            b'    <DateCode>2022010100000042</DateCode>'
            b'</DeviceInfo>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_device_info()

    assert actual == DeviceInfo(
        device_mac_id=b'0123456789ABCDEF',
        install_code=b'ABCDEF0123456789',
        link_key=b'ABCDEF0123456789ABCDEF0123456789',
        fw_version='1.21g',
        hw_version='5.55 rev 2',
        image_type='Mocked',
        manufacturer='aioraven',
        model_id='Python',
        date_code=(date(2022, 1, 1), 42))


@pytest.mark.asyncio
async def test_get_current_price():
    responses = {
        b'<Command><Name>get_current_price</Name></Command>':
            b'<PriceCluster>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <TimeStamp>0x296B2D39</TimeStamp>'
            b'    <Price>0x18</Price>'
            b'    <Currency>0x348</Currency>'
            b'    <TrailingDigits>0x02</TrailingDigits>'
            b'    <Tier>0x08</Tier>'
            b'    <TierLabel>Set by User</TierLabel>'
            b'    <RateLabel>Set by User</RateLabel>'
            b'</PriceCluster>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_current_price()

    assert actual == PriceCluster(
        device_mac_id=b'0123456789ABCDEF',
        meter_mac_id=b'FEDCBA9876543210',
        time_stamp=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        price=0.24,
        currency=Currency.usd,
        tier=8,
        tier_label='Set by User',
        rate_label='Set by User')


@pytest.mark.asyncio
async def test_get_meter_list_zero():
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
async def test_get_meter_list_one():
    responses = {
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'</MeterList>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_meter_list()

    assert actual == MeterList(
        device_mac_id=b'0123456789ABCDEF',
        meter_mac_ids=[b'FEDCBA9876543210'])


@pytest.mark.asyncio
async def test_get_meter_list_two():
    responses = {
        b'<Command><Name>get_meter_list</Name></Command>':
            b'<MeterList>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <MeterMacId>0xfedcba0123456789</MeterMacId>'
            b'</MeterList>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_meter_list()

    assert actual == MeterList(
        device_mac_id=b'0123456789ABCDEF',
        meter_mac_ids=[b'FEDCBA9876543210', b'FEDCBA0123456789'])
