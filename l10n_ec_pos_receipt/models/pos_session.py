from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if 'pos.config' in loaded_data:
            # We don't usually need this if we injected it via pos_ui_models_to_load, but in Odoo 17
            # attributes in pos.config are automatically loaded if they exist, except sometimes they need _loader_params
            pass

    def _loader_params_pos_config(self):
        return super()._loader_params_pos_config()
