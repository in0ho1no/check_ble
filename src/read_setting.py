import re

import yaml  # type: ignore


def is_hex(chk_r: str) -> bool:
    """16進文字列か否かを判定する

    Args:
        chk_r (str): 確認したい文字列

    Returns:
        bool: 16進文字列である:True, 16進文字列ではない:False
    """
    return bool(re.fullmatch(r"[0-9a-fA-F]+", chk_r))


class SimSetting:
    """設定ファイルから読み込んだ情報を保持する"""

    KEY_INFO = "info"
    KEY_BD_ADRS = "bdaddress"

    SEP_BD_ADRS = ":"

    def __init__(self, filepath_r: str) -> None:
        self.filepath_m = filepath_r
        self.read_setting()

    def read_setting(self) -> None:
        """設定ファイルを読み込む"""
        with open(self.filepath_m) as f:
            data_rd = yaml.safe_load(f)

            self.__bd_adrs_m = self.__chk_bd_adrs(data_rd[self.KEY_INFO][self.KEY_BD_ADRS])

    def __chk_bd_adrs(self, chk_r: str) -> str:
        """指定された文字列がBDアドレスとして適切かチェックする

        Args:
            chk_r (str): チェックしたい文字列

        Returns:
            str: BDアドレスに適合しない: 空白文字, BDアドレスに適合する: チェック対象の文字列をそのまま返す
        """
        if self.SEP_BD_ADRS not in chk_r:
            print(f"エラー: 設定ファイル: BDアドレスは{self.SEP_BD_ADRS}で区切ってください。")
            return ""

        split_bd_adrs = chk_r.split(self.SEP_BD_ADRS)
        for split_text in split_bd_adrs:
            if 2 != len(split_text):
                print(f"エラー: 設定ファイル: BDアドレスは2文字ずつ{self.SEP_BD_ADRS}で区切ってください。")
                return ""

            if is_hex(split_text) is False:
                print("エラー: 設定ファイル: BDアドレスは16進文字列で指定してください。")
                return ""

        if len(split_bd_adrs) != 6:
            print("エラー: 設定ファイル: BDアドレスは12文字で指定してください。")
            return ""

        return chk_r

    def get_bd_adrs(self) -> str:
        """保持しているBDアドレスを取得する

        Returns:
            str: 空白文字|BDアドレス
        """
        return self.__bd_adrs_m
