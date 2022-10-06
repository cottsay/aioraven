# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from dataclasses import dataclass
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from enum import Enum
from enum import IntEnum
from typing import List
from typing import Tuple

from iso4217 import Currency


def convert_bool(raw):
    if raw is None:
        return None
    if raw == 'Y':
        return True
    if raw == 'N':
        return False
    raise ValueError(f"Invalid boolean format: '{raw}'")


def convert_currency(raw):
    if raw is None:
        return None
    currency = next(filter(lambda c: c.number == int(raw, 0), Currency), None)
    if currency is None:
        raise ValueError(f"Invalid currency number: '{raw}'")
    return currency


def convert_date(raw):
    if raw is None:
        return None
    if len(raw) < 8:
        raise ValueError(f"Invalid date format: '{raw}'")
    return date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))


def convert_date_code(raw):
    if raw is None:
        return None
    if len(raw) < 9:
        raise ValueError(f"Invalid date code format: '{raw}'")
    return (
        convert_date(raw[:8]),
        raw[8:],
    )


def convert_datetime(raw, utc=False):
    if raw is None or raw == 0xffffff:
        return None
    value = datetime(
        2000, 1, 1, 0, 0,
        tzinfo=timezone.utc if utc else None)
    return value + timedelta(seconds=int(raw, 0))


def convert_float(raw_value, raw_div):
    if raw_value is None:
        return None
    value = float(int(raw_value, 0))
    if raw_div is None:
        return value
    return value / 10 ** int(raw_div, 0)


def convert_hex_to_bytes(raw):
    if raw is None:
        return None
    if raw.startswith('0x'):
        raw = raw[2:]
    return bytes.fromhex(raw)


def convert_int(raw):
    if raw is None:
        return raw
    return int(raw, 0)


def convert_int_formatted(
    raw, mult=None, div=None, digits_right=None, digits_left=None,
    suppress_leading_zero=None
):
    if raw is None:
        return None
    value = int(raw, 0)
    if mult is not None:
        mult = int(mult, 0)
        value *= mult
    if div is not None:
        div = int(div, 0)
        value /= div
    precision = ""
    if digits_right is not None:
        precision = int(digits_right, 0)
    width = ""
    if digits_left is not None:
        if precision == "":
            precision = len(str(value).split(".")[-1])
        width = int(digits_left, 0) + 1 + precision
    value = "{:0>{width}.{precision}f}".format(value, **locals())
    if suppress_leading_zero is not None:
        if suppress_leading_zero == "Y":
            value = value.lstrip("0")
            if value[0] == ".":
                value = "0" + value
    return value


def convert_price(raw_value, raw_div, exponent):
    value = str(convert_float(raw_value, raw_div))
    if exponent is not None:
        major, minor = value.split('.', 1)
        if exponent == 0 and minor == '0':
            return major
        missing = exponent - len(minor)
        if missing > 0:
            value += '0' * missing
    return value


def convert_timedelta(raw):
    if raw is None:
        return None
    value = int(raw, 0)
    return timedelta(seconds=value)


class ConnectionState(str, Enum):
    """Indicates the current state of the device."""

    __str__ = str.__str__

    INITIALIZING = "Initializing"
    NETWORK_DISCOVERY = "Network Discovery"
    JOINING = "Joining"
    JOIN_FAIL = "Join: Fail"
    JOIN_SUCCESS = "Join: Success"
    AUTHENTICATING = "Authenticating"
    AUTHENTICATING_SUCCESS = "Authenticating: Success"
    AUTHENTICATING_FAIL = "Authenticating: Fail"
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    REJOINING = "Rejoining"


class DataStatus(IntEnum):
    """Indicates the status of returned data."""

    SUCCESS = 0
    UNDEFINED = 1
    NOT_SUPPORTED = 2
    INVALID_END_TIME = 3
    TOO_MANY = 4
    NONE_AVAILABLE = 5


class IntervalChannel(str, Enum):
    """Profile interval data channels."""

    DELIVERED = "Delivered"
    RECEIVED = "Received"


class IntervalPeriod(IntEnum):
    """Sampling intervals."""

    DAILY = 0
    SIXTY_MIN = 1
    THIRTY_MIN = 2
    FIFTEEN_MIN = 3
    TEN_MIN = 4
    SEVEN_AND_A_HALF_MIN = 5
    FIVE_MIN = 6
    TWO_AND_A_HALF_MIN = 7


class MessageQueue(str, Enum):
    """Types of queues messages can occupy."""

    __str__ = str.__str__

    ACTIVE = "Active"
    CANCEL_PENDING = "Cancel Pending"


class MeterType(str, Enum):
    """Types of meters to connect to."""

    __str__ = str.__str__

    ELECTRIC = "electric"
    GAS = "gas"
    WATER = "water"
    OTHER = "other"


class ScheduledEvent(str, Enum):
    """Types of events which can be scheduled."""

    __str__ = str.__str__

    TIME = "time"
    PRICE = "price"
    DEMAND = "demand"
    SUMMATION = "summation"
    MESSAGE = "message"


@dataclass
class ConnectionStatus:
    """Diagnostic information about the meter connection."""

    device_mac_id: bytes
    coord_mac_id: bytes
    status: ConnectionState
    description: str
    status_code: bytes
    ext_pan_id: bytes
    channel: int
    short_addr: bytes
    link_strength: int


@dataclass
class CurrentPeriodUsage:
    """Total consumption for current accumulation period."""

    device_mac_id: bytes
    meter_mac_id: bytes
    time_stamp: datetime
    current_usage: str
    start_date: datetime


@dataclass
class CurrentSummationDelivered:
    """Total consumption at the meter to date."""

    device_mac_id: bytes
    meter_mac_id: bytes
    time_stamp: datetime
    summation_delivered: str
    summation_received: str


@dataclass
class DeviceInfo:
    """Information about the device."""

    device_mac_id: bytes
    install_code: bytes
    link_key: bytes
    fw_version: str
    hw_version: str
    image_type: str
    manufacturer: str
    model_id: str
    date_code: Tuple[date, str]


@dataclass
class InstantaneousDemand:
    """Current consumption rate at the meter."""

    device_mac_id: bytes
    meter_mac_id: bytes
    time_stamp: datetime
    demand: str


@dataclass
class LastPeriodUsage:
    """Total consumption for the previous accumulation period."""

    device_mac_id: bytes
    meter_mac_id: bytes
    last_usage: str
    start_date: datetime
    end_date: datetime


@dataclass
class MessageCluster:
    """Text messages from the meter."""

    device_mac_id: bytes
    meter_mac_id: bytes
    time_stamp: datetime
    message_id: bytes
    text: str
    confirmation_required: bool
    confirmed: bool
    queue: MessageQueue


@dataclass
class MeterInfo:
    """Information about a meter on the network."""

    device_mac_id: bytes
    meter_mac_id: bytes
    meter_type: MeterType
    nick_name: str
    account: str
    auth: str
    host: str
    enabled: bool


@dataclass
class MeterList:
    """List of meters the device is connected to."""

    device_mac_id: bytes
    meter_mac_ids: List[bytes]


@dataclass
class NetworkInfo(ConnectionStatus):
    """Information about the network the device is on."""

    device_mac_id: bytes
    coord_mac_id: bytes
    status: ConnectionState
    description: str
    status_code: bytes
    ext_pan_id: bytes
    channel: int
    short_addr: bytes
    link_strength: int


@dataclass
class PriceCluster:
    """The current price in effect on the meter."""

    device_mac_id: bytes
    meter_mac_id: bytes
    time_stamp: datetime
    price: str
    currency: Currency
    tier: int
    tier_label: str
    rate_label: str
    # TODO(cottsay): Add 'Duration'


@dataclass
class ProfileData:
    """A series of interval data as recorded by the meter."""

    device_mac_id: bytes
    meter_mac_id: bytes
    end_time: datetime
    status: DataStatus
    profile_interval_period: IntervalPeriod


@dataclass
class ScheduleInfo:
    """Information about periodic notifications sent by the device."""

    device_mac_id: bytes
    meter_mac_id: bytes
    event: ScheduledEvent
    frequency: timedelta
    enabled: bool


@dataclass
class TimeCluster:
    """The current time reported on the meter."""

    device_mac_id: bytes
    meter_mac_id: bytes
    utc_time: datetime
    local_time: datetime
