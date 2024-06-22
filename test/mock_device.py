# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import asyncio
from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import MutableMapping
from contextlib import asynccontextmanager
import os
import sys
from typing import BinaryIO
from typing import Optional
from typing import SupportsIndex
from typing import TypeVar
from typing import Union

import serial_asyncio_fast


_T = TypeVar('_T')


class _NoPopList(list[_T]):

    def pop(self, index: SupportsIndex = -1) -> _T:
        return self[index]


_ResponseMapping = MutableMapping[bytes, Optional[Union[list[bytes], bytes]]]

DEFAULT_RESPONSES: _ResponseMapping = {
    b'<Command>'
    b'<Name>get_current_price</Name>'
    b'<MeterMacId>0xFEDCBA9876543210</MeterMacId>'
    b'</Command>': _NoPopList((
        b'<PriceCluster>'
        b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
        b'    <MeterMacId>0xFEDCBA9876543210</MeterMacId>'
        b'    <TimeStamp>0x29bd58a7</TimeStamp>'
        b'    <Price>0xc7</Price>'
        b'    <Currency>0x348</Currency>'
        b'    <TrailingDigits>0x03</TrailingDigits>'
        b'    <Tier>0x08</Tier>'
        b'    <TierLabel>Set by User</TierLabel>'
        b'    <RateLabel>Set by User</RateLabel>'
        b'</PriceCluster>',
    )),
    b'<Command>'
    b'<Name>get_current_summation_delivered</Name>'
    b'<MeterMacId>0xFEDCBA9876543210</MeterMacId>'
    b'</Command>': _NoPopList((
        b'<CurrentSummationDelivered>'
        b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
        b'    <MeterMacId>0xFEDCBA9876543210</MeterMacId>'
        b'    <TimeStamp>0x29bd58a7</TimeStamp>'
        b'    <SummationDelivered>0x00000010</SummationDelivered>'
        b'    <SummationReceived>0x00000008</SummationReceived>'
        b'    <Multiplier>0x00000004</Multiplier>'
        b'    <Divisor>0x00000002</Divisor>'
        b'    <DigitsRight>0x02</DigitsRight>'
        b'    <DigitsLeft>0x04</DigitsLeft>'
        b'    <SuppressLeadingZero>N</SuppressLeadingZero>'
        b'</CurrentSummationDelivered>',
    )),
    b'<Command>'
    b'<Name>get_device_info</Name>'
    b'</Command>': _NoPopList((
        b'<DeviceInfo>'
        b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
        b'    <InstallCode>0xABCDEF0123456789</InstallCode>'
        b'    <LinkKey>0xABCDEF0123456789ABCDEF0123456789</LinkKey>'
        b'    <FWVersion>1.21g</FWVersion>'
        b'    <HWVersion>5.55 rev 2</HWVersion>'
        b'    <ImageType>Mocked</ImageType>'
        b'    <Manufacturer>aioraven</Manufacturer>'
        b'    <ModelId>mock device</ModelId>'
        b'    <DateCode>20220101a0000042</DateCode>'
        b'</DeviceInfo>',
    )),
    b'<Command>'
    b'<Name>get_instantaneous_demand</Name>'
    b'<MeterMacId>0xFEDCBA9876543210</MeterMacId>'
    b'</Command>': _NoPopList((
        b'<InstantaneousDemand>'
        b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
        b'    <MeterMacId>0xFEDCBA9876543210</MeterMacId>'
        b'    <TimeStamp>0x29bd58a7</TimeStamp>'
        b'    <Demand>0x00000010</Demand>'
        b'    <Multiplier>0x00000004</Multiplier>'
        b'    <Divisor>0x00000002</Divisor>'
        b'    <DigitsRight>0x02</DigitsRight>'
        b'    <DigitsLeft>0x04</DigitsLeft>'
        b'    <SuppressLeadingZero>Y</SuppressLeadingZero>'
        b'</InstantaneousDemand>',
    )),
    b'<Command>'
    b'<Name>get_meter_info</Name>'
    b'<MeterMacId>0xFEDCBA9876543210</MeterMacId>'
    b'</Command>': _NoPopList((
        b'<MeterInfo>'
        b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
        b'    <MeterMacId>0xFEDCBA9876543210</MeterMacId>'
        b'    <MeterType>electric</MeterType>'
        b'    <NickName>House</NickName>'
        b'    <Account>8675309</Account>'
        b'    <Auth>p@ssw0rd</Auth>'
        b'    <Host>Example, Inc.</Host>'
        b'    <Enabled>Y</Enabled>'
        b'</MeterInfo>',
    )),
    b'<Command><Name>get_meter_list</Name></Command>': _NoPopList((
        b'<MeterList>'
        b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
        b'    <MeterMacId>0xFEDCBA9876543210</MeterMacId>'
        b'</MeterList>',
    )),
    b'<Command><Name>get_network_info</Name></Command>': _NoPopList((
        b'<NetworkInfo>'
        b'    <DeviceMacId>0x0123456789ABCDEF</DeviceMacId>'
        b'    <CoordMacId>0xFEDCBA9876543210</CoordMacId>'
        b'    <Status>Connected</Status>'
        b'    <Description>Network is operational</Description>'
        b'    <StatusCode>0x42</StatusCode>'
        b'    <ExtPanId>0x9876543210ABCDEF</ExtPanId>'
        b'    <Channel>24</Channel>'
        b'    <ShortAddr>0x5678</ShortAddr>'
        b'    <LinkStrength>0x24</LinkStrength>'
        b'</NetworkInfo>',
    )),
}


async def _device_loop(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    responses: _ResponseMapping
) -> None:
    buffer = b''
    while True:
        try:
            try:
                value = await reader.read(1)
            except asyncio.CancelledError:
                break
            if not value:
                break
            buffer += value
            buffer = buffer.lstrip()
            for k, v in responses.items():
                if buffer.startswith(k):
                    if isinstance(v, list):
                        first = v.pop(0)
                        if first is not None:
                            writer.write(first)
                        if not v:
                            del responses[k]
                    else:
                        if v is not None:
                            writer.write(v)
                        del responses[k]
                    buffer = buffer[len(k):]
                    break
        except asyncio.CancelledError:
            if not writer.can_write_eof():
                break
            writer.write_eof()
            await writer.drain()
    writer.close()


@asynccontextmanager
async def mock_pty_device(
    responses: Optional[_ResponseMapping] = None,
    initial_buffer: Optional[bytes] = None
) -> AsyncIterator[str]:
    if responses is None:
        responses = DEFAULT_RESPONSES

    import pty

    server, client = pty.openpty()

    server_in = os.fdopen(server, 'rb', 0, closefd=False)
    server_out = os.fdopen(server, 'wb', 0, closefd=False)

    reader, writer, read_transport = await connect_pipes(server_in, server_out)

    if initial_buffer is not None:
        writer.write(initial_buffer)
    task = asyncio.create_task(_device_loop(reader, writer, responses))

    yield os.ttyname(client)

    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    read_transport.close()
    writer.close()

    server_in.close()
    server_out.close()
    os.close(server)
    os.close(client)


@asynccontextmanager
async def mock_device(
    responses: Optional[_ResponseMapping] = None,
    initial_buffer: Optional[bytes] = None
) -> AsyncIterator[None]:
    """
    Create a mock device at a TCP endpoint.

    This function creates a context-managed TCP endpoint which echoes verbatim
    responses given verbatim requests.

    :param dict responses: A mapping of request strings to responses.
    :param bytes initial_buffer: Content to initialize the response buffer.

    :returns: A tuple including the host and port of the TCP endpoint.
    """
    if responses is None:
        responses = DEFAULT_RESPONSES

    connections = []

    def client_connected(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> Awaitable[None]:
        if initial_buffer is not None:
            writer.write(initial_buffer)
        task = asyncio.create_task(_device_loop(reader, writer, responses))
        connections.append(task)
        return asyncio.wait_for(task, None)

    server = await asyncio.start_server(client_connected, host='127.0.0.1')
    try:
        yield server.sockets[0].getsockname()
    finally:
        server.close()
    if not connections:
        return

    _, pending = await asyncio.wait(connections, timeout=0.1)
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.wait(pending)


async def connect_pipes(
    in_pipe: BinaryIO,
    out_pipe: BinaryIO,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter, asyncio.ReadTransport]:
    if loop is None:
        loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)

    read_transport, _ = await loop.connect_read_pipe(
        lambda: protocol, in_pipe)
    write_transport, write_protocol = await loop.connect_write_pipe(
        asyncio.streams.FlowControlMixin, out_pipe)
    writer = asyncio.StreamWriter(
        write_transport, write_protocol, reader, loop)
    return reader, writer, read_transport


async def main(argv: list[str] = sys.argv) -> Optional[int]:
    if len(argv) == 1:
        reader, writer, read_transport = await connect_pipes(
            sys.stdin.buffer, sys.stdout.buffer)
    elif len(argv) == 2:
        read_transport = None
        reader, writer = await serial_asyncio_fast.open_serial_connection(
            url=argv[1])
    else:
        print(f'Usage: {argv[0]} [DEVICE_PATH]', file=sys.stderr)
        return 1
    await _device_loop(reader, writer, DEFAULT_RESPONSES)
    if read_transport is not None:
        read_transport.close()
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
