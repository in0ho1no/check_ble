import tkinter as tk

import define_main as dm
from gui.log_viewer import LogViewer
from operation_panel import OperationPanel
from read_setting import SimSetting


class BLEManager:
    def __init__(self) -> None:
        self.root = tk.Tk()
        # 不要なメインウィンドウを非表示にする
        self.root.withdraw()

        # SimSettingインスタンスを作成
        self.sim_setting = SimSetting(dm.PATH_SETTING)

        # LogViewerウィンドウの作成
        self.log_viewer_window = tk.Toplevel(self.root)
        self.log_viewer = LogViewer(self.log_viewer_window)

        # BDAddressManagerウィンドウの作成
        self.operation_panel_window = tk.Toplevel(self.root)
        self.operation_panel = OperationPanel(self.operation_panel_window, self.sim_setting, self.log_viewer)

        # ウィンドウが閉じられたときの処理
        self.log_viewer_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.operation_panel_window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self) -> None:
        if self.operation_panel.scanning:
            self.operation_panel.stop_scan()
        self.operation_panel.loop.call_soon_threadsafe(self.operation_panel.loop.stop)
        self.root.destroy()

    def run(self) -> None:
        # 初期ログメッセージを追加
        self.log_viewer.add_log("情報", "アプリケーションを起動しました。")
        self.root.mainloop()


def main() -> None:
    ble_manager = BLEManager()
    ble_manager.run()


if __name__ == "__main__":
    main()
