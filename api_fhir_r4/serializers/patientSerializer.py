import copy

from insuree.apps import InsureeConfig
from insuree.models import Insuree, Gender, Education, Profession, Family, InsureePhoto
from insuree.gql_mutations import update_or_create_insuree, create_file

from api_fhir_r4.converters import PatientConverter
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.serializers import BaseFHIRSerializer


class PatientSerializer(BaseFHIRSerializer):
    fhirConverter = PatientConverter()

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        chf_id = validated_data.get('chf_id')
        if Insuree.objects.filter(chf_id=chf_id).count() > 0:
            raise FHIRException('Exists patient with following chfid `{}`'.format(chf_id))
        copied_data = copy.deepcopy(validated_data)
        del copied_data['_state']
        obj = update_or_create_insuree(copied_data, user)
        # create photo as a file to specified configured path
        if InsureeConfig.insuree_photos_root_path:
            create_file(date=obj.photo.date, insuree_id=obj.id, photo_bin=obj.photo.photo)
        if copied_data['head']:
            obj.family = Family.objects.create(head_insuree=obj, audit_user_id=copied_data['audit_user_id'])
            obj.save()
        return obj

    def update(self, instance, validated_data):
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.other_names = validated_data.get('other_names', instance.other_names)
        instance.passport = validated_data.get('passport', instance.passport)
        instance.dob = validated_data.get('dob', instance.dob)
        gender_code = validated_data.get('gender_id', instance.gender.code)
        instance.gender = Gender.objects.get(pk=gender_code)
        instance.marital = validated_data.get('marital', instance.marital)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.current_address = validated_data.get('current_address', instance.current_address)
        instance.geolocation = validated_data.get('geolocation', instance.geolocation)
        instance.audit_user_id = self.get_audit_user_id()
        instance.save()
        return instance
