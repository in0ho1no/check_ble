import tkinter as tk
from tkinter import messagebox, ttk

from read_setting import SimSetting


class BDAddressManagerGUI:
    def __init__(self, master: tk.Tk, sim_setting: SimSetting):
        self.master = master
        self.sim_setting = sim_setting

        self.master.title("BD Address Manager")
        self.master.geometry("400x200")

        self.create_widgets()
        self.load_addresses(0)

    def create_widgets(self) -> None:
        # コンボボックス
        self.address_var = tk.StringVar()
        self.address_combo = ttk.Combobox(self.master, textvariable=self.address_var)
        self.address_combo.pack(pady=10)

        # ボタンフレーム
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        # 追加ボタン
        add_button = tk.Button(button_frame, text="追加", command=self.add_address)
        add_button.pack(side=tk.LEFT, padx=5)

        # 削除ボタン
        remove_button = tk.Button(button_frame, text="削除", command=self.remove_address)
        remove_button.pack(side=tk.LEFT, padx=5)

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
            # 追加したアドレスを再度設定する
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
    app = BDAddressManagerGUI(root, sim_setting)
    root.mainloop()


if __name__ == "__main__":
    main()
