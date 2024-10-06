import tkinter as tk
from tkinter import messagebox, ttk

from gui.parts_modern_button import ModernButton
from gui.parts_modern_combobox import ModernCombobox
from read_setting import SimSetting


class BDAddressManager:
    def __init__(self, master: tk.Toplevel, sim_setting: SimSetting):
        self.master = master
        self.sim_setting = sim_setting

        self.master.title("BD Address Manager")
        self.master.geometry("400x200")

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
            messagebox.showerror("エラー", "BDアドレスが入力されていません。")
            return

        if self.sim_setting.add_bd_adrs(new_address):
            # 追加したアドレスを表示する
            self.load_addresses(len(self.sim_setting.get_bd_adrs()) - 1)
            messagebox.showinfo("成功", f"BDアドレス '{new_address}' を追加しました。")
        else:
            messagebox.showerror("エラー", "BDアドレスの追加に失敗しました。")

    def remove_address(self) -> None:
        address_to_remove = self.address_var.get()
        if not address_to_remove:
            messagebox.showerror("エラー", "削除するBDアドレスを選択してください。")
            return

        if self.sim_setting.remove_bd_adrs(address_to_remove):
            self.load_addresses(0)
            messagebox.showinfo("成功", f"BDアドレス '{address_to_remove}' を削除しました。")
        else:
            messagebox.showerror("エラー", "BDアドレスの削除に失敗しました。")


def main() -> None:
    # YAMLファイルのパスを指定
    yaml_file_path = r"./src/settings/setting.yaml"

    # SimSettingインスタンスを作成
    sim_setting = SimSetting(yaml_file_path)

    # GUIアプリケーションを起動
    root = tk.Tk()

    # BDAddressManagerウィンドウの作成
    bd_manager_window = tk.Toplevel(root)
    bd_manager = BDAddressManager(bd_manager_window, sim_setting)

    root.mainloop()


if __name__ == "__main__":
    main()
