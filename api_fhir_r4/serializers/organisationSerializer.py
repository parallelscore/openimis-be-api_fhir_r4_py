import copy
from policyholder.models import PolicyHolder
from api_fhir_r4.converters import OrganisationConverter
from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.serializers import BaseFHIRSerializer


class OrganisationSerializer(BaseFHIRSerializer):
    fhirConverter = OrganisationConverter()
    def create(self,validated_data):
        if PolicyHolder.objects.filter(code=validated_data['code']).count() > 0:
            raise FHIRException('Exists Organisation with following code `{}`'.format(validated_data['code']))
        validated_data.pop('_original_state')
        validated_data.pop('_state')
        request = self.context.get('request', None)
        if request:
            validated_data['user_created_id']=request.user.id
            validated_data['user_updated_id']=request.user.id
        obj=PolicyHolder()
        obj.user_updated=request.user
        obj.user_created=request.user
        obj.trade_name =validated_data['trade_name']
        obj.date_created=validated_data['date_created']
        obj.date_updated=validated_data['date_updated']
        obj.address = validated_data['address']
        obj.code = validated_data['code']
        obj.email = validated_data['email']
        obj.phone = validated_data['phone']
        obj.fax = validated_data['fax']
        obj.legal_form= validated_data['legal_form']
        obj.save()
        return obj

    def update(self, instance, validated_data):
        request = self.context.get('request', None)
        if request:
            validated_data['user_updated_id']=request.user.id
        instance.legal_form = validated_data.get('legal_form', instance.legal_form)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.fax = validated_data.get('fax', instance.fax)
        instance.trade_name = validated_data.get('trade_name', instance.trade_name)
        instance.address = validated_data.get('address', instance.address)
        instance.user_updated_id = validated_data.get('user_updated_id', instance.user_updated_id)
        instance.save()
        return instance