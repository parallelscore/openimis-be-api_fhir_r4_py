import copy

from product.models import Product
from api_fhir_r4.converters import InsurancePlanConverter
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.serializers import BaseFHIRSerializer


class InsurancePlanSerializer(BaseFHIRSerializer):
    fhirConverter = InsurancePlanConverter()

    def create(self, validated_data):
        code = validated_data.get('code')
        if Product.objects.filter(code=code).count() > 0:
            raise FHIRException('Exists product with following code `{}`'.format(code))
        copied_data = copy.deepcopy(validated_data)
        del copied_data['_state']
        # TODO services in product hasn't been developed yet.
        return Product.objects.create(**copied_data)

    def update(self, instance, validated_data):
        pass
