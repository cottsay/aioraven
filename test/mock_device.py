# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def mock_device(responses=None):
    """
    Create a mock device at a TCP endpoint.

    This function creates a context-managed TCP endpoint which echoes verbatim
    responses given verbatim requests.

    :param dict responses: A mapping of request strings to responses.

    :returns: A tuple including the host and port of the TCP endpoint.
    """
    if responses is None:
        responses = {}

    async def client_connected_impl(reader, writer):
        buffer = b''
        try:
            while True:
                value = await reader.read(1)
                if not value:
                    break
                buffer += value
                buffer = buffer.lstrip()
                for k, v in responses.items():
                    if buffer.startswith(k):
                        if v:
                            writer.write(v)
                        buffer = buffer[len(k):]
                        del responses[k]
                        break
        finally:
            writer.write_eof()
            writer.close()

    connections = []

    def client_connected(reader, writer):
        task = asyncio.create_task(client_connected_impl(reader, writer))
        connections.append(task)
        return asyncio.wait_for(task, None)

    server = await asyncio.start_server(client_connected, host='127.0.0.1')
    async with server:
        yield server.sockets[0].getsockname()
    await server.wait_closed()
    if not connections:
        return

    _, connections = await asyncio.wait(connections, timeout=0.1)
    for task in connections:
        task.cancel()
    if connections:
        await asyncio.wait(connections)
