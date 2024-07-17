SRC_FILE_PATH = r"other_in\20240716_2_pc2fpb_2a24-2a00.psd"


class FieldCommon:
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        self.length = len_r
        self.mean = mean_r
        self.data = data_r

    def get_bytes_data(
        self,
        bytes_data_r: bytes,
        len_r: int = 0,
    ) -> bytes:
        if 0 == len_r:
            len = self.length
        else:
            len = len_r

        self.data = bytes_data_r[0:len]
        # print(self.data)
        return bytes_data_r[len:]


class FieldInfo(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)


class FieldNo(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_number(self) -> int:
        return int.from_bytes(self.data, "little")


class FieldTime(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)


class FieldLen(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)

    def get_length(self) -> int:
        return int.from_bytes(self.data, "little")


class FieldPayload(FieldCommon):
    def __init__(self, len_r: int, mean_r: str, data_r: bytes = b"") -> None:
        super().__init__(len_r, mean_r, data_r)


class PsdData:
    def __init__(self, info_r: FieldInfo, no_r: FieldNo, time_r: FieldTime, len_r: FieldLen, pay_r: FieldPayload) -> None:
        self.pkt_info = info_r


with open(SRC_FILE_PATH, "rb") as f:
    file_contents = f.read()

    psd_list: list[PsdData] = []
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

        psd_list.append(PsdData(pkt_info, pkt_no, pkt_time, pkt_len, pkt_payload))

    print(len(psd_list))
