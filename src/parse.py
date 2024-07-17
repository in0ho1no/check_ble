SRC_FILE_PATH = r"other_in\20240716_2_pc2fpb_2a24-2a00.psd"


class FieldCommon:
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        self.length_m = len_r
        self.mean_m = mean_r
        self.data_m = data_r

    def get_bytes_data(
        self,
        bytes_data_r: bytes,
        len_r: int = 0,
    ) -> bytes:
        if 0 == len_r:
            len = self.length_m
        else:
            len = len_r

        self.data_m = bytes_data_r[0:len]
        return bytes_data_r[len:]


class FieldInfo(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)


class FieldNo(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_number(self) -> int:
        return int.from_bytes(self.data_m, "little")


class FieldTime(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_time_us(self) -> int:
        time_ms = int.from_bytes(self.data_m, "little")
        time_lo = time_ms & 0xFFFF
        time_hi = time_ms >> 16
        time_stamp = time_hi * 5000 + time_lo
        time_stamp_us = time_stamp / 32
        return int(time_stamp_us)


class FieldLen(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_length(self) -> int:
        return int.from_bytes(self.data_m, "little")


class FieldPayload(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)


class PacketData:
    def __init__(self, info_r: FieldInfo, no_r: FieldNo, time_r: FieldTime, len_r: FieldLen, pay_r: FieldPayload) -> None:
        self.pkt_info_m = info_r
        self.pkt_no_m = no_r
        self.pkt_time_m = time_r
        self.pkt_len_m = len_r
        self.pkt_payload_m = pay_r

    def set_timestamp(self, time_us: int) -> None:
        self.timestamp_m = time_us
        print(time_us)


with open(SRC_FILE_PATH, "rb") as f:
    file_contents = f.read()

    cnt = 0
    base_time_us = 0
    psd_list: list[PacketData] = []
    while file_contents:
        pkt_info = FieldInfo(1, "Packet_Information")
        pkt_no = FieldNo(4, "Packet_Number")
        pkt_time = FieldTime(8, "Timestamp_ms")
        pkt_len = FieldLen(2, "PacketLength")
        pkt_payload = FieldPayload(256, "PayloadData")

        file_contents = pkt_info.get_bytes_data(file_contents)
        file_contents = pkt_no.get_bytes_data(file_contents)
        file_contents = pkt_time.get_bytes_data(file_contents)
        file_contents = pkt_len.get_bytes_data(file_contents)
        file_contents = pkt_payload.get_bytes_data(file_contents)
        pkt = PacketData(pkt_info, pkt_no, pkt_time, pkt_len, pkt_payload)

        # タイムスタンプを正規化する
        if cnt == 0:
            base_time_us = pkt_time.get_time_us()

        pkt.set_timestamp(pkt_time.get_time_us() - base_time_us)
        psd_list.append(pkt)

        cnt += 1

    print(len(psd_list))
