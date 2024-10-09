import asyncio
import threading
import tkinter as tk
from tkinter import ttk

from bleak import BleakScanner

import gui.gui_common as gc
from gui.log_viewer import LogViewer
from gui.parts_modern_button import ModernButton
from gui.parts_modern_combobox import ModernCombobox
from gui.parts_modern_label_frame import ModernLabelframe
from read_setting import SimSetting


class OperationPanel:
    def __init__(self, master: tk.Toplevel, sim_setting: SimSetting, log_viewer: LogViewer):
        self.master = master
        self.sim_setting = sim_setting
        self.log_viewer = log_viewer

        self.master.iconbitmap(gc.PATH_ICON)
        self.master.title(gc.TITLE_MAIN)
        self.master.geometry(f"+{gc.POS_MAIN_X}+{gc.POS_MAIN_Y}")

        # 非同期ループのためのイベントループ
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_async_loop, daemon=True)
        self.thread.start()

        # スキャン制御用の変数
        self.scanning = False
        self.scanner: None | BleakScanner = None

        self.setup_ui()
        self.load_addresses(0)

    def setup_ui(self) -> None:
        # ボタンフレームの作成
        scan_button_frame = ModernLabelframe(self.master, text="アドバタイズパケット")
        # スキャン開始ボタン
        self.scan_button = ModernButton(scan_button_frame, text="スキャン開始", command=self.start_scan)
        # スキャン停止ボタン
        self.stop_button = ModernButton(scan_button_frame, text="スキャン停止", command=self.stop_scan, state="disabled")

        # BDアドレス設定フレーム
        bdadrs_setting_frame = ModernLabelframe(self.master, text="BDアドレス設定")
        # コンボボックス
        self.address_var = tk.StringVar()
        self.address_combo = ModernCombobox(bdadrs_setting_frame, textvariable=self.address_var)
        # 追加ボタン
        self.add_button = ModernButton(bdadrs_setting_frame, text="追加", command=self.add_address)
        # 削除ボタン
        self.remove_button = ModernButton(bdadrs_setting_frame, text="削除", command=self.remove_address)

        # ウィジェットの配置
        scan_button_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.scan_button.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))

        bdadrs_setting_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.address_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))
        self.remove_button.pack(side=tk.LEFT, padx=(0, 5))

    def load_addresses(self, pos: int) -> None:
        addresses = self.sim_setting.get_bd_adrs()
        self.address_combo["values"] = addresses
        if pos < len(addresses):
            update_address = addresses[pos]
        else:
            update_address = ""
        self.address_combo.set(update_address)

    def add_address(self) -> None:
        new_address = self.address_var.get()
        if not new_address:
            self.log_viewer.add_log("エラー", "BDアドレスが入力されていません。")
            return

        if self.sim_setting.add_bd_adrs(new_address):
            # 追加したアドレスを表示する
            self.load_addresses(len(self.sim_setting.get_bd_adrs()) - 1)
            self.log_viewer.add_log("情報", f"BDアドレス '{new_address}' を追加しました。")
        else:
            self.log_viewer.add_log("エラー", "BDアドレスの追加に失敗しました。")

    def remove_address(self) -> None:
        address_to_remove = self.address_var.get()
        if not address_to_remove:
            self.log_viewer.add_log("エラー", "削除するBDアドレスを選択してください。")
            return

        if self.sim_setting.remove_bd_adrs(address_to_remove):
            self.load_addresses(0)
            self.log_viewer.add_log("情報", f"BDアドレス '{address_to_remove}' を削除しました。")
        else:
            self.log_viewer.add_log("エラー", "BDアドレスの削除に失敗しました。")

    def run_async_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_scan(self) -> None:
        self.scan_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.scanning = True
        asyncio.run_coroutine_threadsafe(self.run_scanner(), self.loop)

    def stop_scan(self) -> None:
        self.scanning = False
        self.log_viewer.add_log("情報", "スキャンを停止中...")
        self.stop_button.config(state="disabled")

    async def run_scanner(self) -> None:
        self.log_viewer.add_log("情報", "スキャンを開始しました...")

        bd_adrs_list = []
        self.scanner = BleakScanner()

        try:
            async with self.scanner:
                n = 5
                while self.scanning:
                    devices = await self.scanner.discover(timeout=1.0)
                    for device in devices:
                        if device.address not in bd_adrs_list:
                            bd_adrs_list.append(device.address)

                            found = len(device.name or "") > n
                            log_message = f" Found{' it' if found else ''} {device!r}"
                            self.log_viewer.add_log("スキャン", log_message)
        except Exception as e:
            self.log_viewer.add_log("エラー", f"スキャン中にエラーが発生しました: {str(e)}")
        finally:
            self.scanner = None
            self.log_viewer.add_log("情報", "スキャンを停止しました。")
            self.master.after(0, self.reset_buttons)

    def reset_buttons(self) -> None:
        self.scan_button.config(state="normal")
        self.stop_button.config(state="disabled")
