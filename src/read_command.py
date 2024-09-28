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
