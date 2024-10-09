import tkinter as tk
from tkinter import ttk

import gui.gui_common as gc
from gui.log_viewer import LogViewer
from gui.parts_modern_button import ModernButton
from gui.parts_modern_combobox import ModernCombobox
from read_setting import SimSetting


class BDAddressManager:
    def __init__(self, master: tk.Toplevel, sim_setting: SimSetting, log_viewer: LogViewer):
        self.master = master
        self.sim_setting = sim_setting
        self.log_viewer = log_viewer

        self.master.iconbitmap(gc.PATH_ICON)
        self.master.title(gc.TITLE_MAIN)
        self.master.geometry(f"+{gc.POS_MAIN_X}+{gc.POS_MAIN_Y}")

        self.create_widgets()
        self.load_addresses(0)

    def create_widgets(self) -> None:
        # BDアドレス設定フレーム
        bdadrs_setting_frame = ttk.Frame(self.master)

        # コンボボックス
        self.address_var = tk.StringVar()
        self.address_combo = ModernCombobox(bdadrs_setting_frame, textvariable=self.address_var)

        # ボタンフレーム
        bdadrs_setting_frame.pack(pady=10)

        # 追加ボタン
        self.add_button = ModernButton(bdadrs_setting_frame, text="追加", command=self.add_address)

        # 削除ボタン
        self.remove_button = ModernButton(bdadrs_setting_frame, text="削除", command=self.remove_address)

        # ウィジェットの配置
        self.address_combo.pack(side=tk.LEFT, pady=5)
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.remove_button.pack(side=tk.LEFT, padx=5)

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
            self.log_viewer.add_log("エラー: BDアドレスが入力されていません。")
            return

        if self.sim_setting.add_bd_adrs(new_address):
            # 追加したアドレスを表示する
            self.load_addresses(len(self.sim_setting.get_bd_adrs()) - 1)
            self.log_viewer.add_log(f"成功: BDアドレス '{new_address}' を追加しました。")
        else:
            self.log_viewer.add_log("エラー: BDアドレスの追加に失敗しました。")

    def remove_address(self) -> None:
        address_to_remove = self.address_var.get()
        if not address_to_remove:
            self.log_viewer.add_log("エラー: 削除するBDアドレスを選択してください。")
            return

        if self.sim_setting.remove_bd_adrs(address_to_remove):
            self.load_addresses(0)
            self.log_viewer.add_log(f"成功: BDアドレス '{address_to_remove}' を削除しました。")
        else:
            self.log_viewer.add_log("エラー: BDアドレスの削除に失敗しました。")
