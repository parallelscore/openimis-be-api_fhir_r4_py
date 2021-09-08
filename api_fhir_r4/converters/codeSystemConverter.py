from django.contrib.contenttypes.models import ContentType
from api_fhir_r4.converters import BaseFHIRConverter
from fhir.resources.codesystem import CodeSystem, CodeSystemConcept


class CodeSystemConverter(BaseFHIRConverter):

    @classmethod
    def to_fhir_obj(cls, imis_model, code_field, display_field, id, name, title, description, url):
        fhir_code_system = {}
        cls.build_fhir_code_system_status(fhir_code_system)
        cls.build_fhir_code_system_content(fhir_code_system)
        fhir_code_system = CodeSystem(**fhir_code_system)
        cls.build_fhir_id(fhir_code_system, id)
        cls.build_fhir_url(fhir_code_system, url)
        cls.build_fhir_code_system_name(fhir_code_system, name)
        cls.build_fhir_code_system_title(fhir_code_system, title)
        cls.build_fhir_code_system_date(fhir_code_system)
        cls.build_fhir_code_system_description(fhir_code_system, description)
        cls.build_fhir_code_system_concept(fhir_code_system, imis_model, code_field, display_field)
        return fhir_code_system

    @classmethod
    def build_fhir_id(cls, fhir_code_system, id):
        fhir_code_system.id = id

    @classmethod
    def build_fhir_url(cls, fhir_code_system, url):
        fhir_code_system.url = url

    @classmethod
    def build_fhir_code_system_name(cls, fhir_code_system, name):
        fhir_code_system.name = name

    @classmethod
    def build_fhir_code_system_title(cls, fhir_code_system, title):
        fhir_code_system.title = title

    @classmethod
    def build_fhir_code_system_date(cls, fhir_code_system):
        from core.utils import TimeUtils
        fhir_code_system.date = TimeUtils.now()

    @classmethod
    def build_fhir_code_system_description(cls, fhir_code_system, description):
        fhir_code_system.description = description

    @classmethod
    def build_fhir_code_system_status(cls, fhir_code_system):
        fhir_code_system['status'] = 'active'

    @classmethod
    def build_fhir_code_system_content(cls, fhir_code_system):
        fhir_code_system['content'] = 'complete'

    @classmethod
    def build_fhir_code_system_count(cls, fhir_code_system, number_of_records):
        fhir_code_system.count = f"{number_of_records}"

    @classmethod
    def build_fhir_code_system_concept(cls, fhir_code_system, imis_model, code_field, display_field):
        content_type = ContentType.objects.get(model=imis_model)
        model_class = content_type.model_class()
        results = model_class.objects.all()
        number_of_records = results.count()
        cls.build_fhir_code_system_count(fhir_code_system, number_of_records)
        for result in results:
            code_system_concept = CodeSystemConcept.construct()
            code_system_concept.code = getattr(result, code_field)
            code_system_concept.display = getattr(result, display_field)
            if type(fhir_code_system.concept) is not list:
                fhir_code_system.concept = [code_system_concept]
            else:
                fhir_code_system.concept.append(code_system_concept)
