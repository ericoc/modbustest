#!/usr/bin/env python3
import asyncio
import logging
from argparse import ArgumentParser
from pymodbus.client import AsyncModbusTcpClient


DEFAULT_HOST = "adam.home.ericoc.com"
DEFAULT_PORT = 502
DEFAULT_COILS = range(16, 22)
DEFAULT_LOG_LEVEL = logging.INFO


async def main(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    coils: (list, int) = DEFAULT_COILS,
    toggle: bool = False,
):
    """ADAM unit interaction."""

    # Connect to the ADAM unit.
    client = AsyncModbusTcpClient(host=host, port=port)
    await client.connect()

    # Place single coil number in a list.
    if isinstance(coils, int):
        coils = [coils]

    # Iterate each coil in the list.
    for coil in coils:

        # Handle requests to toggle coil(s).
        if toggle:

            # Get existing boolean coil value, to determine the new value.
            original = await client.read_coils(address=coil, count=1)
            value = False
            if original.bits[0] is value:
                value = True

            # Set the new boolean coil value.
            await client.write_coil(address=coil, value=value)

        # Re-check the final value of the coil.
        recheck = await client.read_coils(address=coil, count=1)
        logging.info(f"Coil #{coil}: {recheck.bits[0]}")

    # Disconnect from ADAM unit.
    client.close()


# Main entry point.
if __name__ == "__main__":

    # Set up argument parser.
    parser = ArgumentParser(description="ADAM unit testing")
    connect = parser.add_argument_group(
        title="ADAM unit",
        description="Connection details for ADAM unit, via Modbus TCP"
    )
    connect.add_argument(
        "-H", "--host", "--hostname",
        dest="host",
        default=DEFAULT_HOST,
        help=f'ADAM Modbus TCP host or IP address (default: "{DEFAULT_HOST}")'
    )
    connect.add_argument(
        "-P", "--port",
        dest="port",
        default=DEFAULT_PORT,
        help=f"ADAM Modbus TCP port number (default: {DEFAULT_PORT})"
    )
    connect.add_argument(
        "-C", "--coil",
        dest="coil", type=int,
        default=DEFAULT_COILS,
        help=f"ADAM Modbus TCP single coil number (default: {DEFAULT_COILS})"
    )
    parser.add_argument(
        "-f", "--flip", "-t", "--toggle",
        dest="toggle", action="store_true",
        help="toggle the boolean value of the coil"
    )
    parser.add_argument(
        "-v", "--debug",
        dest="debug", action="store_true",
        help="very verbose (debug) output"
    )
    args = parser.parse_args()

    # Debug logging if requested (-v).
    LOG_LEVEL = DEFAULT_LOG_LEVEL
    if args.debug:
        LOG_LEVEL = logging.DEBUG

    # Configure logging.
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S %Z (%z)",
        format="%(asctime)s [%(levelname)s] (%(process)d): %(message)s",
        handlers=[logging.StreamHandler()], level=LOG_LEVEL
    )

    # Run main function async.
    asyncio.run(
        main(
            host=args.host,
            port=args.port,
            coils=args.coil,
            toggle=args.toggle
        ),
        debug=args.debug
    )
