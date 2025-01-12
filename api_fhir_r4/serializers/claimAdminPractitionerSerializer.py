import copy
import uuid

from claim.models import ClaimAdmin
from claim.services import ClaimAdminService
# ClaimAdminService
from api_fhir_r4.converters import ClaimAdminPractitionerConverter
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.serializers import BaseFHIRSerializer


class ClaimAdminPractitionerSerializer(BaseFHIRSerializer):

    fhirConverter = ClaimAdminPractitionerConverter()

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        code = validated_data.get('code')

        if 'uuid' in validated_data.keys() and validated_data.get('uuid') is None:
            # In serializers using graphql services can't provide uuid. If uuid is provided then
            # resource is updated and not created. This check ensure UUID was provided.
            validated_data['uuid'] = uuid.uuid4()

        if ClaimAdmin.objects.filter(code=code).count() > 0:
            raise FHIRException(
                'Exists practitioner with following code `{}`'.format(code))
        copied_data = copy.deepcopy(validated_data)
        del copied_data['_state']

        return ClaimAdminService(user).create_or_update(copied_data, True)

        # return ClaimAdmin.objects.create(**copied_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user
        instance.code = validated_data.get('code', instance.code)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.other_names = validated_data.get(
            'other_names', instance.other_names)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email_id = validated_data.get('email_id', instance.email_id)
        instance.audit_user_id = self.get_audit_user_id()

        return ClaimAdminService(user).create_or_update(instance.__dict__)

        # instance.save()
        # return instance
