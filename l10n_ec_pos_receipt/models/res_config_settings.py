from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_l10n_ec_print_edi_receipt = fields.Boolean(
        related='pos_config_id.l10n_ec_print_edi_receipt',
        readonly=False
    )
