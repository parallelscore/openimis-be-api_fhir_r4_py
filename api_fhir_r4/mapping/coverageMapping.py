from api_fhir_r4.configurations import R4CoverageConfig


class CoverageStatus(object):

    @classmethod
    def map_status(cls, code):
        codes = {
            1: R4CoverageConfig.get_status_idle_code(),
            2: R4CoverageConfig.get_status_active_code(),
            4: R4CoverageConfig.get_status_suspended_code(),
            8: R4CoverageConfig.get_status_suspended_code(),
            None: R4CoverageConfig.get_status_idle_code(),
        }
        return codes[code]
