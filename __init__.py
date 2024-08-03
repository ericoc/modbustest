#!/usr/bin/env python3
import asyncio
import logging
from argparse import ArgumentParser
from pymodbus.client import AsyncModbusTcpClient


async def main(
    host: str = "adam.home.ericoc.com",
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
        if args.flip:
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
    parser = ArgumentParser(description="ADAM-6060 unit testing")
    parser.add_argument("-c", "--coil", dest="coil", type=int)
    parser.add_argument("-f", "--flip", dest="flip", action="store_true")
    log_parser = parser.add_mutually_exclusive_group()
    log_parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")
    log_parser.add_argument("-vv", "--debug", dest="debug", action="store_true")
    args = parser.parse_args()

    # Log level based on arguments (-v or -vv).
    LOG_LEVEL = logging.WARNING
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
