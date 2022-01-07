# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from aioraven.streams import RAVEnNetworkDevice
import pytest

from .mock_device import mock_device


@pytest.mark.asyncio
async def test_device_info():
    responses = {
        b'<Command><Name>get_device_info</Name></Command>':
            b'<DeviceInfo>'
            b'    <DeviceMacId>0x0123456789abcdef</DeviceMacId>'
            b'    <InstallCode>0xabcdef0123456789</InstallCode>'
            b'    <LinkKey>0xabcdef0123456789abcdef0123456789</LinkKey>'
            b'    <FWVersion>1.21g</FWVersion>'
            b'    <HWVersion>5.55</HWVersion>'
            b'    <ImageType>Mocked</ImageType>'
            b'    <Manufacturer>aioraven</Manufacturer>'
            b'    <ModelId>Python</ModelId>'
            b'    <DateCode>2022010100000042</DateCode>'
            b'</DeviceInfo>'
    }

    async with mock_device(responses) as (host, port):
        dut = RAVEnNetworkDevice()
        await dut.open(host, port)
        info = await dut.get_device_info()
        await dut.close()

    import pprint
    pprint.pprint(info)
