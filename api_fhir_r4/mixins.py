import logging
from abc import abstractmethod, ABC
from typing import List

from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.http import Http404

from rest_framework import mixins
from api_fhir_r4.converters.containedResourceConverter import ContainedResourceConverter
from fhir.resources.fhirabstractmodel import FHIRAbstractModel

from api_fhir_r4.model_retrievers import GenericModelRetriever
from rest_framework.response import Response

from api_fhir_r4.multiserializer.mixins import MultiSerializerUpdateModelMixin, MultiSerializerRetrieveModelMixin

logger = logging.getLogger(__name__)


class ContainedContentSerializerMixin:
    """
    Mixin for extending BaseFHIRSerializer. The creation of a FHIR representation through to_representation is extended
    with a "contained" value. It contains model attributes mapped to FHIR through ContainedResourceConverters
    listed contained_resources. The contained values are added only if the 'contained'
    value in the serializer context is set to True.
    """

    #  Used for determining what reference type will be used used in contained value,
    # if None then value from ContainedResourceConverter is used

    @property
    def contained_resources(self) -> List[ContainedResourceConverter]:
        """ List of ContainedResourceConverter objects, used to determine which attributes will be contained.
        :return:
        """
        raise NotImplementedError('Serializer with contained resources require contained_resources implemented')

    def fhir_object_reference_fields(self, fhir_obj: FHIRAbstractModel) -> List[FHIRAbstractModel]:
        """
        When contained resources are used, the references in fhir object fields should
        change to the contained resource reference starting with hash.
        References for values listed in this property will be changed.
        :return: List of fields from fhir_objects with references, which have representation in contained resources
        """
        raise NotImplementedError('fhir_object_reference_fields not implemented')

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
        dict_list = [resource.dict() for resource in contained_resources]
        return dict_list

    def create_contained_resource_fhir_implementation(self, obj) -> List[FHIRAbstractModel]:
        contained_resources = []
        for resource, fhir_repr in self._get_converted_resources(obj):
            contained_resources.extend(fhir_repr)
        return contained_resources

    def _add_contained_references(self, fhir_obj: FHIRAbstractModel):
        for field in self.fhir_object_reference_fields(fhir_obj):
            field.reference = self._create_contained_reference(field.reference)

    def _create_contained_reference(self, base_reference):
        # Contained references are made by adding hash
        return F"#{base_reference}"


class GenericMultiIdentifierMixin(ABC):
    lookup_field = 'identifier'

    @property
    @abstractmethod
    def retrievers(self) -> List[GenericModelRetriever]:
        # Identifiers available for given resource
        pass

    def _get_object_with_first_valid_retriever(self, identifier):
        for retriever in self.retrievers:
            if retriever.identifier_validator(identifier):
                try:
                    queryset = retriever.retriever_additional_queryset_filtering(self.get_queryset())
                    resource = retriever.get_model_object(queryset, identifier)

                    # May raise a permission denied
                    self.check_object_permissions(self.request, resource)
                    return retriever.serializer_reference_type, resource
                except ObjectDoesNotExist as e:
                    logger.exception(
                        F"Failed to retrieve object from queryset {self.get_queryset()} using"
                        F"identifier {identifier} for matching retriever: {retriever}"
                    )

        # Raise Http404 if resource couldn't be fetched with any of the retrievers
        raise Http404(f"Resource for identifier {identifier} not found")


class MultiIdentifierRetrieverMixin(mixins.RetrieveModelMixin, GenericMultiIdentifierMixin, ABC):

    def retrieve(self, request, *args, **kwargs):
        ref_type, instance = self._get_object_with_first_valid_retriever(kwargs['identifier'])
        serializer = self.get_serializer(instance, reference_type=ref_type)
        return Response(serializer.data)


class MultiIdentifierUpdateMixin(mixins.UpdateModelMixin, GenericMultiIdentifierMixin, ABC):

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        ref_type, instance = self._get_object_with_first_valid_retriever(kwargs['identifier'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial, reference_type=ref_type)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class GenericMultiIdentifierForManySerializers(GenericMultiIdentifierMixin, ABC):

    def _get_object_with_first_valid_retriever(self, queryset, identifier):
        for retriever in self.retrievers:
            if retriever.identifier_validator(identifier):
                try:
                    queryset = retriever.retriever_additional_queryset_filtering(queryset)
                    resource = retriever.get_model_object(queryset, identifier)

                    # May raise a permission denied
                    self.check_object_permissions(self.request, resource)
                    return retriever.serializer_reference_type, resource
                except ObjectDoesNotExist:
                    logger.exception(
                        F"Failed to retrieve object from queryset {queryset} using"
                        F"identifier {identifier} for matching retriever: {retriever}"
                    )
                except FieldError:
                    logger.exception(F"Failed to retrieve object from queryset {queryset} using"
                                     F"{self.lookup_field}, field does not available for given model {queryset.model}")
        return None, None


class MultiIdentifierUpdateManySerializersMixin(MultiSerializerUpdateModelMixin,
                                                GenericMultiIdentifierForManySerializers, ABC):
    def update(self, request, *args, **kwargs):
        self._validate_update_request()
        partial = kwargs.pop('partial', False)
        results = []
        for serializer, (qs, _) in self.get_eligible_serializers_iterator():
            ref_type, instance = self._get_object_with_first_valid_retriever(qs, kwargs['identifier'])
            update_result = self._update_for_serializer(serializer, instance, request.data, partial,
                                                        reference_type=ref_type)
            results.append(update_result)

        response = results[0]  # By default there should be only one eligible serializer
        return Response(response)


class MultiIdentifierRetrieveManySerializersMixin(MultiSerializerRetrieveModelMixin,
                                                  GenericMultiIdentifierForManySerializers, ABC):
    def retrieve(self, request, *args, **kwargs):
        self._validate_retrieve_model_request()
        retrieved = []
        for serializer, (qs, _) in self.get_eligible_serializers_iterator():
            ref_type, instance = self._get_object_with_first_valid_retriever(qs, kwargs['identifier'])
            if instance:
                serializer = serializer(instance, reference_type=ref_type)
                if serializer.data:
                    retrieved.append(serializer.data)

        if len(retrieved) > 1:
            raise ValueError("Ambiguous retrieve result, object found for multiple serializers.")
        if len(retrieved) == 0:
            raise Http404(f"Resource for identifier {kwargs['identifier']} not found")

        return Response(retrieved[0])
