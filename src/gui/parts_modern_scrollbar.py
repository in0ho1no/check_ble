from tkinter import ttk
from typing import Any

from . import gui_common as gc


class ModernScrollbar(ttk.Scrollbar):
    """スクロールバーのカスタムクラス

    Args:
        ttk (_type_): ttk.Scrollbarを継承する
    """

    # スタイルの定数をクラスレベルで定義
    STYLE_ID = "Modern.Vertical.TScrollbar"
    COLOR_BG = gc.COMMON_BG
    COLOR_BG_MOUSE_OVER = gc.COMMON_BG_MOUSE_OVER

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
