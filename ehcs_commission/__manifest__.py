# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ehcs Commission',
    'version': '16.0',
    'category': 'commission',
    'author': 'ERP Harbor Consulting Services',
    'depends': ['sale_crm', 'account', 'ehcs_custom_extended', 'stock', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'data/sequence_data.xml',
        'views/commission_view.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'views/commission_payment_view.xml',
        'wizard/wiz_commission_transaction_view.xml',
        # Case Studies wizard
        'wizard/redirect_link_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
