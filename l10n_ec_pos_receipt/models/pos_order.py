from odoo import models, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super().create_from_ui(orders, draft=draft)
        # res is a list of dicts: [{'id': 1, 'account_move': 2, ...}]
        for order_data in res:
            if order_data.get('account_move'):
                order_id = order_data.get('id')
                move = self.env['account.move'].browse(order_data.get('account_move'))
                if move.exists() and move.company_id.account_fiscal_country_id.code == 'EC':
                    sri_edis = move.sudo().edi_document_ids.filtered(lambda d: hasattr(d.edi_format_id, 'code') and d.edi_format_id.code == 'l10n_ec_format_sri')
                    if sri_edis and hasattr(sri_edis[0], '_l10n_ec_get_info_tributaria'):
                        try:
                            # Generar de inmediato la clave de acceso para que viaje al frontend usando superusuario
                            if not sri_edis[0].l10n_ec_xml_access_key:
                                info = sri_edis[0].sudo()._l10n_ec_get_info_tributaria(move.sudo())
                                access_key = info.get('claveAcceso') or ''
                                # Forzar el write en base de datos de manera definitiva
                                if access_key:
                                    sri_edis.sudo().write({'l10n_ec_xml_access_key': access_key})
                        except Exception as e:
                            import logging
                            logging.getLogger(__name__).error("Error generating SRI XML access key immediately in POS checkout: %s", str(e))
                            pass
                    
                    # Como ya forzamos generarlo, al refrescar el move obtendremos de forma segura el dato
                    move.invalidate_recordset(['l10n_ec_xml_access_key'])
                    
                    order_data['l10n_ec_xml_access_key'] = move.l10n_ec_xml_access_key or ''
                    order_data['l10n_latam_document_number'] = move.l10n_latam_document_number or ''
                    order_data['company_env'] = move.company_id.l10n_ec_type_environment if hasattr(move.company_id, 'l10n_ec_type_environment') else ''
                    
                    # Desencadenar el cron de EDI para enviar al SRI asincronamente rapido
                    cron = self.env.ref('account_edi.ir_cron_edi_network', raise_if_not_found=False)
                    if cron:
                        cron.sudo()._trigger()
        return res
