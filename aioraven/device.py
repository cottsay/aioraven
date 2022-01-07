# Copyright 2022 Scott K Logan
# Licensed under the Apache License, Version 2.0

from aioraven.data import convert_currency
from aioraven.data import convert_date_code
from aioraven.data import convert_datetime
from aioraven.data import convert_float
from aioraven.data import convert_hex_to_bytes
from aioraven.data import convert_int
from aioraven.data import DeviceInfo
from aioraven.data import PriceCluster


class RAVEnBaseDevice:

    async def _query(self, cmd_name, res_name=None, args=None):
        raise NotImplementedError(
            "Derived class must implement '_query' function")

    async def close_current_period(self, meter=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        return await self._query('close_current_period', None, args)

    async def confirm_message(self, msg_id, meter=None):
        args = {
            'Id': str(msg_id),
        }
        if meter is not None:
            args['MeterMacId'] = str(meter)
        return await self._query('confirm_message', None, args)

    async def factory_reset(self):
        return await self._query('factory_reset')

    async def get_current_period_usage(self, meter=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        return await self._query(
            'get_current_period_usage', 'CurrentPeriodUsage', args)

    async def get_current_summation_delivered(self, *, meter=None,
                                              refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        if refresh is not None:
            args['Refresh'] = str(refresh)
        return await self._query(
            'get_current_summation_delivered', 'CurrentSummationDelivered',
            args)

    async def get_current_price(self, *, meter=None, refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        if refresh is not None:
            args['Refresh'] = str(refresh)
        raw = await self._query('get_current_price', 'PriceCluster', args)
        return PriceCluster(
            device_mac_id=convert_hex_to_bytes(raw.get('DeviceMacId')),
            meter_mac_id=convert_hex_to_bytes(raw.get('MeterMacId')),
            time_stamp=convert_datetime(raw.get('TimeStamp'), True),
            price=convert_float(raw.get('Price'), raw.get('TrailingDigits')),
            currency=convert_currency(raw.get('Currency')),
            tier=convert_int(raw.get('Tier')),
            tier_label=raw.get('TierLabel'),
            rate_label=raw.get('RateLabel'))

    async def get_device_info(self):
        raw = await self._query('get_device_info', 'DeviceInfo')
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
            args['MeterMacId'] = str(meter)
        if refresh is not None:
            args['Refresh'] = str(refresh)
        return await self._query(
            'get_instantaneous_demand', 'InstantaneousDemand', args)

    async def get_last_period_usage(self, *, meter=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        return await self._query(
            'get_last_period_usage', 'LastPeriodUsage', args)

    async def get_message(self, *, meter=None, refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        if refresh is not None:
            args['Refresh'] = str(refresh)
        return await self._query('get_message', 'MessageCluster', args)

    async def get_meter_info(self, *, meter=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        return await self._query('get_meter_info', 'MeterInfo', args)

    async def get_meter_list(self):
        return await self._query('get_meter_list', 'MeterList')

    async def get_network_info(self):
        return await self._query('get_network_info', 'NetworkInfo')

    async def get_profile_data(self, count, end, channel, *, meter=None):
        args = {
            'NumberOfPeriods': str(count),
            'EndTime': str(end),
            'IntervalChannel': str(channel),
        }
        if meter is not None:
            args['MeterMacId'] = str(meter)
        return await self._query(
            'get_profile_data', 'ProfileData', args)

    async def get_schedule(self, *, meter=None, event=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        if event is not None:
            args['Event'] = str(event)
        return await self._query('get_schedule', 'ScheduleInfo', args)

    async def get_time(self, *, meter=None, refresh=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        if refresh is not None:
            args['Refresh'] = str(refresh)
        return await self._query('get_time', 'TimeCluster', args)

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
            args['MeterMacId'] = str(meter)
        return await self._query('set_fast_poll', None, args)

    async def set_meter_info(self, meter=None, nick=None, account=None,
                             auth=None, host=None, enabled=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        if nick is not None:
            args['NickName'] = str(nick)
        if account is not None:
            args['Account'] = str(account)
        if auth is not None:
            args['Auth'] = str(auth)
        if host is not None:
            args['host'] = str(host)
        if enabled is not None:
            args['enabled'] = str(enabled)
        return await self._query('set_meter_info', None, args)

    async def set_schedule(self, event, frequency, enabled, meter=None):
        args = {
            'Event': str(event),
            'Frequency': str(frequency),
            'Enabled': str(enabled),
        }
        if meter is not None:
            args['MeterMacId'] = str(meter)
        return await self._query('set_schedule', None, args)

    async def set_schedule_default(self, meter=None, event=None):
        args = {}
        if meter is not None:
            args['MeterMacId'] = str(meter)
        if event is not None:
            args['Event'] = str(event)
        return await self._query('set_schedule_default', None, args)
