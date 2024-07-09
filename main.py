import asyncio

from bleak import BleakScanner


async def main() -> None:
    bd_adrs_list: list[str] = []

    async with BleakScanner() as scanner:
        print("Scanning...")

        n = 5
        cnt = 10
        print(f"\nFind device with name longer than {n} characters...")
        async for bd, ad in scanner.advertisement_data():
            if bd.address not in bd_adrs_list:
                bd_adrs_list.append(bd.address)

                found = len(bd.name or "") > n or len(ad.local_name or "") > n
                print(f" Found{' it' if found else ''} {bd!r}")
                if found:
                    cnt -= 1

                if 0 == cnt:
                    break


if __name__ == "__main__":
    asyncio.run(main())
