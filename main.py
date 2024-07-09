import asyncio

from bleak import BleakScanner


async def main() -> None:
    async with BleakScanner() as scanner:
        print("Scanning...")

        n = 5
        print(f"\nFind device with name longer than {n} characters...")
        async for bd, ad in scanner.advertisement_data():
            found = len(bd.name or "") > n or len(ad.local_name or "") > n
            print(f" Found{' it' if found else ''} {bd!r} with {ad!r}")
            if found:
                break


if __name__ == "__main__":
    asyncio.run(main())
