import uuid
from abc import ABC, abstractmethod, abstractproperty
from typing import Union

from django.db.models.query import QuerySet
from django.db.models import Model

from api_fhir_r4.converters import ReferenceConverterMixin


class GenericModelRetriever(ABC):

    @property
    @abstractmethod
    def identifier_field(self) -> str:
        pass

    @property
    @abstractmethod
    def serializer_reference_type(self) -> Union[
        ReferenceConverterMixin.UUID_REFERENCE_TYPE,
        ReferenceConverterMixin.CODE_REFERENCE_TYPE,
        ReferenceConverterMixin.DB_ID_REFERENCE_TYPE
    ]:
        pass

    #ReferenceConverterMixin.UUID_REFERENCE_TYPE
    @classmethod
    @abstractmethod
    def identifier_validator(cls, identifier_value) -> bool:
        pass

    @classmethod
    def get_model_object(cls, queryset: QuerySet, identifier_value) -> Model:
        return queryset.get(**{cls.identifier_field: identifier_value})


class UUIDIdentifierModelRetriever(GenericModelRetriever):
    identifier_field = 'uuid'
    serializer_reference_type = ReferenceConverterMixin.UUID_REFERENCE_TYPE

    @classmethod
    def identifier_validator(cls, identifier_value):
        return cls._is_uuid_identifier(identifier_value)

    @classmethod
    def _is_uuid_identifier(cls, identifier):
        try:
            uuid.UUID(str(identifier))
            return True
        except ValueError:
            return False


class CodeIdentifierModelRetriever(GenericModelRetriever):
    identifier_field = 'code'
    serializer_reference_type = ReferenceConverterMixin.CODE_REFERENCE_TYPE

    @classmethod
    def identifier_validator(cls, identifier_value):
        return isinstance(identifier_value, str)


class CHFIdentifierModelRetriever(GenericModelRetriever):
    identifier_field = 'chf_id'
    serializer_reference_type = ReferenceConverterMixin.CODE_REFERENCE_TYPE

    @classmethod
    def identifier_validator(cls, identifier_value):
        # From model specification
        return isinstance(identifier_value, str) and len(identifier_value) <= 12


