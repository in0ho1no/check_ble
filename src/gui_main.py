import asyncio
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Any

from bleak import BleakScanner

GUI_TITLE = "通信ログビューア"
COMMON_FONT = "メイリオ"


class ModernTreeview(ttk.Treeview):
    # スタイルの定数をクラスレベルで定義
    CUSTUM_STYLE_MTV = "Modern.Treeview"

    BACKGROUND_COLOR = "#F0F0F0"
    FOREGROUND_COLOR = "#0F0F0F"
    SELECTED_COLOR = "#3366CC"
    FONT = (COMMON_FONT, 10)
    ROW_HEIGHT = 25

    # ヘッダ部の定義
    CUSTUM_STYLE_MTVH = CUSTUM_STYLE_MTV + "." + "Heading"
    MTVH_BACKGROUND_COLOR = "#9BB3C2"
    MTVH_FOREGROUND_COLOR = "#0F1E59"
    MTVH_FONT = (COMMON_FONT, 10)
    MTVH_BORDER_WIDTH = 0

    # ツリーエリアの定義
    CUSTUM_STYLE_TREE_AREA = CUSTUM_STYLE_MTV + "." + "treearea"

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master_r: ttk.Frame, **kw: Any) -> None:
        # カスタムスタイルを利用する
        super().__init__(master_r, style=ModernTreeview.CUSTUM_STYLE_MTV, **kw)
        if not ModernTreeview.style_initialized:
            self._initialize_style()

    @classmethod
    def _initialize_style(cls) -> None:
        """スタイルの初期化をクラスメソッドとして定義し、一度だけ実行"""
        style = ttk.Style()
        # config設定が反映されないのであらかじめ用意されたテーマを設定しておく
        style.theme_use("alt")
        print(style.theme_names())

        # treeviewの設定
        style.layout(
            cls.CUSTUM_STYLE_MTV,
            [(cls.CUSTUM_STYLE_TREE_AREA, {"sticky": "nswe"})],
        )
        style.configure(
            cls.CUSTUM_STYLE_MTV,
            font=cls.FONT,
            background=cls.BACKGROUND_COLOR,
            foreground=cls.FOREGROUND_COLOR,
            rowheight=cls.ROW_HEIGHT,
        )
        style.map(
            cls.CUSTUM_STYLE_MTV,
            background=[("selected", cls.SELECTED_COLOR)],
        )

        # ヘッダ部の設定
        style.configure(
            cls.CUSTUM_STYLE_MTVH,
            font=cls.MTVH_FONT,
            background=cls.MTVH_BACKGROUND_COLOR,
            foreground=cls.MTVH_FOREGROUND_COLOR,
            borderwidth=cls.MTVH_BORDER_WIDTH,
        )
        style.map(
            cls.CUSTUM_STYLE_MTVH,
            background=[("active", cls.MTVH_BACKGROUND_COLOR)],
        )

        # ツリーエリアの設定
        style.configure(
            cls.CUSTUM_STYLE_TREE_AREA,
            fieldbackground=cls.MTVH_FOREGROUND_COLOR,
        )

        # 初期設定完了
        cls.style_initialized = True


class ModernScrollbar(ttk.Scrollbar):
    # スタイルの定数をクラスレベルで定義
    STYLE_ID = "Modern.Vertical.TScrollbar"

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master_r: ttk.Frame, **kw: Any) -> None:
        super().__init__(master_r, style=ModernScrollbar.STYLE_ID, **kw)
        if not ModernScrollbar.style_initialized:
            self._initialize_style()

    @classmethod
    def _initialize_style(cls) -> None:
        style = ttk.Style()
        style.layout(
            ModernScrollbar.STYLE_ID,
            [
                (
                    "Vertical.Scrollbar.trough",
                    {
                        "children": [
                            # 上下矢印を表示させない
                            # ("Vertical.Scrollbar.uparrow", {"side": "top", "sticky": "we"}),
                            ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"}),
                            # ("Vertical.Scrollbar.downarrow", {"side": "bottom", "sticky": "we"}),
                        ],
                        "sticky": "ns",
                    },
                ),
            ],
        )
        style.configure(
            ModernScrollbar.STYLE_ID,
            # theme_useによって使えるconfigが異なるので注意
            background="#E8E8E8",
            bordercolor="#E8E8E8",
            troughcolor="#F0F0F0",
            width=12,
        )
        style.map(
            ModernScrollbar.STYLE_ID,
            background=[("active", "#9BB3C2")],
            bordercolor=[("active", "#9BB3C2")],
        )

        cls.style_initialized = True


class LogViewer:
    def __init__(self, master_r: tk.Tk) -> None:
        self.master_m = master_r
        self.master_m.title(GUI_TITLE)
        self.master_m.geometry("+100+100")

        # メインフレームの作成
        main_frame = ttk.Frame(self.master_m)

        # Treeviewの設定
        self.tree = ModernTreeview(main_frame, columns=("No", "Timestamp", "Log"), show="headings")
        self.tree.heading("No", text="No.")
        self.tree.heading("Timestamp", text="タイムスタンプ")
        self.tree.heading("Log", text="ログ")
        self.tree.column("No", width=50, minwidth=50, anchor="center", stretch=False)
        self.tree.column("Timestamp", width=150, minwidth=150, anchor="center", stretch=False)
        self.tree.column("Log", width=400)

        # 背景色の交互設定
        self.tree.tag_configure("odd", background="#E8E8E8")
        self.tree.tag_configure("even", background="#FFFFFF")

        # スクロールバーの追加
        self.scrollbar = ModernScrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.config(command=self.custom_scroll)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # ボタンフレームの作成
        button_frame = ttk.Frame(self.master_m)

        # スキャン開始ボタン
        self.scan_button = ttk.Button(button_frame, text="スキャン開始", command=self.start_scan)

        # スキャン停止ボタン
        self.stop_button = ttk.Button(button_frame, text="スキャン停止", command=self.stop_scan, state="disabled")

        main_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        button_frame.pack(side=tk.BOTTOM, pady=10)
        self.scan_button.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        self.stop_button.pack(side=tk.LEFT, anchor=tk.E, padx=5)

        # 非同期ループのためのイベントループ
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_async_loop, daemon=True)
        self.thread.start()

        # スキャン制御用の変数
        self.scanning = False
        self.scanner: None | BleakScanner = None

        # ログのカウンター
        self.log_counter = 0

    def add_log(self, log: str) -> None:
        self.master_m.after(0, self._add_log, log)

    def _add_log(self, log: str) -> None:
        self.log_counter += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tags = ("even",) if self.log_counter % 2 == 0 else ("odd",)
        self.tree.insert("", "end", values=(self.log_counter, timestamp, log), tags=tags)
        self.tree.yview_moveto(1)  # スクロールを最下部に移動

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

    # スクロールバーのクリックイベントをキャプチャしてスクロール量をカスタマイズ
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
                # スクロール量を2行にカスタマイズ
                self.tree.yview_scroll(move_units * 1, "units")  # 2行分ずつスクロール

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
            self.master_m.after(0, self.reset_buttons)

    def reset_buttons(self) -> None:
        self.scan_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def run(self) -> None:
        self.master_m.mainloop()


def main() -> None:
    root = tk.Tk()
    log_viewer = LogViewer(root)

    # ウィンドウが閉じられたときの処理を追加
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
