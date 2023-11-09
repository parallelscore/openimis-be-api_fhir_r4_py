import copy

from location.models import Location

from api_fhir_r4.converters import LocationConverter
from api_fhir_r4.serializers import BaseFHIRSerializer
from location.services import LocationService


class LocationSerializer(BaseFHIRSerializer):
    fhirConverter = LocationConverter()

    def create(self, validated_data):
        
        request = self.context.get("request")
        user = request.user
        
        copied_data = copy.deepcopy(validated_data)
        del copied_data['_state']
        del copied_data['uuid']
        
        copied_data["audit_user_id"] = self.get_audit_user_id()
        # print(copied_data)
        # return Location.objects.create(**copied_data)
        return LocationService(user).update_or_create(copied_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user
        
        instance.code = validated_data.get('code', instance.code)
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.parent_id = validated_data.get('parent_id', instance.parent_id)
        instance.audit_user_id = self.get_audit_user_id()
        return LocationService(user).update_or_create(instance.__dict__)
        # instance.save()
        # return instance
