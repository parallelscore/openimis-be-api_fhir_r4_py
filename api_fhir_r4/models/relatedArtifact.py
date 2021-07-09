from enum import Enum


class RelatedArtifactType(Enum):

    DOCUMENTATION = 'documentation'
    JUSTIFICATION = 'justification'
    CITATION = 'citation'
    PREDECESSOR = 'predecessor'
    SUCCESSOR = 'successor'
    DERIVED_FROM = 'derived-from'
    DEPENDS_ON = 'depends-on'
    COMPOSED_OF = 'composed-of'
