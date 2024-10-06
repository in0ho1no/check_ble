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

    BD_ADRS_SEPALATE = ":"
    BD_ADRS_PARTS = 6
    BD_ADRS_PART_LENGTH = 2

    def __init__(self, filepath_r: str) -> None:
        self.filepath_m = filepath_r
        self.read_setting()

    def read_setting(self) -> None:
        """設定ファイルを読み込む"""
        with open(self.filepath_m) as f:
            data_rd = yaml.safe_load(f)

            self.__bd_adrs_list_m = []
            bd_adrs_list = data_rd[self.KEY_INFO][self.KEY_BD_ADRS]
            for bd_adrs in bd_adrs_list:
                if self.__chk_bd_adrs(bd_adrs) is None:
                    continue

                self.__bd_adrs_list_m.append(bd_adrs)

    @classmethod
    def __chk_bd_adrs(cls, chk_r: str) -> str | None:
        """指定された文字列がBDアドレスとして適切かチェックする

        Args:
            chk_r (str): チェックしたい文字列

        Returns:
            str: BDアドレスに適合しない: 空白文字, BDアドレスに適合する: チェック対象の文字列をそのまま返す
        """
        if cls.BD_ADRS_SEPALATE not in chk_r:
            print(f"エラー: 設定ファイル: BDアドレスは{cls.BD_ADRS_SEPALATE}で区切ってください。")
            return None

        split_bd_adrs = chk_r.split(cls.BD_ADRS_SEPALATE)
        for split_text in split_bd_adrs:
            if cls.BD_ADRS_PART_LENGTH != len(split_text):
                print(f"エラー: 設定ファイル: BDアドレスは{cls.BD_ADRS_PART_LENGTH}文字ずつ{cls.BD_ADRS_SEPALATE}で区切ってください。")
                return None

            if is_hex(split_text) is False:
                print("エラー: 設定ファイル: BDアドレスは16進文字列で指定してください。")
                return None

        if cls.BD_ADRS_PARTS != len(split_bd_adrs):
            print(f"エラー: 設定ファイル: BDアドレスは{cls.BD_ADRS_PARTS*cls.BD_ADRS_PART_LENGTH}文字で指定してください。")
            return None

        return chk_r

    def get_bd_adrs(self) -> list[str]:
        """保持しているBDアドレスを取得する

        Returns:
            str: 空白文字|BDアドレス
        """
        return self.__bd_adrs_list_m
