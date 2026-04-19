from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    l10n_ec_print_edi_receipt = fields.Boolean(string="Imprimir Info SRI (Factura Electrónica) en Recibo POS", default=True)
