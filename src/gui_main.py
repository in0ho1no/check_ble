import asyncio
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Any

from bleak import BleakScanner

from gui.parts_modern_button import ModernButton
from gui.parts_modern_checkbutton import ModernCheckbutton
from gui.parts_modern_scrollbar import ModernScrollbar
from gui.parts_modern_treeview import ModernTreeview

PATH_ICON = r"src\ico\ble-sim-24px.ico"

GUI_TITLE = "通信ログビューア"


class LogViewer:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title(GUI_TITLE)
        self.master.iconbitmap(PATH_ICON)
        self.master.geometry("+100+100")

        # ログのカウンター
        self.log_counter = 0
        # 自動スクロールの状態
        self.auto_scroll = tk.BooleanVar(value=True)

        self.setup_ui()

        # 非同期ループのためのイベントループ
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_async_loop, daemon=True)
        self.thread.start()

        # スキャン制御用の変数
        self.scanning = False
        self.scanner: None | BleakScanner = None

    def setup_ui(self) -> None:
        # メインフレームの作成
        self.main_frame = ttk.Frame(self.master)

        # Treeviewの設定
        self.tree = ModernTreeview(self.main_frame, columns=("No", "Timestamp", "Log"), show="headings")
        self.setup_tree_columns()

        # スクロールバーの追加
        self.scrollbar = ModernScrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.config(command=self.custom_scroll)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # 操作用フレームの作成
        self.operation_frame = ttk.Frame(self.master)

        # ボタンフレームの作成
        self.button_frame = ttk.Frame(self.operation_frame)

        # スキャン開始ボタン
        self.scan_button = ModernButton(self.button_frame, text="スキャン開始", command=self.start_scan)

        # スキャン停止ボタン
        self.stop_button = ModernButton(self.button_frame, text="スキャン停止", command=self.stop_scan, state="disabled")

        # オプション用フレームの作成
        self.option_frame = ttk.Frame(self.operation_frame)

        # ログクリアボタン
        self.clear_button = ModernButton(self.option_frame, text="ログクリア", command=self.clear_log)

        # 自動スクロールのチェックボックス
        self.auto_scroll_check = ModernCheckbutton(self.option_frame, text="自動スクロール", variable=self.auto_scroll)

        self.pack_widgets()

    def setup_tree_columns(self) -> None:
        # 列の設定
        self.tree.heading("No", text="No.")
        self.tree.heading("Timestamp", text="タイムスタンプ")
        self.tree.heading("Log", text="ログ")
        self.tree.column("No", width=50, minwidth=50, anchor="center", stretch=False)
        self.tree.column("Timestamp", width=150, minwidth=150, anchor="center", stretch=False)
        self.tree.column("Log", width=400)

        # 背景色の交互設定
        self.tree.tag_configure("odd", background="#E8E8E8")
        self.tree.tag_configure("even", background="#FFFFFF")

    def pack_widgets(self) -> None:
        # ログ表示部分の配置
        self.main_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ボタン部分の配置
        self.operation_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH, padx=10, pady=(0, 10))

        self.button_frame.pack(side=tk.LEFT, padx=5)
        self.scan_button.pack(side=tk.LEFT, anchor=tk.W, padx=(0, 5))
        self.stop_button.pack(side=tk.LEFT, anchor=tk.E, padx=(0, 5))

        self.option_frame.pack(side=tk.RIGHT, padx=5)
        self.clear_button.pack(side=tk.TOP, pady=5)
        self.auto_scroll_check.pack(side=tk.BOTTOM, pady=5)

    def add_log(self, log: str) -> None:
        self.master.after(0, self._add_log, log)

    def _add_log(self, log: str) -> None:
        # ログ追加
        self.log_counter += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tags = ("even",) if self.log_counter % 2 == 0 else ("odd",)
        self.tree.insert("", "end", values=(self.log_counter, timestamp, log), tags=tags)

        # 自動スクロールが有効な場合のみ最下部にスクロール
        if self.auto_scroll.get():
            self.tree.yview_moveto(1)

    def clear_log(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.log_counter = 0
        self.add_log("ログをクリアしました。")

    def start_scan(self) -> None:
        self.scan_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.scanning = True
        asyncio.run_coroutine_threadsafe(self.run_scanner(), self.loop)

    def stop_scan(self) -> None:
        self.scanning = False
        self.add_log("スキャンを停止中...")
        self.stop_button.config(state="disabled")

    def run_async_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def custom_scroll(self, *args: Any) -> None:
        # スクロールバーの動作をカスタマイズ
        # args[0] が 'moveto' なら、スライダーの位置を設定
        if args[0] == "moveto":
            self.tree.yview_moveto(args[1])
        else:
            # 'scroll' の場合、通常のスクロール操作 (line, page) でスクロール
            move_type = args[0]
            move_units = int(args[1])

            if move_type == "scroll":
                # スクロール量をn行にカスタマイズ
                self.tree.yview_scroll(move_units * 1, "units")

    async def run_scanner(self) -> None:
        self.add_log("スキャンを開始しました...")

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
                            self.add_log(log_message)
        except Exception as e:
            self.add_log(f"エラーが発生しました: {str(e)}")
        finally:
            self.scanner = None
            self.add_log("スキャンを停止しました。")
            self.master.after(0, self.reset_buttons)

    def reset_buttons(self) -> None:
        self.scan_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def run(self) -> None:
        self.master.mainloop()


def main() -> None:
    root = tk.Tk()
    log_viewer = LogViewer(root)

    # ウィンドウが閉じられたときの処理
    def on_closing() -> None:
        if log_viewer.scanning:
            log_viewer.stop_scan()
        log_viewer.loop.call_soon_threadsafe(log_viewer.loop.stop)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 初期ログメッセージを追加
    log_viewer.add_log("アプリケーションを起動しました。")

    # LogViewerインスタンスのrun()メソッドを呼び出してメインループを開始
    log_viewer.run()


if __name__ == "__main__":
    main()
