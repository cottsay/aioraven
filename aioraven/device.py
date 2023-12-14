# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from datetime import datetime
from typing import Dict
from typing import Optional

from aioraven.data import ConnectionState
from aioraven.data import convert_bool
from aioraven.data import convert_currency
from aioraven.data import convert_date_code
from aioraven.data import convert_datetime
from aioraven.data import convert_float_formatted
from aioraven.data import convert_hex_to_bytes
from aioraven.data import convert_int
from aioraven.data import convert_price
from aioraven.data import convert_str
from aioraven.data import convert_timedelta
from aioraven.data import CurrentPeriodUsage
from aioraven.data import CurrentSummationDelivered
from aioraven.data import DataStatus
from aioraven.data import DeviceInfo
from aioraven.data import InstantaneousDemand
from aioraven.data import IntervalChannel
from aioraven.data import IntervalPeriod
from aioraven.data import LastPeriodUsage
from aioraven.data import MessageCluster
from aioraven.data import MessageQueue
from aioraven.data import MeterInfo
from aioraven.data import MeterList
from aioraven.data import MeterType
from aioraven.data import NetworkInfo
from aioraven.data import PriceCluster
from aioraven.data import ProfileData
from aioraven.data import RAVEnData
from aioraven.data import ScheduledEvent
from aioraven.data import ScheduleInfo
from aioraven.data import TimeCluster


class RAVEnError(IOError):
    """Base class for RAVEn related exceptions."""


class RAVEnConnectionError(RAVEnError):
    """Communication error with a RAVEn device."""


class RAVEnNotOpenError(RAVEnError):
    """The RAVEn device is not open."""


class RAVEnWarning(Warning):
    """The RAVEn device has generated a warning message."""

    def __init__(self, message: str) -> None:
        """
        Construct a RAVEnWarning.

        :param message: The reason for which the device is warning us.
        """
        super().__init__('Warning from RAVEn device: ' + message)


class UnknownRAVEnCommandWarning(RAVEnWarning):
    """A recently executed command is not supported by the RAVEn device."""

    MESSAGE = 'Unknown command'

    def __init__(self) -> None:
        """Construct a UnknownRAVEnCommandWarning."""
        super().__init__(self.MESSAGE)


class RAVEnBaseDevice:
    """RAVEn device command implementation."""

    async def _query(
        self,
        cmd_name: str,
        res_name: Optional[str] = None,
        args: Optional[Dict[str, str]] = None,
    ) -> Optional[RAVEnData]:
        raise NotImplementedError(
            "Derived class must implement '_query' function")

    async def close_current_period(
        self,
        meter: Optional[bytes] = None
    ) -> None:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        await self._query('close_current_period', None, args)

    async def confirm_message(
        self,
        msg_id: int,
        meter: Optional[bytes] = None,
    ) -> None:
        args = {
            'Id': f'0x{msg_id:08X}',
        }
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        await self._query('confirm_message', None, args)

    async def factory_reset(self) -> None:
        await self._query('factory_reset')

    async def get_current_period_usage(
        self,
        meter: Optional[bytes] = None,
    ) -> Optional[CurrentPeriodUsage]:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        raw = await self._query(
            'get_current_period_usage', 'CurrentPeriodUsage', args)
        if not raw:
            return None
        return CurrentPeriodUsage(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            time_stamp=convert_datetime(
                convert_str(raw.get('TimeStamp')), True),
            current_usage=convert_float_formatted(
                convert_str(raw.get('CurrentUsage')),
                convert_str(raw.get('Multiplier')),
                convert_str(raw.get('Divisor')),
                convert_str(raw.get('DigitsRight')),
                convert_str(raw.get('DigitsLeft')),
                convert_str(raw.get('SuppressLeadingZero'))),
            start_date=convert_datetime(
                convert_str(raw.get('StartDate')), True))

    async def get_current_price(
        self,
        *,
        meter: Optional[bytes] = None,
        refresh: Optional[bool] = None,
    ) -> Optional[PriceCluster]:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query('get_current_price', 'PriceCluster', args)
        if not raw:
            return None
        currency = convert_currency(convert_str(raw.get('Currency')))
        return PriceCluster(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            time_stamp=convert_datetime(
                convert_str(raw.get('TimeStamp')), True),
            price=convert_price(
                convert_str(raw.get('Price')),
                convert_str(raw.get('TrailingDigits')),
                currency.exponent if currency else None),
            currency=currency,
            tier=convert_int(convert_str(raw.get('Tier'))),
            tier_label=convert_str(raw.get('TierLabel')),
            rate_label=convert_str(raw.get('RateLabel')))

    async def get_current_summation_delivered(
        self,
        *,
        meter: Optional[bytes] = None,
        refresh: Optional[bool] = None,
    ) -> Optional[CurrentSummationDelivered]:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query(
            'get_current_summation_delivered', 'CurrentSummationDelivered',
            args)
        if not raw:
            return None
        return CurrentSummationDelivered(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            time_stamp=convert_datetime(
                convert_str(raw.get('TimeStamp')), True),
            summation_delivered=convert_float_formatted(
                convert_str(raw.get('SummationDelivered')),
                convert_str(raw.get('Multiplier')),
                convert_str(raw.get('Divisor')),
                convert_str(raw.get('DigitsRight')),
                convert_str(raw.get('DigitsLeft')),
                convert_str(raw.get('SuppressLeadingZero'))),
            summation_received=convert_float_formatted(
                convert_str(raw.get('SummationReceived')),
                convert_str(raw.get('Multiplier')),
                convert_str(raw.get('Divisor')),
                convert_str(raw.get('DigitsRight')),
                convert_str(raw.get('DigitsLeft')),
                convert_str(raw.get('SuppressLeadingZero'))))

    async def get_device_info(self) -> Optional[DeviceInfo]:
        raw = await self._query('get_device_info', 'DeviceInfo')
        if not raw:
            return None
        return DeviceInfo(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            install_code=convert_hex_to_bytes(
                convert_str(raw.get('InstallCode'))),
            link_key=convert_hex_to_bytes(
                convert_str(raw.get('LinkKey'))),
            fw_version=convert_str(raw.get('FWVersion')),
            hw_version=convert_str(raw.get('HWVersion')),
            image_type=convert_str(raw.get('ImageType')),
            manufacturer=convert_str(raw.get('Manufacturer')),
            model_id=convert_str(raw.get('ModelId')),
            date_code=convert_date_code(convert_str(raw.get('DateCode'))))

    async def get_instantaneous_demand(
        self,
        *,
        meter: Optional[bytes] = None,
        refresh: Optional[bool] = None,
    ) -> Optional[InstantaneousDemand]:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query(
            'get_instantaneous_demand', 'InstantaneousDemand', args)
        if not raw:
            return None
        return InstantaneousDemand(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            time_stamp=convert_datetime(
                convert_str(raw.get('TimeStamp')), True),
            demand=convert_float_formatted(
                convert_str(raw.get('Demand')),
                convert_str(raw.get('Multiplier')),
                convert_str(raw.get('Divisor')),
                convert_str(raw.get('DigitsRight')),
                convert_str(raw.get('DigitsLeft')),
                convert_str(raw.get('SuppressLeadingZero'))))

    async def get_last_period_usage(
        self,
        *,
        meter: Optional[bytes] = None,
    ) -> Optional[LastPeriodUsage]:
        # TODO(cottsay): This command has not been tested
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        raw = await self._query(
            'get_last_period_usage', 'LastPeriodUsage', args)
        if not raw:
            return None
        return LastPeriodUsage(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            last_usage=convert_float_formatted(
                convert_str(raw.get('LastUsage')),
                convert_str(raw.get('Multiplier')),
                convert_str(raw.get('Divisor')),
                convert_str(raw.get('DigitsRight')),
                convert_str(raw.get('DigitsLeft')),
                convert_str(raw.get('SuppressLeadingZero'))),
            start_date=convert_datetime(
                convert_str(raw.get('StartDate')), True),
            end_date=convert_datetime(
                convert_str(raw.get('EndDate')), True))

    async def get_message(
        self,
        *,
        meter: Optional[bytes] = None,
        refresh: Optional[bool] = None,
    ) -> Optional[MessageCluster]:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query('get_message', 'MessageCluster', args)
        if not raw:
            return None
        queue = convert_str(raw.get('Queue'))
        return MessageCluster(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            time_stamp=convert_datetime(
                convert_str(raw.get('TimeStamp')), True),
            message_id=convert_hex_to_bytes(
                convert_str(raw.get('Id'))),
            text=convert_str(
                convert_str(raw.get('Text'))),
            confirmation_required=convert_bool(
                convert_str(raw.get('ConfirmationRequired'))),
            confirmed=convert_bool(
                convert_str(raw.get('Confirmed'))),
            queue=MessageQueue(queue) if queue else None)

    async def get_meter_info(
        self,
        *,
        meter: Optional[bytes] = None,
    ) -> Optional[MeterInfo]:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        raw = await self._query('get_meter_info', 'MeterInfo', args)
        if not raw:
            return None
        # TODO(cottsay): Got unexpected numeric '0x0000' instead of 'electric'
        raw_type = convert_str(raw.get('MeterType'))
        return MeterInfo(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            meter_type=MeterType(raw_type) if raw_type else None,
            nick_name=convert_str(raw.get('NickName')),
            account=convert_str(raw.get('Account')),
            auth=convert_str(raw.get('Auth')),
            host=convert_str(raw.get('Host')),
            enabled=convert_bool(convert_str(raw.get('Enabled'))))

    async def get_meter_list(self) -> Optional[MeterList]:
        raw = await self._query('get_meter_list', 'MeterList')
        if not raw:
            return None
        raw_list = raw.get('MeterMacId') or []
        if not isinstance(raw_list, list):
            raw_list = [raw_list]
        converted_list = [convert_hex_to_bytes(m) for m in raw_list]
        return MeterList(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_ids=[m for m in converted_list if m is not None])

    async def get_network_info(self) -> Optional[NetworkInfo]:
        raw = await self._query('get_network_info', 'NetworkInfo')
        if not raw:
            return None
        status = convert_str(raw.get('Status'))
        return NetworkInfo(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            coord_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('CoordMacId'))),
            status=ConnectionState(status) if status else None,
            description=convert_str(raw.get('Description')),
            status_code=convert_hex_to_bytes(
                convert_str(raw.get('StatusCode'))),
            ext_pan_id=convert_hex_to_bytes(convert_str(raw.get('ExtPanId'))),
            channel=convert_int(convert_str(raw.get('Channel'))),
            short_addr=convert_hex_to_bytes(convert_str(raw.get('ShortAddr'))),
            link_strength=convert_int(convert_str(raw.get('LinkStrength'))))

    async def get_profile_data(
        self,
        count: int,
        end: datetime,
        channel: IntervalChannel,
        *,
        meter: Optional[bytes] = None,
    ) -> Optional[ProfileData]:
        # TODO(cottsay): This command has not been tested
        args = {
            'NumberOfPeriods': f'0x{count:02X}',
            'EndTime': str(end),
            'IntervalChannel': f'{channel}',
        }
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        raw = await self._query(
            'get_profile_data', 'ProfileData', args)
        if not raw:
            return None
        status = convert_int(convert_str(raw.get('Status')))
        period = convert_str(raw.get('ProfileIntervalPeriod'))
        return ProfileData(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            end_time=convert_datetime(
                convert_str(raw.get('EndTime')), True),
            status=DataStatus(status) if status is not None else None,
            profile_interval_period=IntervalPeriod(
                int(period)
            ) if period is not None else None)
        # TODO(cottsay): Get the IntervalData

    async def get_schedule(
        self,
        *,
        meter: Optional[bytes] = None,
        event: Optional[ScheduledEvent] = None,
    ) -> Optional[ScheduleInfo]:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        if event is not None:
            args['Event'] = str(event)
        raw = await self._query('get_schedule', 'ScheduleInfo', args)
        if not raw:
            return None
        scheduled_event = convert_str(raw.get('Event'))
        return ScheduleInfo(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            event=ScheduledEvent(scheduled_event) if scheduled_event else None,
            frequency=convert_timedelta(
                convert_str(raw.get('Frequency'))),
            enabled=convert_bool(
                convert_str(raw.get('Enabled'))))

    async def get_time(
        self,
        *,
        meter: Optional[bytes] = None,
        refresh: Optional[bool] = None,
    ) -> Optional[TimeCluster]:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query('get_time', 'TimeCluster', args)
        if not raw:
            return None
        return TimeCluster(
            device_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('DeviceMacId'))),
            meter_mac_id=convert_hex_to_bytes(
                convert_str(raw.get('MeterMacId'))),
            utc_time=convert_datetime(
                convert_str(raw.get('UTCTime')), True),
            local_time=convert_datetime(
                convert_str(raw.get('LocalTime'))))

    async def initialize(self) -> None:
        # TODO(cottsay): This command has not been tested
        await self._query('initialize')

    async def restart(self) -> None:
        await self._query('restart')

    async def set_current_price(
        self,
        price: float,
        *,
        meter: Optional[bytes] = None,
    ) -> None:
        args = {
            'Price': str(price),
            'TrailingDigits': str(0),
        }
        # TODO(cottsay): Handle TrailingDigits
        if meter is not None:
            args['MeterMacId'] = str(meter)
        await self._query('set_current_price', None, args)

    async def set_fast_poll(
        self,
        frequency: int,
        duration: int,
        *,
        meter: Optional[bytes] = None,
    ) -> None:
        args = {
            'Frequency': str(frequency),
            'Duration': str(duration),
        }
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        await self._query('set_fast_poll', None, args)

    async def set_meter_info(
        self,
        *,
        meter: Optional[bytes] = None,
        nick: Optional[str] = None,
        account: Optional[str] = None,
        auth: Optional[str] = None,
        host: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        if nick is not None:
            args['NickName'] = str(nick)
        if account is not None:
            args['Account'] = str(account)
        if auth is not None:
            args['Auth'] = str(auth)
        if host is not None:
            args['host'] = str(host)
        if enabled is not None:
            args['enabled'] = 'Y' if enabled else 'N'
        await self._query('set_meter_info', None, args)

    async def set_schedule(
        self,
        event: ScheduledEvent,
        frequency: int,
        enabled: bool,
        *,
        meter: Optional[bytes] = None,
    ) -> None:
        args = {
            'Event': str(event),
            'Frequency': str(frequency),
            'Enabled': 'Y' if enabled else 'N',
        }
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        await self._query('set_schedule', None, args)

    async def set_schedule_default(
        self,
        *,
        meter: Optional[bytes] = None,
        event: Optional[ScheduledEvent] = None,
    ) -> None:
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.hex().upper()}'
        if event is not None:
            args['Event'] = str(event)
        await self._query('set_schedule_default', None, args)
