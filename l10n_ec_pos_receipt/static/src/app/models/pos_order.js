/** @odoo-module **/

import { Order } from "@point_of_sale/app/store/models";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

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

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.l10n_ec_xml_access_key = this.l10n_ec_xml_access_key;
        result.l10n_latam_document_number = this.l10n_latam_document_number;
        result.company_env = this.company_env;
        result.l10n_ec_print_edi_receipt = this.pos?.config?.l10n_ec_print_edi_receipt || false;
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
