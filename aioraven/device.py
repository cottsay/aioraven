# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from aioraven.data import ConnectionState
from aioraven.data import convert_bool
from aioraven.data import convert_currency
from aioraven.data import convert_date_code
from aioraven.data import convert_datetime
from aioraven.data import convert_float
from aioraven.data import convert_hex_to_bytes
from aioraven.data import convert_int
from aioraven.data import convert_int_formatted
from aioraven.data import convert_timedelta
from aioraven.data import CurrentPeriodUsage
from aioraven.data import CurrentSummationDelivered
from aioraven.data import DataStatus
from aioraven.data import DeviceInfo
from aioraven.data import InstantaneousDemand
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
from aioraven.data import ScheduledEvent
from aioraven.data import ScheduleInfo
from aioraven.data import TimeCluster


class RAVEnBaseDevice:

    async def _query(self, cmd_name, res_name=None, args=None):
        raise NotImplementedError(
            "Derived class must implement '_query' function")

    async def close_current_period(self, meter=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter:016X}'
        return await self._query('close_current_period', None, args)

    async def confirm_message(self, msg_id, meter=None):
        args = {
            'Id': '0x{msg_id:08X}',
        }
        if meter is not None:
            args['MeterMacId'] = f'0x{meter:016X}'
        return await self._query('confirm_message', None, args)

    async def factory_reset(self):
        return await self._query('factory_reset')

    async def get_current_period_usage(self, meter=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter.decode().upper():016s}'
        raw = await self._query(
            'get_current_period_usage', 'CurrentPeriodUsage', args)
        if not raw:
            return None
        return CurrentPeriodUsage(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            time_stamp=convert_datetime(raw.get('TimeStamp'), True),
            current_usage=convert_int_formatted(
                raw.get('CurrentUsage'),
                raw.get('Multiplier'),
                raw.get('Divisor'),
                raw.get('DigitsRight'),
                raw.get('DigitsLeft'),
                raw.get('SuppressLeadingZero')),
            start_date=convert_datetime(raw.get('StartDate'), True))

    async def get_current_price(self, *, meter=None, refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter:016X}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query('get_current_price', 'PriceCluster', args)
        if not raw:
            return None
        return PriceCluster(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            time_stamp=convert_datetime(raw.get('TimeStamp'), True),
            price=convert_float(raw.get('Price'), raw.get('TrailingDigits')),
            currency=convert_currency(raw.get('Currency')),
            tier=convert_int(raw.get('Tier')),
            tier_label=raw.get('TierLabel'),
            rate_label=raw.get('RateLabel'))

    async def get_current_summation_delivered(self, *, meter=None,
                                              refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = '0x{meter:016X}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query(
            'get_current_summation_delivered', 'CurrentSummationDelivered',
            args)
        if not raw:
            return None
        return CurrentSummationDelivered(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            time_stamp=convert_datetime(raw.get('TimeStamp'), True),
            summation_delivered=convert_int_formatted(
                raw.get('SummationDelivered'),
                raw.get('Multiplier'),
                raw.get('Divisor'),
                raw.get('DigitsRight'),
                raw.get('DigitsLeft'),
                raw.get('SuppressLeadingZero')),
            summation_received=convert_int_formatted(
                raw.get('SummationReceived'),
                raw.get('Multiplier'),
                raw.get('Divisor'),
                raw.get('DigitsRight'),
                raw.get('DigitsLeft'),
                raw.get('SuppressLeadingZero')))

    async def get_device_info(self):
        raw = await self._query('get_device_info', 'DeviceInfo')
        if not raw:
            return None
        return DeviceInfo(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            install_code=convert_hex_to_bytes(raw.get('InstallCode')),
            link_key=convert_hex_to_bytes(raw.get('LinkKey')),
            fw_version=raw.get('FWVersion'),
            hw_version=raw.get('HWVersion'),
            image_type=raw.get('ImageType'),
            manufacturer=raw.get('Manufacturer'),
            model_id=raw.get('ModelId'),
            date_code=convert_date_code(raw.get('DateCode')))

    async def get_instantaneous_demand(self, *, meter=None, refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = '0x{meter:016X}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query(
            'get_instantaneous_demand', 'InstantaneousDemand', args)
        if not raw:
            return None
        return InstantaneousDemand(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            time_stamp=convert_datetime(raw.get('TimeStamp'), True),
            demand=convert_int_formatted(
                raw.get('Demand'),
                raw.get('Multiplier'),
                raw.get('Divisor'),
                raw.get('DigitsRight'),
                raw.get('DigitsLeft'),
                raw.get('SuppressLeadingZero')))

    async def get_last_period_usage(self, *, meter=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = '0x{meter:016X}'
        raw = await self._query(
            'get_last_period_usage', 'LastPeriodUsage', args)
        if not raw:
            return None
        return LastPeriodUsage(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            last_usage=convert_int_formatted(
                raw.get('LastUsage'),
                raw.get('Multiplier'),
                raw.get('Divisor'),
                raw.get('DigitsRight'),
                raw.get('DigitsLeft'),
                raw.get('SuppressLeadingZero')),
            start_date=convert_datetime(raw.get('StartDate'), True),
            end_date=convert_datetime(raw.get('EndDate'), True))

    async def get_message(self, *, meter=None, refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = '0x{meter:016X}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query('get_message', 'MessageCluster', args)
        if not raw:
            return
        queue = raw.get('Queue')
        return MessageCluster(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            time_stamp=convert_datetime(raw.get('TimeStamp'), True),
            message_id=convert_hex_to_bytes(raw.get('Id')),
            text=raw.get('Text'),
            confirmation_required=convert_bool(
                raw.get('ConfirmationRequired')),
            confirmed=convert_bool(raw.get('Confirmed')),
            queue=MessageQueue(queue) if queue else None)

    async def get_meter_info(self, *, meter=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter:016X}'
        raw = await self._query('get_meter_info', 'MeterInfo', args)
        if not raw:
            return None
        raw_type = raw.get('MeterType')
        return MeterInfo(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            meter_type=MeterType(raw_type) if raw_type else None,
            nick_name=raw.get('NickName'),
            account=raw.get('Account'),
            auth=raw.get('Auth'),
            host=raw.get('Host'),
            enabled=convert_bool(raw.get('Enabled')))

    async def get_meter_list(self):
        raw = await self._query('get_meter_list', 'MeterList')
        if not raw:
            return None
        raw_list = raw.get('MeterMacId') or []
        if not isinstance(raw_list, list):
            raw_list = [raw_list]
        return MeterList(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_ids=[convert_hex_to_bytes(m) for m in raw_list])

    async def get_network_info(self):
        raw = await self._query('get_network_info', 'NetworkInfo')
        if not raw:
            return raw
        status = raw.get('Status')
        return NetworkInfo(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            coord_mac_id=convert_hex_to_bytes(raw.get('CoordMacId')),
            status=ConnectionState(status) if status else None,
            description=raw.get('Description'),
            status_code=convert_hex_to_bytes(raw.get('StatusCode')),
            ext_pan_id=convert_hex_to_bytes(raw.get('ExtPanId')),
            channel=convert_int(raw.get('Channel')),
            short_addr=convert_hex_to_bytes(raw.get('ShortAddr')),
            link_strength=convert_int(raw.get('LinkStrength')))

    async def get_profile_data(self, count, end, channel, *, meter=None):
        args = {
            'NumberOfPeriods': f'0x{count:02X}',
            'EndTime': str(end),
            'IntervalChannel': f'{channel}',
        }
        if meter is not None:
            args['MeterMacId'] = f'0x{meter:016X}'
        raw = await self._query(
            'get_profile_data', 'ProfileData', args)
        if not raw:
            return raw
        status = convert_int(raw.get('Status'))
        period = raw.get('ProfileIntervalPeriod')
        return ProfileData(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            end_time=convert_datetime(raw.get('EndTime'), True),
            status=DataStatus(status) if status is not None else None,
            profile_interval_period=IntervalPeriod(
                int(period)
            ) if period is not None else None)
        # TODO(cottsay): Get the IntervalData

    async def get_schedule(self, *, meter=None, event=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter:016X}'
        if event is not None:
            args['Event'] = str(event)
        raw = await self._query('get_schedule', 'ScheduleInfo', args)
        if not raw:
            return raw
        event = raw.get('Event')
        return ScheduleInfo(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            event=ScheduledEvent(event) if event else None,
            frequency=convert_timedelta(raw.get('Frequency')),
            enabled=convert_bool(raw.get('Enabled')))

    async def get_time(self, *, meter=None, refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = f'0x{meter:016X}'
        if refresh is not None:
            args['Refresh'] = 'Y' if refresh else 'N'
        raw = await self._query('get_time', 'TimeCluster', args)
        if not raw:
            return None
        return TimeCluster(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            utc_time=convert_datetime(raw.get('UTCTime'), True),
            local_time=convert_datetime(raw.get('LocalTime')))

    async def initialize(self):
        return await self._query('initialize')

    async def restart(self):
        return await self._query('restart')

    async def set_current_price(self, price, meter=None):
        args = {
            'Price': str(price),
            'TrailingDigits': str(0),
        }
        if meter is not None:
            args['MeterMacId'] = str(meter)
        return await self._query('set_current_price', None, args)

    async def set_fast_poll(self, frequency, duration, meter=None):
        args = {
            'Frequency': str(frequency),
            'Duration': str(duration),
        }
        if meter is not None:
            args['MeterMacId'] = '0x{meter:016X}'
        return await self._query('set_fast_poll', None, args)

    async def set_meter_info(self, meter=None, nick=None, account=None,
                             auth=None, host=None, enabled=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = '0x{meter:016X}'
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
        return await self._query('set_meter_info', None, args)

    async def set_schedule(self, event, frequency, enabled, meter=None):
        args = {
            'Event': str(event),
            'Frequency': str(frequency),
            'Enabled': 'Y' if enabled else 'N',
        }
        if meter is not None:
            args['MeterMacId'] = '0x{meter:016X}'
        return await self._query('set_schedule', None, args)

    async def set_schedule_default(self, meter=None, event=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = '0x{meter:016X}'
        if event is not None:
            args['Event'] = str(event)
        return await self._query('set_schedule_default', None, args)
