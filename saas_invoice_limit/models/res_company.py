from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    saas_invoice_monthly_limit = fields.Integer(
        string="Límite Mensual de Facturas (SaaS)", 
        default=0,
        help="Número máximo de facturas permitidas por mes. Poner 0 para ilimitado."
    )
