{
    'name': 'Ecuador - POS Receipt SRI Info',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Shows SRI Electronic Authorization details on the POS Ticket',
    'author': 'AGSISTEMAS',
    'depends': ['point_of_sale', 'l10n_ec_account_edi'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'l10n_ec_pos_receipt/static/src/app/models/pos_order.js',
            'l10n_ec_pos_receipt/static/src/app/screens/receipt_screen/receipt/order_receipt.xml',
            'l10n_ec_pos_receipt/static/src/app/screens/partner_editor.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
