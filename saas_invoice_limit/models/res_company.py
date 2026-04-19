from odoo import models, fields, api
from datetime import date

class ResCompany(models.Model):
    _inherit = 'res.company'

    saas_invoice_monthly_limit = fields.Integer(
        string="Límite Mensual de Facturas (SaaS)", 
        default=0,
        help="Número máximo de facturas permitidas por mes. Poner 0 para ilimitado."
    )

    saas_invoice_monthly_used = fields.Integer(
        string="Facturas Usadas este mes",
        compute='_compute_saas_invoices_used'
    )
    
    saas_invoice_monthly_remaining = fields.Integer(
        string="Facturas Restantes",
        compute='_compute_saas_invoices_used'
    )

    @api.depends('saas_invoice_monthly_limit')
    def _compute_saas_invoices_used(self):
        today = date.today()
        first_day = today.replace(day=1)
        for company in self:
            invoice_count = self.env['account.move'].search_count([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('company_id', '=', company.id),
                ('invoice_date', '>=', first_day),
                ('invoice_date', '<=', today)
            ])
            company.saas_invoice_monthly_used = invoice_count
            if company.saas_invoice_monthly_limit > 0:
                remaining = company.saas_invoice_monthly_limit - invoice_count
                company.saas_invoice_monthly_remaining = remaining if remaining > 0 else 0
            else:
                company.saas_invoice_monthly_remaining = 0
