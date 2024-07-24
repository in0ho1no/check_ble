import asyncio
import io
import logging

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

MODEL_NBR_UUID = "2A24"
GAP_DEVICE_NAME = "2A00"


async def scan_device(device_name_r: str) -> BLEDevice:
    """指定されたデバイスを検索する

    Args:
        device_name_r (str): 検索したいデバイス名を指定

    Returns:
        BLEDevice: BLEDevice情報を返す
    """
    bd_adrs_list: list[str] = []

    async with BleakScanner() as scanner:
        print("Scanning...")

        n = 5
        print(f"\nFind device with name longer than {n} characters...")
        async for bd, ad in scanner.advertisement_data():
            # 検出済みのBDアドレスは無視
            if bd.address in bd_adrs_list:
                continue

            # 未検出のBDアドレスを処理する
            bd_adrs_list.append(bd.address)

            # 結果を出力する
            found = len(bd.name or "") > n or len(ad.local_name or "") > n
            print(f" Found{' it' if found else ''} {bd!r}")

            # デバイス名を含まない場合何もしない
            if found is not True:
                continue

            if device_name_r == bd.name:
                print(f"Found: {device_name_r}, BDAddress:{bd.address}")
                break

    return bd


async def connect_device(device_r: BLEDevice) -> None:
    """指定されたBDアドレスのデバイスと接続する

    Args:
        adrs_r (str): 接続したいBDアドレス
    """

    def handle_disconnect(_: BleakClient) -> None:
        print("Device was disconnected, goodbye.")
        for task in asyncio.all_tasks():
            try:
                task.cancel()
            except asyncio.exceptions.CancelledError:
                logging.warn("タスク中断: handle_disconnect")

    print("Connecting...")
    async with BleakClient(
        device_r,
        disconnected_callback=handle_disconnect,
    ) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print(f'Model Number: {"".join(map(chr, model_number))}')

        model_number = await client.read_gatt_char(GAP_DEVICE_NAME)
        print(f'Model Number: {"".join(map(chr, model_number))}')


async def main() -> None:
    device = await scan_device("RTK5RLG140C")
    await connect_device(device)


# ログ用のstream用意
log_stream = io.StringIO()

# ログの設定
logging.basicConfig(
    stream=log_stream,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.exceptions.CancelledError:
        logging.warn("タスク中断: main")


# ログ出力
print(log_stream.getvalue())
