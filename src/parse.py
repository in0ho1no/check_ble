SRC_FILE_PATH = r"other_in\20240718_0_test.psd"


class FieldCommon:
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
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)


class FieldNumber(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_number(self) -> int:
        """パケット番号を取得する

        Returns:
            int: パケット番号
        """
        return int.from_bytes(self.data_m, "little")


class FieldTimestamp(FieldCommon):
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
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_length(self) -> int:
        """Payload長を取得する

        Returns:
            int: Payload長
        """
        return int.from_bytes(self.data_m, "little")


class FieldPayload(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)


class PacketData:
    def __init__(self, info_r: FieldInformation, no_r: FieldNumber, time_r: FieldTimestamp, len_r: FieldLength, pay_r: FieldPayload) -> None:
        self.fld_info_m = info_r
        self.fld_no_m = no_r
        self.fld_time_m = time_r
        self.fld_len_m = len_r
        self.fld_payload_m = pay_r

        self.__set_payload_len()
        self.__set_payload_raw()
        self.__set_status_bytes()
        self.__set_crc()
        self.__set_rssi()

    def __set_payload_len(self) -> None:
        """payload長として保持する"""
        self.payload_len_m = self.fld_len_m.get_length()

    def __set_payload_raw(self) -> None:
        """payloadをbytesデータのまま保持する"""
        self.payload_raw_m = self.fld_payload_m.data_m[: self.payload_len_m - 2]

    def __set_status_bytes(self) -> None:
        """status bytesをbytesデータのまま保持する"""
        self.status_bytes_raw_m = self.fld_payload_m.data_m[self.payload_len_m - 2 : self.payload_len_m]

    def __set_crc(self) -> None:
        """CRCを保持する"""
        # payloadの末尾3byteがCRC
        crc_bytes = self.payload_raw_m[-3:]
        self.crc_m = hex(int.from_bytes(crc_bytes, "little"))

    def __set_rssi(self) -> None:
        """RSSIを保持する"""

        # デバイスに応じた優良値(?)のようなものが存在する模様なので加味した値を保持する
        self.rssi_m = -94 + self.status_bytes_raw_m[0]

    def set_timestamp(self, time_us: int) -> None:
        self.timestamp_m = time_us


def main() -> None:
    with open(SRC_FILE_PATH, "rb") as f:
        file_contents = f.read()

    cnt = 0
    base_time_us = 0
    psd_list: list[PacketData] = []
    while file_contents:
        # フィールド単位で格納する
        pkt_info = FieldInformation(1, "Packet_Information")
        pkt_no = FieldNumber(4, "Packet_Number")
        pkt_time = FieldTimestamp(8, "Timestamp_ms")
        pkt_len = FieldLength(2, "PacketLength")
        pkt_payload = FieldPayload(256, "PayloadData")

        file_contents = pkt_info.hold_data(file_contents)
        file_contents = pkt_no.hold_data(file_contents)
        file_contents = pkt_time.hold_data(file_contents)
        file_contents = pkt_len.hold_data(file_contents)
        file_contents = pkt_payload.hold_data(file_contents)
        pkt = PacketData(pkt_info, pkt_no, pkt_time, pkt_len, pkt_payload)

        # タイムスタンプを0リセットする
        if 0 == cnt:
            base_time_us = pkt_time.get_timestamp_us()
        pkt.set_timestamp(pkt_time.get_timestamp_us() - base_time_us)

        psd_list.append(pkt)
        cnt += 1

    print(len(psd_list))


if __name__ == "__main__":
    main()
