from api_fhir_r4.configurations import SubscriptionConfiguration


class R4SubscriptionConfig(SubscriptionConfiguration):
    _config = 'R4_fhir_subscription_config'

    @classmethod
    def build_configuration(cls, cfg):
        cls.get_config().R4_fhir_subscription_config = cfg['R4_fhir_subscription_config']

    @classmethod
    def get_fhir_subscription_channel_rest_hook(cls):
        return cls.get_config_attribute('R4_fhir_subscription_config').get('fhir_sub_channel_rest_hook', 'rest_hook')

    @classmethod
    def get_fhir_subscription_status_off(cls):
        return cls.get_config_attribute('R4_fhir_subscription_config').get('fhir_sub_status_off', 'off')

    @classmethod
    def get_fhir_subscription_status_active(cls):
        return cls.get_config_attribute('R4_fhir_subscription_config').get('fhir_sub_status_active', 'active')
