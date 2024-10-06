from tkinter import ttk
from typing import Any

from . import gui_common as gc


class ModernCombobox(ttk.Combobox):
    """コンボボックスのカスタムクラス

    Args:
        ttk (_type_): ttk.Comboboxを継承する
    """

    # スタイルの定数をクラスレベルで定義
    STYLE_ID = "Modern.Combobox"
    FONT = (gc.COMMON_FONT, gc.COMMON_FONT_SIZE)
    COLOR_BG = gc.COMMON_BG
    COLOR_BG_MOUSE_OVER = gc.COMMON_BG_MOUSE_OVER
    COLOR_FONT = gc.COMMON_FG

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
        style.theme_use("alt")
        style.layout(
            cls.STYLE_ID,
            style.layout("TCombobox"),  # 標準レイアウトを継承
        )

        style.configure(
            cls.STYLE_ID,
            font=cls.FONT,
            background=cls.COLOR_BG,
            foreground=cls.COLOR_FONT,
        )

        cls.style_initialized = True
