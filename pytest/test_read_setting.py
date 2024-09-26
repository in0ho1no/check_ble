import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..//src"))


from read_setting import is_hex


# Trueを期待するテストケース
@pytest.mark.parametrize(
    "input_str",
    [
        "1a2b3c",  # 小文字の16進数
        "ABCDEF",  # 大文字の16進数
        "1234567890",  # 数字のみ
        "aBcD1234",  # 大文字小文字混在
        "abcdef",  # 小文字のみ
        "ABC123",  # 大文字と数字
        "0",  # 単一の数字
        "f",  # 単一の小文字
        "F",  # 単一の大文字
    ],
)
def test_is_hex_true(input_str: str) -> None:
    assert is_hex(input_str) is True


# Falseを期待するテストケース
@pytest.mark.parametrize(
    "input_str",
    [
        "1g2h3i",  # 16進数ではない文字を含む
        "XYZ",  # 16進数に含まれないアルファベット
        "123g456",  # 'g' は16進数ではない
        "123 456",  # スペースが含まれる
        "12-34",  # ハイフンが含まれる
        "12.34",  # ドットが含まれる
        "GHIJKL",  # 大文字の16進数に含まれない文字
        "",  # 空文字
        "!@#$%^",  # 特殊記号
        "12\n34",  # 改行が含まれる
        "12\t34",  # タブが含まれる
    ],
)
def test_is_hex_false(input_str: str) -> None:
    assert is_hex(input_str) is False


# pytestを使ったテストの実行
if __name__ == "__main__":
    pytest.main()
