import asyncio

from bleak import BleakClient, BleakError, BleakScanner

from gui.log_viewer import LogViewer


class BleClient:
    def __init__(self, log_viewer: LogViewer) -> None:
        self.log_viewer = log_viewer
        self.scanning = False

    async def advertise_scanner(self) -> None:
        self.scanning = True
        self.log_viewer.add_log("情報", "スキャンを開始しました...")

        bd_adrs_list = []
        scanner = BleakScanner()

        try:
            async with scanner:
                n = 5
                while self.scanning:
                    devices = await scanner.discover(timeout=1.0)
                    for device in devices:
                        if device.address not in bd_adrs_list:
                            bd_adrs_list.append(device.address)

                            found = len(device.name or "") > n
                            log_message = f" Found{' it' if found else ''} {device!r}"
                            self.log_viewer.add_log("スキャン", log_message)
        except Exception as e:
            self.log_viewer.add_log("エラー", f"スキャン中にエラーが発生しました: {str(e)}")
        finally:
            self.log_viewer.add_log("情報", "スキャンを停止しました。")

    def stop_scanner(self) -> None:
        self.scanning = False

    async def test_client(self, bd_addr: str) -> None:
        """指定されたBDアドレスのデバイスと接続する

        Args:
            device_r (BLEDevice): 接続したいBLEDevice
        """

        def handle_disconnect(_: BleakClient) -> None:
            """デバイス切断時の処理

            Args:
                _ (BleakClient): 読み捨て
            """
            self.log_viewer.add_log("情報", "Device was disconnected, goodbye.")

        try:
            async with BleakClient(
                bd_addr,
                timeout=10,
                disconnected_callback=handle_disconnect,
                winrt={"use_cached_services": True},
            ) as client:
                print("Connected")

                self.show_client_info(client)

                print("Diconnect...")
                await client.disconnect()
            self.log_viewer.add_log("情報", "接続に成功しました。")
        except asyncio.exceptions.CancelledError:
            self.log_viewer.add_log("情報", "接続を中断しました。")
        except asyncio.exceptions.TimeoutError as e:
            self.log_viewer.add_log("エラー", f"接続に失敗しました。タイムアウト: {e}")
        except BleakError as e:
            self.log_viewer.add_log("エラー", f"接続に失敗しました。BleakError: {e}")

    def show_client_info(self, client_r: BleakClient) -> None:
        """接続先から取得できる情報を表示する

        Args:
            client_r (BleakClient): 情報表示したい接続先
        """
        self.log_viewer.add_log("情報", f"MTU size: {client_r.mtu_size}")

        # サービスとCharacteristicを表示
        for service in client_r.services:
            self.log_viewer.add_log("情報", f"Service: {service.uuid}")
            for char in service.characteristics:
                self.log_viewer.add_log("情報", f"  Characteristic: {char.uuid}, Handle: {char.handle}")
