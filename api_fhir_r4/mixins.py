from rest_framework import mixins
from django.db.models import Manager
from typing import List

from api_fhir_r4.converters.containedResourceConverter import ContainedResourceConverter
from api_fhir_r4.models import Resource, FHIRBaseObject


class ContainedContentSerializerMixin:
    """
    Mixin for extending BaseFHIRSerializer. The creation of a FHIR representation through to_representation is extended
    with a "contained" value. It contains model attributes mapped to FHIR through ContainedResourceConverters
    listed contained_resources. The contained values are added only if the 'contained'
    value in the serializer context is set to True.
    """

    @property
    def contained_resources(self) -> List[ContainedResourceConverter]:
        """ List of ContainedResourceConverter objects, used to determine which attributes will be contained.
        :return:
        """
        raise NotImplementedError('Serializer with contained resources require contained_resources implemented')

    def _get_converted_resources(self, obj):
        converted_values = []
        for resource in self.contained_resources:
            resource_fhir_repr = resource.convert_from_source(obj)
            converted_values.append((resource, resource_fhir_repr))
        return converted_values

    def to_representation(self, obj):
        base_fhir_obj_repr = super(ContainedContentSerializerMixin, self).to_representation(obj)
        if self.context.get('contained', False):
            base_fhir_obj_repr['contained'] = self._create_contained_obj_dict(obj)
        return base_fhir_obj_repr

    def _create_contained_obj_dict(self, obj):
        contained_resources = self.create_contained_resource_fhir_implementation(obj)
        return [resource.toDict() for resource in contained_resources]

    def create_contained_resource_fhir_implementation(self, obj) -> List[FHIRBaseObject]:
        contained_resources = []
        for resource, fhir_repr in self._get_converted_resources(obj):
            contained_resources.extend(fhir_repr)
        return contained_resources
