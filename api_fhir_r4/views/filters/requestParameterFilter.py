from abc import ABC
from datetime import timedelta

from api_fhir_r4.utils import TimeUtils
from core.datetimes.ad_datetime import datetime


class QuerysetFilterABC(ABC):
    def __init__(self, parameter, value):
        self.parameter = parameter
        self.value = value

    def apply_filter(self, queryset):
        raise NotImplemented('apply_filter() not implemented')


class QuerysetEqualFilter(QuerysetFilterABC):
    def apply_filter(self, queryset):
        return queryset.filter(**{self.parameter: self.value})


class QuerysetNotEqualFilter(QuerysetFilterABC):
    def apply_filter(self, queryset):
        return queryset.exclude(**{self.parameter: self.value})


class QuerysetGreaterThanFilter(QuerysetFilterABC):
    def apply_filter(self, queryset):
        return queryset.filter(**{f'{self.parameter}__gt': self.value})


class QuerysetLesserThanFilter(QuerysetFilterABC):
    def apply_filter(self, queryset):
        return queryset.filter(**{f'{self.parameter}__lt': self.value})


class QuerysetGreaterThanEqualFilter(QuerysetFilterABC):
    def apply_filter(self, queryset):
        return queryset.filter(**{f'{self.parameter}__gte': self.value})


class QuerysetLesserThanEqualFilter(QuerysetFilterABC):
    def apply_filter(self, queryset):
        return queryset.filter(**{f'{self.parameter}__lte': self.value})


class QuerysetApproximateDateFilter(QuerysetFilterABC):
    def apply_filter(self, queryset):
        range_size = (TimeUtils.now() - self.value).days * 0.1
        value_start = self.value - timedelta(days=range_size)
        value_end = self.value + timedelta(days=range_size)
        return queryset.filter(**{f'{self.parameter}__range': (value_start, value_end)})


class QuerysetParameterABC(ABC):
    def __init__(self, output_parameter):
        self.output_parameter = output_parameter
        self.accepted_prefixes = self._get_prefix_filter_mapping().keys()

    def _get_prefix_filter_mapping(self):
        raise NotImplemented('_get_modifier_filter_mapping() not implemented')

    def build_filter(self, request_parameter_value):
        modifier, value = self._get_prefix_and_value(request_parameter_value)
        return self._get_prefix_filter_mapping()[modifier if modifier else 'eq'](self.output_parameter, value)

    def _get_prefix_and_value(self, parameter):
        modifier = next((modifier for modifier in self.accepted_prefixes if parameter.startswith(modifier)), '')
        output_value = self._parse_value(parameter[len(modifier):])
        return modifier, output_value

    def _parse_value(self, value):
        return value


class QuerysetLastUpdatedParameter(QuerysetParameterABC):
    def _get_prefix_filter_mapping(self):
        return {
            'eq': lambda param, value: QuerysetEqualFilter(param, value),
            'ne': lambda param, value: QuerysetNotEqualFilter(param, value),
            'gt': lambda param, value: QuerysetGreaterThanFilter(param, value),
            'lt': lambda param, value: QuerysetLesserThanFilter(param, value),
            'ge': lambda param, value: QuerysetGreaterThanEqualFilter(param, value),
            'le': lambda param, value: QuerysetLesserThanEqualFilter(param, value),
            'sa': lambda param, value: QuerysetGreaterThanEqualFilter(param, value),
            'eb': lambda param, value: QuerysetLesserThanEqualFilter(param, value),
            'ap': lambda param, value: QuerysetApproximateDateFilter(param, value)
        }

    def _parse_value(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            raise ValueError('{request_parameter} value is not a valid datetime')


class RequestParameterFilterABC(ABC):
    def __init__(self, request):
        self.request = request

    def _get_parameter_mapping(self):
        raise NotImplemented('_get_parameter_mapping() not implemented')

    def filter_queryset(self, queryset):
        parameter_mapping = self._get_parameter_mapping()
        accepted_parameters = parameter_mapping.keys()
        request_parameters = {parameter: self.request.GET[parameter]
                              for parameter in accepted_parameters if parameter in self.request.GET}

        output_queryset = queryset
        for request_parameter in request_parameters:
            output_parameter = self._get_parameter_mapping()[request_parameter]()
            try:
                output_queryset = output_parameter.build_filter(self.request.GET[request_parameter]).apply_filter(
                    output_queryset)
            except ValueError as parsingError:
                raise ValueError(str(parsingError).format(**{'request_parameter': request_parameter}))

        return output_queryset


class ValidityFromRequestParameterFilter(RequestParameterFilterABC):
    def _get_parameter_mapping(self):
        return {
            '_lastUpdated': lambda: QuerysetLastUpdatedParameter('validity_from'),
        }


class DateUpdatedRequestParameterFilter(RequestParameterFilterABC):
    def _get_parameter_mapping(self):
        return {
            '_lastUpdated': lambda: QuerysetLastUpdatedParameter('date_updated'),
        }
