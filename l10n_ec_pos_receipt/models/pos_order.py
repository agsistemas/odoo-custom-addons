from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        # Primero permitimos que Odoo publique la factura y genere los documentos EDI
        res = super()._post(soft=soft)
        for move in self:
            if move.company_id.account_fiscal_country_id.code == 'EC':
                sri_edis = move.sudo().edi_document_ids.filtered(lambda d: hasattr(d.edi_format_id, 'code') and d.edi_format_id.code == 'l10n_ec_format_sri')
                if sri_edis and hasattr(sri_edis[0], '_l10n_ec_get_info_tributaria'):
                    try:
                        if not sri_edis[0].l10n_ec_xml_access_key:
                            info = sri_edis[0].sudo()._l10n_ec_get_info_tributaria(move.sudo())
                            access_key = info.get('claveAcceso') or ''
                            if access_key:
                                sri_edis.sudo().write({'l10n_ec_xml_access_key': access_key})
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).error("Error generating SRI XML access key inside _post: %s", str(e))
        return res

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _export_for_ui(self, order):
        result = super()._export_for_ui(order)
        if order.account_move and order.account_move.company_id.account_fiscal_country_id.code == 'EC':
            move = order.account_move
            sri_edis = move.sudo().edi_document_ids.filtered(lambda d: hasattr(d.edi_format_id, 'code') and d.edi_format_id.code == 'l10n_ec_format_sri')
            if sri_edis:
                result['l10n_ec_xml_access_key'] = sri_edis[0].l10n_ec_xml_access_key or ''
            else:
                result['l10n_ec_xml_access_key'] = ''
            result['l10n_latam_document_number'] = move.l10n_latam_document_number or ''
            result['company_env'] = move.company_id.l10n_ec_type_environment if hasattr(move.company_id, 'l10n_ec_type_environment') else ''
        return result

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super().create_from_ui(orders, draft=draft)
        for order_data in res:
            if order_data.get('account_move'):
                move = self.env['account.move'].browse(order_data.get('account_move'))
                if move.exists() and move.company_id.account_fiscal_country_id.code == 'EC':
                    move.invalidate_recordset(['l10n_ec_xml_access_key'])
                    order_data['l10n_ec_xml_access_key'] = move.l10n_ec_xml_access_key or ''
                    order_data['l10n_latam_document_number'] = move.l10n_latam_document_number or ''
                    order_data['company_env'] = move.company_id.l10n_ec_type_environment if hasattr(move.company_id, 'l10n_ec_type_environment') else ''
                    
                    # Desencadenar el cron de EDI para enviar al SRI asincronamente rapido
                    cron = self.env.ref('account_edi.ir_cron_edi_network', raise_if_not_found=False)
                    if cron:
                        cron.sudo()._trigger()
        return res
