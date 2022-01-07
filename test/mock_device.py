# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def mock_device(responses):
    """
    Create a mock device at a TCP endpoint.

    This function creates a context-managed TCP endpoint which echoes verbatim
    responses given verbatim requests.

    :param dict responses: A mapping of request strings to responses.

    :returns: A tuple including the host and port of the TCP endpoint.
    """
    async def client_connected(reader, writer):
        buffer = b''
        while True:
            buffer += await reader.read(1)
            buffer = buffer.lstrip()
            for k, v in responses.items():
                if buffer.startswith(k):
                    writer.write(v)
                    buffer = buffer[len(k):]

    server = await asyncio.start_server(client_connected, host='127.0.0.1')
    async with server:
        yield server.sockets[0].getsockname()
    await asyncio.sleep(0)
