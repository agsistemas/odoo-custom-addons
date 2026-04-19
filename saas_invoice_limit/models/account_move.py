from odoo import models, api, _
from odoo.exceptions import UserError
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        # Primero, verificamos si hay límite configurado
        for move in self:
            # Solo nos importa si es Factura de Cliente (out_invoice)
            if move.move_type == 'out_invoice':
                company = move.company_id
                limit = company.saas_invoice_monthly_limit

                # Si el límite es mayor a 0, procedemos a contar
                if limit > 0:
                    today = date.today()
                    first_day = today.replace(day=1)
                    
                    # Contamos facturas confirmadas (posted) este mes
                    # Excluimos la factura actual si ya estuviera en base de datos para evitar doble conteo (aunque en post usualmente está en draft)
                    invoice_count = self.env['account.move'].search_count([
                        ('move_type', '=', 'out_invoice'),
                        ('state', '=', 'posted'),
                        ('company_id', '=', company.id),
                        ('invoice_date', '>=', first_day),
                        ('invoice_date', '<=', today)
                    ])

                    if invoice_count >= limit:
                        msg = _(
                            "Has alcanzado el límite de facturas de tu plan mensual (%s facturas).\n"
                            "Por favor contacta a AGSistemas Informáticos para actualizar tu membresía."
                        ) % limit
                        raise UserError(msg)

        # Si todo está bien, ejecutamos el código original de Odoo
        return super(AccountMove, self).action_post()
