from api_fhir_r4.converters import CodeSystemConverter
from api_fhir_r4.serializers import BaseFHIRSerializer


class CodeSystemSerializer(BaseFHIRSerializer):

    fhirConverter = CodeSystemConverter

    def __init__(self, *args, **kwargs):
        self.model_name = kwargs.pop('model_name')
        self.code_field = kwargs.pop('code_field')
        self.display_field = kwargs.pop('display_field')
        self.id = kwargs.pop('id')
        self.name = kwargs.pop('name')
        self.title = kwargs.pop('title')
        self.description = kwargs.pop('description')
        self.url = kwargs.pop('url')
        super().__init__(*args, **kwargs)

    def to_representation(self, obj):
        return CodeSystemConverter.to_fhir_obj(
            self.model_name,
            self.code_field,
            self.display_field,
            self.id,
            self.name,
            self.title,
            self.description,
            self.url
        ).dict()
