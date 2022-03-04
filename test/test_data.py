# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from aioraven.data import ConnectionState
from aioraven.data import CurrentPeriodUsage
from aioraven.data import CurrentSummationDelivered
from aioraven.data import DataStatus
from aioraven.data import DeviceInfo
from aioraven.data import InstantaneousDemand
from aioraven.data import IntervalChannel
from aioraven.data import IntervalPeriod
from aioraven.data import LastPeriodUsage
from aioraven.data import MessageCluster
from aioraven.data import MessageQueue
from aioraven.data import MeterInfo
from aioraven.data import MeterList
from aioraven.data import MeterType
from aioraven.data import NetworkInfo
from aioraven.data import PriceCluster
from aioraven.data import ProfileData
from aioraven.data import ScheduledEvent
from aioraven.data import ScheduleInfo
from aioraven.data import TimeCluster
from aioraven.streams import RAVEnNetworkDevice
from iso4217 import Currency
import pytest

from .mock_device import mock_device


@pytest.mark.asyncio
@pytest.mark.parametrize('meter', (bytes.fromhex('FEDCBA9876543210'), None))
async def test_get_current_period_usage(meter):
    responses = {
        b'<Command><Name>get_current_period_usage</Name></Command>':
            b'<CurrentPeriodUsage>'
            b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
            b'    <MeterMacId>0xFEDCBA9876543210</MeterMacId>'
            b'    <TimeStamp>0x296B2D39</TimeStamp>'
            b'    <CurrentUsage>0x00000010</CurrentUsage>'
            b'    <Multiplier>0x00000004</Multiplier>'
            b'    <Divisor>0x00000002</Divisor>'
            b'    <DigitsRight>0x02</DigitsRight>'
            b'    <DigitsLeft>0x04</DigitsLeft>'
            b'    <SuppressLeadingZero>N</SuppressLeadingZero>'
            b'    <StartDate>0x296B2D38</StartDate>'
            b'</CurrentPeriodUsage>',
    }
    responses[
        b'<Command>'
        b'<Name>get_current_period_usage</Name>'
        b'<MeterMacId>0xFEDCBA9876543210</MeterMacId>'
        b'</Command>'
    ] = responses[b'<Command><Name>get_current_period_usage</Name></Command>']

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_current_period_usage(
                meter=meter,
            )

    assert actual == CurrentPeriodUsage(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        time_stamp=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        current_usage='0032.00',
        start_date=datetime(
            2022, 1, 7, 5, 56, 24, tzinfo=timezone.utc))


@pytest.mark.asyncio
@pytest.mark.parametrize('meter', (bytes.fromhex('FEDCBA9876543210'), None))
async def test_get_current_summation_delivered(meter):
    responses = {
        b'<Command><Name>get_current_summation_delivered</Name></Command>':
            b'<CurrentSummationDelivered>'
            b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
            b'    <MeterMacId>0xFEDCBA9876543210</MeterMacId>'
            b'    <TimeStamp>0x296B2D39</TimeStamp>'
            b'    <SummationDelivered>0x00000010</SummationDelivered>'
            b'    <SummationReceived>0x00000008</SummationReceived>'
            b'    <Multiplier>0x00000004</Multiplier>'
            b'    <Divisor>0x00000002</Divisor>'
            b'    <DigitsRight>0x02</DigitsRight>'
            b'    <DigitsLeft>0x04</DigitsLeft>'
            b'    <SuppressLeadingZero>N</SuppressLeadingZero>'
            b'</CurrentSummationDelivered>',
    }
    responses[
        b'<Command>'
        b'<Name>get_current_summation_delivered</Name>'
        b'<MeterMacId>0xFEDCBA9876543210</MeterMacId>'
        b'</Command>'
    ] = responses[
        b'<Command><Name>get_current_summation_delivered</Name></Command>']

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_current_summation_delivered(meter=meter)

    assert actual == CurrentSummationDelivered(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        time_stamp=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        summation_delivered='0032.00',
        summation_received='0016.00')


@pytest.mark.asyncio
@pytest.mark.parametrize('meter', (bytes.fromhex('FEDCBA9876543210'), None))
async def test_get_current_price(meter):
    responses = {
        b'<Command><Name>get_current_price</Name></Command>':
            b'<PriceCluster>'
            b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
            b'    <MeterMacId>0xFEDCBA9876543210</MeterMacId>'
            b'    <TimeStamp>0x296B2D39</TimeStamp>'
            b'    <Price>0x18</Price>'
            b'    <Currency>0x348</Currency>'
            b'    <TrailingDigits>0x02</TrailingDigits>'
            b'    <Tier>0x08</Tier>'
            b'    <TierLabel>Set by User</TierLabel>'
            b'    <RateLabel>Set by User</RateLabel>'
            b'</PriceCluster>',
    }
    responses[
        b'<Command>'
        b'<Name>get_current_price</Name>'
        b'<MeterMacId>0xFEDCBA9876543210</MeterMacId>'
        b'</Command>'
    ] = responses[b'<Command><Name>get_current_price</Name></Command>']

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_current_price(meter=meter)

    assert actual == PriceCluster(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        time_stamp=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        price=0.24,
        currency=Currency.usd,
        tier=8,
        tier_label='Set by User',
        rate_label='Set by User')


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
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        install_code=bytes.fromhex('ABCDEF0123456789'),
        link_key=bytes.fromhex('ABCDEF0123456789ABCDEF0123456789'),
        fw_version='1.21g',
        hw_version='5.55 rev 2',
        image_type='Mocked',
        manufacturer='aioraven',
        model_id='Python',
        date_code=(date(2022, 1, 1), 42))


@pytest.mark.asyncio
async def test_get_instantaneous_demand():
    responses = {
        b'<Command><Name>get_instantaneous_demand</Name></Command>':
            b'<InstantaneousDemand>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <TimeStamp>0x296B2D39</TimeStamp>'
            b'    <Demand>0x00000010</Demand>'
            b'    <Multiplier>0x00000004</Multiplier>'
            b'    <Divisor>0x00000002</Divisor>'
            b'    <DigitsRight>0x02</DigitsRight>'
            b'    <DigitsLeft>0x04</DigitsLeft>'
            b'    <SuppressLeadingZero>N</SuppressLeadingZero>'
            b'</InstantaneousDemand>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_instantaneous_demand()

    assert actual == InstantaneousDemand(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        time_stamp=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        demand='0032.00')


@pytest.mark.asyncio
async def test_get_last_period_usage():
    responses = {
        b'<Command><Name>get_last_period_usage</Name></Command>':
            b'<LastPeriodUsage>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <LastUsage>0x00000010</LastUsage>'
            b'    <Multiplier>0x00000004</Multiplier>'
            b'    <Divisor>0x00000002</Divisor>'
            b'    <DigitsRight>0x02</DigitsRight>'
            b'    <DigitsLeft>0x04</DigitsLeft>'
            b'    <SuppressLeadingZero>N</SuppressLeadingZero>'
            b'    <StartDate>0x296B2D39</StartDate>'
            b'    <EndDate>0x29940BB9</EndDate>'
            b'</LastPeriodUsage>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_last_period_usage()

    assert actual == LastPeriodUsage(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        last_usage='0032.00',
        start_date=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        end_date=datetime(
            2022, 2, 7, 5, 56, 25, tzinfo=timezone.utc))


@pytest.mark.asyncio
async def test_get_message():
    responses = {
        b'<Command><Name>get_message</Name></Command>':
            b'<MessageCluster>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <TimeStamp>0x296B2D39</TimeStamp>'
            b'    <Id>0x02468ACE</Id>'
            b'    <Text>Hello, World!</Text>'
            b'    <ConfirmationRequired>N</ConfirmationRequired>'
            b'    <Confirmed>Y</Confirmed>'
            b'    <Queue>Active</Queue>'
            b'</MessageCluster>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_message()

    assert actual == MessageCluster(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        time_stamp=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        message_id=bytes.fromhex('02468ACE'),
        text='Hello, World!',
        confirmation_required=False,
        confirmed=True,
        queue=MessageQueue.ACTIVE)


@pytest.mark.asyncio
async def test_get_meter_info():
    responses = {
        b'<Command><Name>get_meter_info</Name></Command>':
            b'<MeterInfo>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <MeterType>electric</MeterType>'
            b'    <NickName>House</NickName>'
            b'    <Account>8675309</Account>'
            b'    <Auth>p@ssw0rd</Auth>'
            b'    <Host>Example, Inc.</Host>'
            b'    <Enabled>Y</Enabled>'
            b'</MeterInfo>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_meter_info()

    assert actual == MeterInfo(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        meter_type=MeterType.ELECTRIC,
        nick_name='House',
        account='8675309',
        auth='p@ssw0rd',
        host='Example, Inc.',
        enabled=True)


@pytest.mark.asyncio
async def test_get_network_info():
    responses = {
        b'<Command><Name>get_network_info</Name></Command>':
            b'<NetworkInfo>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <CoordMacId>0xfedcba9876543210</CoordMacId>'
            b'    <Status>Connected</Status>'
            b'    <Description>Network is operational</Description>'
            b'    <StatusCode>0x42</StatusCode>'
            b'    <ExtPanId>0x9876543210abcdef</ExtPanId>'
            b'    <Channel>24</Channel>'
            b'    <ShortAddr>0x5678</ShortAddr>'
            b'    <LinkStrength>0x24</LinkStrength>'
            b'</NetworkInfo>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_network_info()

    assert actual == NetworkInfo(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        coord_mac_id=bytes.fromhex('FEDCBA9876543210'),
        status=ConnectionState.CONNECTED,
        description='Network is operational',
        status_code=bytes.fromhex('42'),
        ext_pan_id=bytes.fromhex('9876543210ABCDEF'),
        channel=24,
        short_addr=bytes.fromhex('5678'),
        link_strength=36)


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
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
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
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_ids=[bytes.fromhex('FEDCBA9876543210')])


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
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_ids=[
            bytes.fromhex('FEDCBA9876543210'),
            bytes.fromhex('FEDCBA0123456789')])


@pytest.mark.asyncio
async def test_get_profile_data():
    responses = {
        b'<Command>'
        b'<Name>get_profile_data</Name>'
        b'<NumberOfPeriods>0x02</NumberOfPeriods>'
        b'<EndTime>0x296B2D39</EndTime>'
        b'<IntervalChannel>Delivered</IntervalChannel>'
        b'</Command>':
            b'<ProfileData>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <EndTime>0x296B2D39</EndTime>'
            b'    <Status>0x00</Status>'
            b'    <ProfileIntervalPeriod>2</ProfileIntervalPeriod>'
            b'</ProfileData>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_profile_data(
                2, '0x296B2D39',
                IntervalChannel.DELIVERED)

    assert actual == ProfileData(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        end_time=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        status=DataStatus.SUCCESS,
        profile_interval_period=IntervalPeriod.THIRTY_MIN)


@pytest.mark.asyncio
async def test_get_schedule():
    responses = {
        b'<Command><Name>get_schedule</Name></Command>':
            b'<ScheduleInfo>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <Event>summation</Event>'
            b'    <Frequency>0x13579bdf</Frequency>'
            b'    <Enabled>Y</Enabled>'
            b'</ScheduleInfo>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_schedule()

    assert actual == ScheduleInfo(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        event=ScheduledEvent.SUMMATION,
        frequency=timedelta(seconds=0x13579bdf),
        enabled=True)


@pytest.mark.asyncio
async def test_get_time():
    responses = {
        b'<Command><Name>get_time</Name></Command>':
            b'<TimeCluster>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <MeterMacId>0xfedcba9876543210</MeterMacId>'
            b'    <UTCTime>0x296B2D39</UTCTime>'
            b'    <LocalTime>0x296B2D39</LocalTime>'
            b'</TimeCluster>',
    }

    async with mock_device(responses) as (host, port):
        async with RAVEnNetworkDevice(host, port) as dut:
            actual = await dut.get_time()

    assert actual == TimeCluster(
        device_mac_id=bytes.fromhex('0123456789ABCDEF'),
        meter_mac_id=bytes.fromhex('FEDCBA9876543210'),
        utc_time=datetime(
            2022, 1, 7, 5, 56, 25, tzinfo=timezone.utc),
        local_time=datetime(2022, 1, 6, 21, 56, 25))
