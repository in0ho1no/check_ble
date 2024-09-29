from typing import Any

import yaml  # type: ignore


class ReadData:
    KEY_FUNC = "func"
    KEY_FUNC_NAME = "name"
    KEY_FUNC_HANDLE = "handle"

    func: str
    name: str
    handle: int
    rcv_data: Any

    def __init__(self, read_data_r: dict) -> None:
        self.func = read_data_r[self.KEY_FUNC]
        self.name = read_data_r[self.KEY_FUNC_NAME]
        self.handle = read_data_r[self.KEY_FUNC_HANDLE]
        self.rcv_data = ""


class WriteData:
    def __init__(self) -> None:
        pass

    def calc_check_sum(self, data_list_r: list[int]) -> int:
        """与えられたint型リストの総和を返す

        Args:
            data_list_r (list[int]): チェックサムを求めたいリスト

        Returns:
            int: 総和
        """
        sum = 0

        for data in data_list_r:
            sum = sum + data

        return sum

    def convert_int2two_byte_list(self, tgt_r: int) -> list[int]:
        """10進整数を2バイトのint型リストに変換する

        Args:
            tgt_r (int): 変換する10進整数（0-65535の範囲）

        Raises:
            ValueError: 入力値が0-65535の範囲外の場合

        Returns:
            list[int]: 2バイトのint型リスト
        """
        # 例外処理
        if not 0 <= tgt_r <= 65535:
            raise ValueError("入力値は0から65535の範囲内である必要があります")

        # 上位バイト（8-15ビット）を取得
        high_byte = (tgt_r >> 8) & 0xFF

        # 下位バイト（0-7ビット）を取得
        low_byte = tgt_r & 0xFF

        return [high_byte, low_byte]

    def get_check_sum(self, data_list_r: list[int]) -> list[int]:
        """チェックサムの配列を取得する

        Args:
            data_list_r (list[int]): チェックサムを取得したいリスト

        Returns:
            list[int]: 2byteのチェックサムを上下入れ替えて返す
        """
        sum = self.calc_check_sum(data_list_r)
        two_byte_list = self.convert_int2two_byte_list(sum)
        return [two_byte_list[1], two_byte_list[0]]


class SimCommand:
    """設定ファイルから読み込んだ情報を保持する"""

    KEY_RW_R = "read"

    read_data_list: list[ReadData] = []

    def __init__(self, filepath_r: str) -> None:
        """設定ファイルを読み込む"""
        self.filepath_m = filepath_r
        with open(self.filepath_m) as f:
            data_rd = yaml.safe_load(f)

            for inner in data_rd[self.KEY_RW_R]:
                self.read_data_list.append(ReadData(inner))


if __name__ == "__main__":
    FILE_NAME_COMMAND = r"./src/settings/command.yaml"
    cmnd = SimCommand(FILE_NAME_COMMAND)
    for data in cmnd.read_data_list:
        print(data)
