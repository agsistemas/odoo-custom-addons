/** @odoo-module **/

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        if (this.order && this.order.pos?.config?.l10n_ec_print_edi_receipt) {
            const unit_price_without_tax = this.get_unit_price(); 
            if (this.pos && this.pos.env && this.pos.env.utils && this.pos.env.utils.formatCurrency) {
                result.price = this.pos.env.utils.formatCurrency(unit_price_without_tax);
            } else {
                result.price = unit_price_without_tax.toFixed(2);
            }
            result.price_display = this.get_price_without_tax();
        }
        return result;
    }
});

patch(PosStore.prototype, {
    async push_single_order(order, opts) {
        const syncOrderResult = await super.push_single_order(...arguments);
        if (syncOrderResult && syncOrderResult.length > 0) {
            const res = syncOrderResult[0];
            if (res && order) {
                order.l10n_ec_xml_access_key = res.l10n_ec_xml_access_key || "";
                order.l10n_latam_document_number = res.l10n_latam_document_number || "";
                order.company_env = res.company_env || "";
            }
        }
        return syncOrderResult;
    }
});

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.l10n_ec_xml_access_key = this.l10n_ec_xml_access_key || "";
        this.l10n_latam_document_number = this.l10n_latam_document_number || "";
        this.company_env = this.company_env || "";
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.l10n_ec_xml_access_key = json.l10n_ec_xml_access_key || "";
        this.l10n_latam_document_number = json.l10n_latam_document_number || "";
        this.company_env = json.company_env || "";
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.l10n_ec_xml_access_key = this.l10n_ec_xml_access_key;
        json.l10n_latam_document_number = this.l10n_latam_document_number;
        json.company_env = this.company_env;
        return json;
    },

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.l10n_ec_xml_access_key = this.l10n_ec_xml_access_key;
        result.l10n_latam_document_number = this.l10n_latam_document_number;
        result.company_env = this.company_env;
        result.l10n_ec_print_edi_receipt = this.pos?.config?.l10n_ec_print_edi_receipt || false;
        
        const partner = this.get_partner();
        if (partner) {
            result.partner = {
                name: partner.name,
                vat: partner.vat,
                address: partner.contact_address || partner.address || "",
                phone: partner.phone || partner.mobile || "",
                mobile: partner.mobile || "",
                email: partner.email || ""
            };
        }
        
        let ec_subtotals = {
            subtotals_iva: {},
            ivas: {},
            subtotal_no_objeto: 0.0,
            subtotal_exento: 0.0,
            sin_impuestos: 0.0,
            ice: 0.0,
            irbpnr: 0.0,
            descuento: 0.0
        };

        if (this.get_orderlines) {
            this.get_orderlines().forEach(line => {
                const price_without_tax = line.get_price_without_tax();
                ec_subtotals.sin_impuestos += price_without_tax;

                const taxes = line.get_taxes();
                if (!taxes || taxes.length === 0) {
                    ec_subtotals.subtotals_iva['0'] = (ec_subtotals.subtotals_iva['0'] || 0) + price_without_tax;
                } else {
                    let has_exento = false;
                    let has_no_objeto = false;
                    let iva_pct = 0;
                    
                    taxes.forEach(t => {
                        const name = (t.name || "").toLowerCase();
                        if (name.includes('exento')) {
                            has_exento = true;
                        } else if (name.includes('no objeto')) {
                            has_no_objeto = true;
                        } else if (!name.includes('ice') && !name.includes('irbpnr')) {
                            let pct = t.amount;
                            if (pct > 0 && pct < 1) pct = pct * 100;
                            if (pct > iva_pct) {
                                iva_pct = pct;
                            }
                        }
                    });
                    
                    if (has_exento) {
                        ec_subtotals.subtotal_exento += price_without_tax;
                    } else if (has_no_objeto) {
                        ec_subtotals.subtotal_no_objeto += price_without_tax;
                    } else {
                        // Eliminar decimales innecesarios (e.g. 15.0 -> 15)
                        const key = parseFloat(iva_pct.toFixed(2)).toString();
                        ec_subtotals.subtotals_iva[key] = (ec_subtotals.subtotals_iva[key] || 0) + price_without_tax;
                    }
                }
                
                const unit_price = line.get_unit_price();
                const qty = line.get_quantity();
                const discount_pct = line.get_discount() || 0;
                if (discount_pct > 0) {
                    ec_subtotals.descuento += (unit_price * qty) * (discount_pct / 100);
                }
            });
        }

        if (this.get_tax_details) {
            const taxDetails = this.get_tax_details();
            taxDetails.forEach(td => {
                const name = (td.name || "").toLowerCase();
                if (name.includes('ice')) {
                    ec_subtotals.ice += td.amount;
                } else if (name.includes('irbpnr')) {
                    ec_subtotals.irbpnr += td.amount;
                } else if (!name.includes('exento') && !name.includes('no objeto')) {
                    let pct = 0;
                    if (td.tax && td.tax.amount !== undefined) {
                        pct = td.tax.amount;
                    } else {
                        // Intenta sacar el porcentaje del nombre como respaldo
                        const match = name.match(/(\d+(?:\.\d+)?)\s*%/);
                        if (match) {
                            pct = parseFloat(match[1]);
                        }
                    }
                    if (pct > 0 && pct < 1) pct = pct * 100;
                    if (td.amount > 0) {
                        const key = parseFloat(pct.toFixed(2)).toString();
                        ec_subtotals.ivas[key] = (ec_subtotals.ivas[key] || 0) + td.amount;
                    }
                }
            });
        }
        
        // Convertir a arrays para fácil renderizado en XML
        ec_subtotals.subtotals_iva_arr = Object.entries(ec_subtotals.subtotals_iva).map(([pct, amount]) => ({ pct, amount }));
        if (!ec_subtotals.subtotals_iva_arr.find(i => i.pct === '0')) {
            ec_subtotals.subtotals_iva_arr.push({ pct: '0', amount: 0 });
        }
        ec_subtotals.subtotals_iva_arr.sort((a, b) => parseFloat(a.pct) - parseFloat(b.pct));

        ec_subtotals.ivas_arr = Object.entries(ec_subtotals.ivas).map(([pct, amount]) => ({ pct, amount }));
        ec_subtotals.ivas_arr.sort((a, b) => parseFloat(a.pct) - parseFloat(b.pct));
        
        result.ec_subtotals = ec_subtotals;
        
        if (result.l10n_ec_print_edi_receipt && result.headerData) {
            result.headerData.trackingNumber = result.name;
        }
        
        return result;
    },
});

patch(PaymentScreen.prototype, {
    shouldDownloadInvoice() {
        // Obviar la descarga automatica del archivo RIDE PDF en el navegador si ya
        // se esta incrustando la Facturacion Electronica en el Ticket
        if (this.pos?.config?.l10n_ec_print_edi_receipt) {
            return false;
        }
        return super.shouldDownloadInvoice(...arguments);
    }
});
