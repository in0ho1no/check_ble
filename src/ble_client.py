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
            bd_addr (str): 接続したいBDアドレス
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
            if "Unreachable" in str(e):
                self.log_viewer.add_log("エラー", "接続に失敗しました。再接続を試みてください。")
            else:
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

    async def read_client_data(self, bd_addr: str) -> None:
        """指定されたBDアドレスのデバイスと接続する

        Args:
            bd_addr (str): 接続したいBDアドレス
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

                # 接続端末からハンドルを取得する
                handle_list = []
                for service in client.services:
                    for char in service.characteristics:
                        handle_list.append(char.handle)

                # 取得したハンドルから情報を取得する
                for handle in handle_list:
                    try:
                        rcv_data = await client.read_gatt_char(handle, use_cached=True)
                        print(rcv_data)
                        self.log_viewer.add_log("情報", f"{handle=}")
                        self.log_viewer.add_log("情報", f"    生値: {rcv_data}")
                        self.log_viewer.add_log("情報", f'    ASCII: {"".join(map(chr, rcv_data))}')
                        self.log_viewer.add_log("情報", f'    16進: {",".join(map(hex, rcv_data))}')
                    except BleakError as e:
                        # 読み出せないハンドルは無視
                        # BleakError: Could not read characteristic handle XXXX: Protocol Error 0x02: Read Not Permitted
                        print(e)

                print("Diconnect...")
                await client.disconnect()
            self.log_viewer.add_log("情報", "接続に成功しました。")
        except asyncio.exceptions.CancelledError:
            self.log_viewer.add_log("情報", "接続を中断しました。")
        except asyncio.exceptions.TimeoutError as e:
            self.log_viewer.add_log("エラー", f"接続に失敗しました。タイムアウト: {e}")
        except BleakError as e:
            if "Unreachable" in str(e):
                self.log_viewer.add_log("エラー", "接続に失敗しました。再接続を試みてください。")
            else:
                self.log_viewer.add_log("エラー", f"接続に失敗しました。BleakError: {e}")
