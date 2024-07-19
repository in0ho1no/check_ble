"""PSDファイルに格納されたパケットのうちヘッダ部分を扱う"""


class FieldCommon:
    """パケット内に共通するフィールドの情報"""

    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        self.length_m = len_r
        self.mean_m = mean_r
        self.data_m = data_r

    def hold_data(self, bytes_data_r: bytes, len_r: int = 0) -> bytes:
        """bytesデータから指定されたサイズだけ保持する

        Args:
            bytes_data_r (bytes): データを取得したいbytesデータ
            len_r (int, optional): 保持したいサイズ。指定しない場合は0

        Returns:
            bytes: 引数で与えられたbytesデータのうち保持しなかった分のデータ
        """
        if 0 == len_r:
            len = self.length_m
        else:
            len = len_r

        self.data_m = bytes_data_r[0:len]
        return bytes_data_r[len:]


class FieldInformation(FieldCommon):
    """Packet Information フィールド固有の情報

    Args:
        FieldCommon (): パケット内に共通するフィールドの情報
    """

    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)


class FieldNumber(FieldCommon):
    """Packet Number フィールド固有の情報

    Args:
        FieldCommon (): パケット内に共通するフィールドの情報
    """

    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_data(self) -> int:
        """パケット番号を取得する

        Returns:
            int: パケット番号
        """
        return int.from_bytes(self.data_m, "little")


class FieldTimestamp(FieldCommon):
    """Timestamp フィールド固有の情報

    Args:
        FieldCommon (): パケット内に共通するフィールドの情報
    """

    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_timestamp_us(self) -> int:
        """タイムスタンプを取得する

        0起算ではないので注意
        Returns:
            int: 取得したタイムスタンプ[us]
        """
        time_ms = int.from_bytes(self.data_m, "little")
        time_lo = time_ms & 0xFFFF
        time_hi = time_ms >> 16
        time_stamp = time_hi * 5000 + time_lo
        time_stamp_us = time_stamp / 32
        return int(time_stamp_us)


class FieldLength(FieldCommon):
    """Length フィールド固有の情報

    Args:
        FieldCommon (): パケット内に共通するフィールドの情報
    """

    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_data(self) -> int:
        """Payload+StatusBytes長を取得する

        Returns:
            int: Payload+StatusBytes長
        """
        return int.from_bytes(self.data_m, "little")


class FieldPayloadWStatusbytes(FieldCommon):
    """Payload フィールド固有の情報

    Args:
        FieldCommon (): パケット内に共通するフィールドの情報
    """

    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)
