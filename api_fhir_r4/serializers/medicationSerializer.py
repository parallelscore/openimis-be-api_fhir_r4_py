import copy
from medical.models import Item
from api_fhir_r4.converters import MedicationConverter
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.serializers import BaseFHIRSerializer


class MedicationSerializer(BaseFHIRSerializer):
    fhirConverter = MedicationConverter()

    def create(self, validated_data):
        code = validated_data.get('code')
        if Item.objects.filter(code=code).count() > 0:
            raise FHIRException('Exists medical item with following code `{}`'.format(code))
        copied_data = copy.deepcopy(validated_data)
        del copied_data['_state']
        return Item.objects.create(**copied_data)

    def update(self, instance, validated_data):
        instance.code = validated_data.get('code', instance.code)
        instance.name = validated_data.get('name', instance.name)
        instance.package = validated_data.get('package', instance.package)
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance
