import logging

from parse_PSD_head import FieldInformation as FInfo
from parse_PSD_head import FieldLength as FLength
from parse_PSD_head import FieldNumber as FNumber
from parse_PSD_head import FieldPayloadWStatusbytes as FPayloadWSb
from parse_PSD_head import FieldTimestamp as FTimeStamp
from parse_PSD_Payload import Payload
from parse_PSD_SB import StatusBytes

ADVERTISING_PACKET_ACCESS_ADRS = 0x8E89BED6
ADVERTISING_PACKET_CHANNEL_LIST = [37, 38, 39]


class PacketData:
    def __init__(self, info_r: FInfo, no_r: FNumber, time_r: FTimeStamp, len_r: FLength, pay_r: FPayloadWSb) -> None:
        self.fld_info_m = info_r
        self.fld_no_m = no_r
        self.fld_timestamp_m = time_r
        self.fld_length_m = len_r
        self.fld_payload_w_sb_m = pay_r

        self.__set_payload()
        self.__set_status_bytes()

        self.__set_pdu_type()

    def __set_payload(self) -> None:
        """payloadをbytesデータのまま保持する"""
        raw_data = self.fld_payload_w_sb_m.data_m[: self.fld_length_m.get_data() - 2]
        self.fld_payload_m = Payload(raw_data)

    def __set_status_bytes(self) -> None:
        """status bytesをbytesデータのまま保持する"""
        raw_data = self.fld_payload_w_sb_m.data_m[self.fld_length_m.get_data() - 2 : self.fld_length_m.get_data()]
        self.fld_status_bytes_m = StatusBytes(raw_data)

    def set_timestamp(self, time_us: int) -> None:
        self.timestamp_m = time_us

    def __set_pdu_type(self) -> None:
        if ADVERTISING_PACKET_ACCESS_ADRS == self.fld_payload_m.access_adrs_m:
            if self.fld_status_bytes_m.channel_m in ADVERTISING_PACKET_CHANNEL_LIST:
                # Access Address と Channelの両方を満足したとき Advertise Packet とみなす
                pass
            else:
                # Channelが異なるので読み捨てる
                logging.warn("Err")
        else:
            if self.fld_status_bytes_m.channel_m in ADVERTISING_PACKET_CHANNEL_LIST:
                # Channelが異なるので読み捨てる
                logging.warn("Err")
            else:
                # Access Address と Channelの両方を満足したとき DataPhys Packet とみなす
                # logging.debug(f"Phy: {self.fld_payload_m.access_adrs_m}, {self.fld_status_bytes_m.channel_m}")
                pass


def get_packet_list(file_contents_r: bytes) -> list[PacketData]:
    cnt = 0
    psd_list: list[PacketData] = []
    while file_contents_r:
        # フィールド単位で格納する
        pkt_info = FInfo(1, "Packet_Information")
        pkt_no = FNumber(4, "Packet_Number")
        pkt_time = FTimeStamp(8, "Timestamp_ms")
        pkt_len = FLength(2, "PacketLength")
        pkt_payload = FPayloadWSb(256, "PayloadData")

        file_contents_r = pkt_info.hold_data(file_contents_r)
        file_contents_r = pkt_no.hold_data(file_contents_r)
        file_contents_r = pkt_time.hold_data(file_contents_r)
        file_contents_r = pkt_len.hold_data(file_contents_r)
        file_contents_r = pkt_payload.hold_data(file_contents_r)
        pkt = PacketData(pkt_info, pkt_no, pkt_time, pkt_len, pkt_payload)

        # タイムスタンプを0リセットする
        if 0 == cnt:
            base_time_us = pkt_time.get_timestamp_us()
        pkt.set_timestamp(pkt_time.get_timestamp_us() - base_time_us)

        psd_list.append(pkt)
        cnt += 1

        # 結果出力
        print(f"\
{pkt.fld_no_m.get_data()},\
{pkt.timestamp_m},\
{pkt.fld_status_bytes_m.channel_m},\
{hex(pkt.fld_payload_m.access_adrs_m)},\
{pkt.fld_status_bytes_m.rssi_m},\
{pkt.fld_status_bytes_m.indicate_crc_m},\
")

    return psd_list
