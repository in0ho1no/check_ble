import asyncio
import io
import logging

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

from read_setting import SimSetting

FILE_NAME_SETTING = r"./settings/setting.yaml"


async def scan_device(bd_addr_r: str) -> BLEDevice:
    """指定されたデバイスを検索する

    Args:
        bd_addr_r (str): 検索したいBDアドレスを指定

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

            if bd_addr_r == bd.address:
                print(f"Found: {bd.name}, BDAddress:{bd.address}")
                break

    return bd


def show_client_info(client_r: BleakClient) -> None:
    """接続先から取得できる情報を表示する

    Args:
        client_r (BleakClient): 情報表示したい接続先
    """
    print(f"MTU size{client_r.mtu_size}")

    # サービスとCharacteristicを表示
    for service in client_r.services:
        print(f"Service: {service.uuid}")
        for char in service.characteristics:
            print(f"  Characteristic: {char.uuid}, Handle: {char.handle}")


async def connect_device(device_r: BLEDevice) -> None:
    """指定されたBDアドレスのデバイスと接続する

    Args:
        device_r (BLEDevice): 接続したいBLEDevice
    """

    def handle_disconnect(_: BleakClient) -> None:
        # 実行中のタスクを中断して終了する
        print("Device was disconnected, goodbye.")
        for task in asyncio.all_tasks():
            task.cancel()

    print("Connecting...")
    async with BleakClient(
        device_r,
        disconnected_callback=handle_disconnect,
        winrt={"use_cached_services": True},
    ) as client:
        print("Connected")
        show_client_info(client)

        print("Diconnect...")
        await client.disconnect()


async def main() -> None:
    sim_setting = SimSetting(FILE_NAME_SETTING)
    bd_adrs = sim_setting.get_bd_adrs()
    if "" == bd_adrs:
        return

    # 接続対象のスキャン
    device = await scan_device(bd_adrs)
    # 対象と接続
    try:
        await connect_device(device)
    except asyncio.exceptions.CancelledError:
        logging.warning("タスク中断")
    except asyncio.exceptions.TimeoutError:
        logging.warning("タスクタイムアウト")
    except BleakError as e:
        logging.warning(f"BleakError: {e}")


# ログ用のstream用意
log_stream = io.StringIO()

# ログの設定
logging.basicConfig(
    stream=log_stream,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    asyncio.run(main())


# ログ出力
print(log_stream.getvalue())
