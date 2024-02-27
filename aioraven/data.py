# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from dataclasses import dataclass
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from enum import Enum
from enum import IntEnum
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from iso4217 import Currency


RAVEnDatum = Union[Optional[str], List[Optional[str]]]
RAVEnData = Dict[str, RAVEnDatum]


def convert_str(raw: RAVEnDatum) -> Optional[str]:
    if raw is not None:
        if isinstance(raw, str):
            return raw
        raise ValueError(f'Expected a single value but got {len(raw)}')
    return None


def convert_bool(raw: Optional[str]) -> Optional[bool]:
    if raw is not None:
        if raw == 'Y':
            return True
        elif raw == 'N':
            return False
        raise ValueError(f"Invalid boolean format: '{raw}'")
    return None


def convert_currency(raw: Optional[str]) -> Optional[Currency]:
    if raw is not None:
        number = int(raw, 0)
        for currency in Currency:
            if currency.number == number:
                return currency
        raise ValueError(f"Invalid currency number: '{raw}'")
    return None


def convert_date(raw: Optional[str]) -> Optional[date]:
    if raw is not None:
        if len(raw) >= 8:
            return date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))
        raise ValueError(f"Invalid date format: '{raw}'")
    return None


def convert_date_code(raw: Optional[str]) -> Optional[Tuple[date, str]]:
    if raw is not None:
        if len(raw) >= 9:
            date = convert_date(raw[:8])
            if date is not None:
                return (date, raw[8:])
            return None
        raise ValueError(f"Invalid date code format: '{raw}'")
    return None


def convert_datetime(
    raw: Optional[str],
    utc: bool = False
) -> Optional[datetime]:
    if raw is not None and raw != '0xffffff':
        value = datetime(
            2000, 1, 1, 0, 0,
            tzinfo=timezone.utc if utc else None)
        return value + timedelta(seconds=int(raw, 0))
    return None


def convert_float(
    raw_value: Optional[str],
    raw_div: Optional[str]
) -> Optional[float]:
    if raw_value is not None:
        value = float(int(raw_value, 0))
        if raw_div is not None:
            return value / 10.0 ** int(raw_div, 0)
        return value
    return None


def convert_float_formatted(
    raw: Optional[str],
    mult: Optional[str] = None,
    div: Optional[str] = None,
    digits_right: Optional[str] = None,
    digits_left: Optional[str] = None,
    suppress_leading_zero: Optional[str] = None,
) -> Optional[str]:
    value_int = convert_int(raw, sign_extend=True)
    if value_int is not None:
        value = float(value_int)
        if mult is not None:
            value *= int(mult, 0)
        if div is not None:
            value /= int(div, 0)
        whole, frac = str(value).split('.', 1)
        if whole.startswith('-'):
            sign = '-'
            whole = whole[1:]
        else:
            sign = ''
        if digits_right is not None:
            places = int(digits_right, 0)
            difference = len(frac) - places
            if difference > 0:
                frac = str((int(frac) + 5 ** difference) // 10 ** difference)
            elif difference < 0:
                frac += '0' * (-difference)
        if digits_left is not None:
            whole = format(whole, f'0>{int(digits_left, 0)}')
        if suppress_leading_zero is not None:
            if suppress_leading_zero == 'Y':
                whole = whole.lstrip('0')
                if not whole:
                    whole = '0'
        return f'{sign}{whole}.{frac}'
    return None


def convert_hex_to_bytes(raw: Optional[str]) -> Optional[bytes]:
    if raw is not None:
        if raw.startswith('0x'):
            raw = raw[2:]
        return bytes.fromhex(raw)
    return None


def convert_int(
    raw: Optional[str],
    *,
    sign_extend: bool = False,
) -> Optional[int]:
    if raw is not None:
        value = int(raw, 0)
        if sign_extend:
            value = (value & 0x7FFFFFFF) - (value & 0x80000000)
        return value
    return None


def convert_price(
    raw_value: Optional[str],
    raw_div: Optional[str],
    exponent: Optional[int],
) -> Optional[str]:
    value = str(convert_float(raw_value, raw_div))
    if value is not None and exponent is not None:
        major, minor = value.split('.', 1)
        if exponent == 0 and minor == '0':
            return major
        missing = exponent - len(minor)
        if missing > 0:
            value += '0' * missing
    return value


def convert_timedelta(raw: Optional[str]) -> Optional[timedelta]:
    if raw is not None:
        return timedelta(seconds=int(raw, 0))
    return None


class ConnectionState(str, Enum):
    """Indicates the current state of the device."""

    def __str__(self) -> str:
        return super().__str__()

    INITIALIZING = 'Initializing'
    NETWORK_DISCOVERY = 'Network Discovery'
    JOINING = 'Joining'
    JOIN_FAIL = 'Join: Fail'
    JOIN_SUCCESS = 'Join: Success'
    AUTHENTICATING = 'Authenticating'
    AUTHENTICATING_SUCCESS = 'Authenticating: Success'
    AUTHENTICATING_FAIL = 'Authenticating: Fail'
    CONNECTED = 'Connected'
    DISCONNECTED = 'Disconnected'
    REJOINING = 'Rejoining'


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

    def __str__(self) -> str:
        return super().__str__()

    DELIVERED = 'Delivered'
    RECEIVED = 'Received'


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

    def __str__(self) -> str:
        return super().__str__()

    ACTIVE = 'Active'
    CANCEL_PENDING = 'Cancel Pending'


class MeterType(str, Enum):
    """Types of meters to connect to."""

    def __str__(self) -> str:
        return super().__str__()

    ELECTRIC = 'electric'
    GAS = 'gas'
    WATER = 'water'
    OTHER = 'other'


class ScheduledEvent(str, Enum):
    """Types of events which can be scheduled."""

    def __str__(self) -> str:
        return super().__str__()

    TIME = 'time'
    PRICE = 'price'
    DEMAND = 'demand'
    SUMMATION = 'summation'
    MESSAGE = 'message'


@dataclass
class ConnectionStatus:
    """Diagnostic information about the meter connection."""

    device_mac_id: Optional[bytes]
    coord_mac_id: Optional[bytes]
    status: Optional[ConnectionState]
    description: Optional[str]
    status_code: Optional[bytes]
    ext_pan_id: Optional[bytes]
    channel: Optional[int]
    short_addr: Optional[bytes]
    link_strength: Optional[int]


@dataclass
class CurrentPeriodUsage:
    """Total consumption for current accumulation period."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    time_stamp: Optional[datetime]
    current_usage: Optional[str]
    start_date: Optional[datetime]


@dataclass
class CurrentSummationDelivered:
    """Total consumption at the meter to date."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    time_stamp: Optional[datetime]
    summation_delivered: Optional[str]
    summation_received: Optional[str]


@dataclass
class DeviceInfo:
    """Information about the device."""

    device_mac_id: Optional[bytes]
    install_code: Optional[bytes]
    link_key: Optional[bytes]
    fw_version: Optional[str]
    hw_version: Optional[str]
    image_type: Optional[str]
    manufacturer: Optional[str]
    model_id: Optional[str]
    date_code: Optional[Tuple[date, str]]


@dataclass
class InstantaneousDemand:
    """Current consumption rate at the meter."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    time_stamp: Optional[datetime]
    demand: Optional[str]


@dataclass
class LastPeriodUsage:
    """Total consumption for the previous accumulation period."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    last_usage: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]


@dataclass
class MessageCluster:
    """Text messages from the meter."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    time_stamp: Optional[datetime]
    message_id: Optional[bytes]
    text: Optional[str]
    confirmation_required: Optional[bool]
    confirmed: Optional[bool]
    queue: Optional[MessageQueue]


@dataclass
class MeterInfo:
    """Information about a meter on the network."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    meter_type: Optional[MeterType]
    nick_name: Optional[str]
    account: Optional[str]
    auth: Optional[str]
    host: Optional[str]
    enabled: Optional[bool]


@dataclass
class MeterList:
    """List of meters the device is connected to."""

    device_mac_id: Optional[bytes]
    meter_mac_ids: Optional[List[bytes]]


@dataclass
class NetworkInfo(ConnectionStatus):
    """Information about the network the device is on."""

    device_mac_id: Optional[bytes]
    coord_mac_id: Optional[bytes]
    status: Optional[ConnectionState]
    description: Optional[str]
    status_code: Optional[bytes]
    ext_pan_id: Optional[bytes]
    channel: Optional[int]
    short_addr: Optional[bytes]
    link_strength: Optional[int]


@dataclass
class PriceCluster:
    """The current price in effect on the meter."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    time_stamp: Optional[datetime]
    price: Optional[str]
    currency: Optional[Currency]
    tier: Optional[int]
    tier_label: Optional[str]
    rate_label: Optional[str]
    # TODO(cottsay): Add 'Duration'


@dataclass
class ProfileData:
    """A series of interval data as recorded by the meter."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    end_time: Optional[datetime]
    status: Optional[DataStatus]
    profile_interval_period: Optional[IntervalPeriod]


@dataclass
class ScheduleInfo:
    """Information about periodic notifications sent by the device."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    event: Optional[ScheduledEvent]
    frequency: Optional[timedelta]
    enabled: Optional[bool]


@dataclass
class TimeCluster:
    """The current time reported on the meter."""

    device_mac_id: Optional[bytes]
    meter_mac_id: Optional[bytes]
    utc_time: Optional[datetime]
    local_time: Optional[datetime]
