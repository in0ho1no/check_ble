import asyncio
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Any

from bleak import BleakScanner

PATH_ICON = r"src\ico\ble-sim-24px.ico"

GUI_TITLE = "通信ログビューア"
COMMON_FONT = "メイリオ"
COMMON_BG = "#9BB3C2"
COMMON_FG = "#0F1E59"

COMMON_BG_DISABLE = "#c7e7f2"
COMMON_FG_DISABLE = "#0F1E59"


class ModernTreeview(ttk.Treeview):
    # スタイルの定数をクラスレベルで定義
    STYLE_ID = "Modern.Treeview"

    BACKGROUND_COLOR = "#F0F0F0"
    FOREGROUND_COLOR = "#0F0F0F"
    SELECTED_COLOR = "#3366CC"
    FONT = (COMMON_FONT, 10)
    ROW_HEIGHT = 25

    # ヘッダ部の定義
    CUSTUM_STYLE_MTVH = STYLE_ID + "." + "Heading"
    MTVH_BACKGROUND_COLOR = COMMON_BG_DISABLE
    MTVH_FOREGROUND_COLOR = COMMON_FG_DISABLE
    MTVH_FONT = (COMMON_FONT, 10)
    MTVH_BORDER_WIDTH = 0

    # ツリーエリアの定義
    CUSTUM_STYLE_TREE_AREA = STYLE_ID + "." + "treearea"

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master: ttk.Frame, **kw: Any) -> None:
        # スタイルを初期化
        self.initialize_style()
        # カスタムスタイルを利用する
        super().__init__(master, style=self.STYLE_ID, **kw)

    @classmethod
    def initialize_style(cls) -> None:
        """スタイルの初期化をクラスメソッドとして定義し、一度だけ実行"""
        if cls.style_initialized:
            return

        style = ttk.Style()
        # config設定が反映されないのであらかじめ用意されたテーマを設定しておく
        style.theme_use("alt")

        # treeviewの設定
        style.layout(
            cls.STYLE_ID,
            [(cls.CUSTUM_STYLE_TREE_AREA, {"sticky": "nswe"})],
        )
        style.configure(
            cls.STYLE_ID,
            font=cls.FONT,
            background=cls.BACKGROUND_COLOR,
            foreground=cls.FOREGROUND_COLOR,
            rowheight=cls.ROW_HEIGHT,
        )
        style.map(
            cls.STYLE_ID,
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
    COLOR_BG = COMMON_BG
    COLOR_BG_MOUSE_OVER = "#38759B"

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master: ttk.Frame, **kw: Any) -> None:
        # スタイルを初期化
        self.initialize_style()
        # カスタムスタイルを利用する
        super().__init__(master, style=self.STYLE_ID, **kw)

    @classmethod
    def initialize_style(cls) -> None:
        """スタイルの初期化をクラスメソッドとして定義し、一度だけ実行"""
        if cls.style_initialized:
            return

        style = ttk.Style()
        style.layout(
            cls.STYLE_ID,
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
            cls.STYLE_ID,
            # theme_useによって使えるconfigが異なるので注意
            background=cls.COLOR_BG,
            bordercolor=cls.COLOR_BG,
            troughcolor="#F0F0F0",
            width=12,
        )
        style.map(
            cls.STYLE_ID,
            background=[("active", cls.COLOR_BG_MOUSE_OVER)],
            bordercolor=[("active", cls.COLOR_BG_MOUSE_OVER)],
        )

        cls.style_initialized = True


class ModernButton(ttk.Button):
    # スタイルの定数をクラスレベルで定義
    STYLE_ID = "Modern.Button"
    FONT = (COMMON_FONT, 10)
    COLOR_BG = COMMON_BG
    COLOR_BG_MOUSE_OVER = "#38759B"
    COLOR_BG_DISABLE = COMMON_BG_DISABLE
    COLOR_FONT = COMMON_FG

    COLOR_FG_DISABLE = "#FFFFFF"

    # スタイルは1度だけ定義して再利用
    style_initialized = False

    def __init__(self, master: ttk.Frame, **kw: Any) -> None:
        # スタイルを初期化
        self.initialize_style()
        # カスタムスタイルを利用する
        super().__init__(master, style=self.STYLE_ID, **kw)

    @classmethod
    def initialize_style(cls) -> None:
        """スタイルの初期化をクラスメソッドとして定義し、一度だけ実行"""
        if cls.style_initialized:
            return

        style = ttk.Style()

        style.layout(
            cls.STYLE_ID,
            style.layout("TButton"),  # TButtonの標準レイアウトを継承
        )

        # ボタンのデフォルトスタイルの設定
        style.configure(
            cls.STYLE_ID,
            font=cls.FONT,
            background=cls.COLOR_BG,
            foreground=cls.COLOR_FONT,
            padding=2,  # 内側のパディング
            borderwidth=1,  # ボーダー幅
            relief=tk.FLAT,
        )

        # 異なる状態でのスタイルをマッピング
        style.map(
            cls.STYLE_ID,
            background=[
                ("active", cls.COLOR_BG_MOUSE_OVER),
                ("focus", cls.COLOR_BG_MOUSE_OVER),  # フォーカス時の背景色
                ("disabled", cls.COLOR_BG_DISABLE),  # 無効時の背景色
            ],
            foreground=[
                ("disabled", cls.COLOR_FG_DISABLE),  # 無効時のテキスト色
            ],
        )

        cls.style_initialized = True


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

        # ボタンフレームの作成
        self.button_frame = ttk.Frame(self.master)

        # スキャン開始ボタン
        self.scan_button = ModernButton(self.button_frame, text="スキャン開始", command=self.start_scan)

        # スキャン停止ボタン
        self.stop_button = ModernButton(self.button_frame, text="スキャン停止", command=self.stop_scan, state="disabled")

        # 自動スクロールのチェックボックス
        self.auto_scroll_check = ttk.Checkbutton(
            self.button_frame,
            text="自動スクロール",
            variable=self.auto_scroll,
            style="TCheckbutton",
        )

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
        self.button_frame.pack(side=tk.BOTTOM, pady=10)
        self.scan_button.pack(side=tk.LEFT, anchor=tk.W)
        self.stop_button.pack(side=tk.LEFT, anchor=tk.E)
        self.auto_scroll_check.pack(side=tk.LEFT)

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
