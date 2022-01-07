# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from datetime import date

from aioraven.data import DeviceInfo
from aioraven.serial import RAVEnSerialDevice
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
        async with RAVEnSerialDevice() as dut:
            await dut.open(f'socket://{host}:{port}')
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
