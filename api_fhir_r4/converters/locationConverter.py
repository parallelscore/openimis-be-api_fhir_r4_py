from django.utils.translation import gettext as _
from django.utils.translation import gettext
from location.models import Location

from api_fhir_r4.configurations import R4IdentifierConfig, R4LocationConfig
from api_fhir_r4.converters import BaseFHIRConverter, ReferenceConverterMixin
from fhir.resources.location import Location as FHIRLocation

from api_fhir_r4.exceptions import FHIRException
from api_fhir_r4.mapping.locationMapping import LocationTypeMapping
from api_fhir_r4.models.imisModelEnums import ImisLocationType
from api_fhir_r4.utils import DbManagerUtils


class LocationConverter(BaseFHIRConverter, ReferenceConverterMixin):

    @classmethod
    def to_fhir_obj(cls, imis_location, reference_type=ReferenceConverterMixin.UUID_REFERENCE_TYPE):
        fhir_location = FHIRLocation.construct()
        cls.build_fhir_physical_type(fhir_location, imis_location)
        cls.build_fhir_pk(fhir_location, imis_location, reference_type)
        cls.build_fhir_location_identifier(fhir_location, imis_location)
        cls.build_fhir_location_name(fhir_location, imis_location)
        cls.build_fhir_part_of(fhir_location, imis_location, reference_type)
        cls.build_fhir_status(fhir_location, imis_location)
        cls.build_fhir_mode(fhir_location)
        return fhir_location

    @classmethod
    def to_imis_obj(cls, fhir_location, audit_user_id):
        errors = []
        fhir_location = FHIRLocation(**fhir_location)
        imis_location = Location()
        cls.build_imis_location_identiftier(imis_location, fhir_location, errors)
        cls.build_imis_location_name(imis_location, fhir_location, errors)
        cls.build_imis_location_type(imis_location, fhir_location, errors)
        cls.build_imis_parent_location_id(imis_location, fhir_location, errors)
        cls.check_errors(errors)
        return imis_location

    @classmethod
    def get_fhir_code_identifier_type(cls):
        return R4IdentifierConfig.get_fhir_location_code_type()

    @classmethod
    def get_reference_obj_uuid(cls, imis_location: Location):
        return imis_location.uuid

    @classmethod
    def get_reference_obj_id(cls, imis_location: Location):
        return imis_location.id

    @classmethod
    def get_reference_obj_code(cls, imis_location: Location):
        return imis_location.code

    @classmethod
    def get_fhir_resource_type(cls):
        return Location

    @classmethod
    def get_imis_obj_by_fhir_reference(cls, reference, errors=None):
        location_uuid = cls.get_resource_id_from_reference(reference)
        return DbManagerUtils.get_object_or_none(Location, uuid=location_uuid)

    @classmethod
    def build_fhir_location_identifier(cls, fhir_location, imis_location):
        identifiers = []
        cls.build_all_identifiers(identifiers, imis_location)
        fhir_location.identifier = identifiers
        cls._validate_imis_identifiers(identifiers)

    @classmethod
    def build_fhir_location_code_identifier(cls, identifiers, imis_location):
        if imis_location is not None:
            identifier = cls.build_fhir_identifier(imis_location.code,
                                                   R4IdentifierConfig.get_fhir_identifier_type_system(),
                                                   R4IdentifierConfig.get_fhir_location_code_type())
            identifiers.append(identifier)

    @classmethod
    def build_imis_location_identiftier(cls, imis_location, fhir_location, errors):
        value = cls.get_fhir_identifier_by_code(
            fhir_location.identifier,
            R4IdentifierConfig.get_fhir_location_code_type()
        )
        if value:
            imis_location.code = value
        cls.valid_condition(imis_location.code is None, gettext('Missing location code'), errors)

    @classmethod
    def build_fhir_location_name(cls, fhir_location, imis_location):
        fhir_location.name = imis_location.name
        cls._validate_imis_name(imis_location)

    @classmethod
    def build_imis_location_name(cls, imis_location, fhir_location, errors):
        name = fhir_location.name
        if not cls.valid_condition(name is None, _('Missing location `name` attribute'), errors):
            imis_location.name = name

    @classmethod
    def build_fhir_physical_type(cls, fhir_location, imis_location):
        cls._validate_physical_type(imis_location)
        system_definition = LocationTypeMapping.PHYSICAL_TYPES_DEFINITIONS.get(imis_location.type)
        fhir_location.physicalType = cls.build_codeable_concept(**system_definition)

    @classmethod
    def build_imis_location_type(cls, imis_location, fhir_location, errors):
        # get the type of location code
        code = fhir_location.type[0].coding[0].code
        if code == R4LocationConfig.get_fhir_code_for_region():
            imis_location.type = ImisLocationType.REGION.value
        elif code == R4LocationConfig.get_fhir_code_for_district():
            imis_location.type = ImisLocationType.DISTRICT.value
        elif code == R4LocationConfig.get_fhir_code_for_ward():
            imis_location.type = ImisLocationType.WARD.value
        elif code == R4LocationConfig.get_fhir_code_for_village():
            imis_location.type = ImisLocationType.VILLAGE.value
        cls.valid_condition(imis_location.type is None, _('Missing location type'), errors)

    @classmethod
    def build_fhir_part_of(cls, fhir_location, imis_location, reference_type):
        if not cls.__is_highers_level_location(imis_location):
            fhir_location.partOf = LocationConverter.build_fhir_resource_reference(
                imis_location.parent,
                'Location',
                imis_location.parent.code,
                reference_type=reference_type
            )

    @classmethod
    def build_imis_parent_location_id(cls, imis_location, fhir_location, errors):
        if fhir_location.partOf:
            parent_id = fhir_location.partOf
            if not cls.valid_condition(parent_id is None, _('Missing location `parent id` attribute'), errors):
                # get the imis parent location object, check if exists
                uuid_location = parent_id.identifier.value
                parent_location = Location.objects.filter(uuid=uuid_location)
                if parent_location:
                    parent_location = parent_location.first()
                    imis_location.parent = parent_location

    @classmethod
    def _validate_imis_identifiers(cls, identifiers):
        code_identifier = cls.get_fhir_identifier_by_code(identifiers, cls.get_fhir_code_identifier_type())
        if not code_identifier:
            raise FHIRException(_('Code identifier has to be present in FHIR Location identifiers, '
                                  '\nidentifiers are: %(identifiers)') % {'identifiers': identifiers})

    @classmethod
    def _validate_imis_name(cls, imis_location):
        if not imis_location.name:
            raise FHIRException(
                _('Location  %(location_uuid)s without name') % {'uuid': imis_location.uuid}
            )

    @classmethod
    def _validate_physical_type(cls, imis_location):
        allowed_keys = LocationTypeMapping.PHYSICAL_TYPES_DEFINITIONS.keys()
        if imis_location.type not in allowed_keys:
            error_msg_keys = {
                'type': imis_location.type, 'location': imis_location.uuid, 'types': allowed_keys
            }
            raise FHIRException(
                _('Invalid location type %(type) for location %(location), '
                  'supported types are: %(types)') % error_msg_keys
            )

    @classmethod
    def build_fhir_mode(cls, fhir_location):
        fhir_location.mode = 'instance'

    @classmethod
    def build_fhir_status(cls, fhir_location, imis_location):
        if cls.__location_active(imis_location):
            fhir_location.status = R4LocationConfig.get_fhir_code_for_active()
        else:
            fhir_location.status = R4LocationConfig.get_fhir_code_for_inactive()

    @classmethod
    def __location_active(cls, imis_location):
        return imis_location.validity_to is None

    @classmethod
    def __is_highers_level_location(cls, imis_location):
        return imis_location.parent is None
