#!/usr/bin/env python3
import asyncio
import logging
from argparse import ArgumentParser
from pymodbus.client import AsyncModbusTcpClient


DEFAULT_HOST = "adam.home.ericoc.com"
DEFAULT_PORT = 502
DEFAULT_LOG_LEVEL = logging.WARNING


async def main(
    host: str = DEFAULT_HOST,
    port: int = 502,
    coils: (list, int, None) = None
):
    """ADAM unit interaction."""
    client = AsyncModbusTcpClient(host=host, port=port)
    await client.connect()

    # Default to six (6) read-write coils: 16, 17, 18, 19, 20, 21.
    if not coils:
        coils = range(16, 22)
    if isinstance(coils, int):
        coils = [coils]

    # Iterate each coil.
    for coil in coils:

        # Toggle the existing value of the coil, if requested.
        if args.toggle:
            original = await client.read_coils(address=coil, count=1)
            value = False
            if original.bits[0] is value:
                value = True
            await client.write_coil(address=coil, value=value)

        # Display the final value of the coil.
        recheck = await client.read_coils(address=coil, count=1)
        logging.warning(f"Coil #{coil}: {recheck.bits[0]}")

    # Disconnect from ADAM unit.
    client.close()


# Main entry point.
if __name__ == "__main__":

    # Set up argument parser.
    parser = ArgumentParser(description="ADAM unit testing")
    adam_unit = parser.add_argument_group(
        title="ADAM unit",
        description="Connection details for ADAM unit"
    )
    adam_unit.add_argument(
        "-H", "--host", "--hostname",
        dest="hostname",
        default=DEFAULT_HOST,
        help=f'ADAM unit hostname or IP address (default: "{DEFAULT_HOST}")'
    )
    adam_unit.add_argument(
        "-p", "--port",
        dest="port",
        default=DEFAULT_PORT,
        help=f"ADAM unit ModbusTCP port number (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "-c", "--coil",
        dest="coil", type=int,
        help="single coil number (default: range of 16-21)"
    )
    parser.add_argument(
        "-f", "--flip", "-t", "--toggle",
        dest="toggle", action="store_true",
        help="toggle the boolean value of the coil"
    )
    log_parser = parser.add_mutually_exclusive_group()
    log_parser.add_argument(
        "-v", "--verbose",
        dest="verbose", action="store_true",
        help="verbose output"
    )
    log_parser.add_argument(
        "-vv", "--debug",
        dest="debug", action="store_true",
        help="very verbose (debug) output"
    )
    args = parser.parse_args()

    # Log level based on arguments (-v or -vv).
    LOG_LEVEL = DEFAULT_LOG_LEVEL
    if args.verbose:
        LOG_LEVEL = logging.INFO
    if args.debug:
        LOG_LEVEL = logging.DEBUG

    # Configure logging.
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S %Z (%z)",
        format="%(asctime)s [%(levelname)s] (%(process)d): %(message)s",
        handlers=[logging.StreamHandler()],
        level=LOG_LEVEL
    )

    # Run main function async.
    asyncio.run(main(coils=args.coil))
