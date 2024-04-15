# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ehcs Custom Extended',
    'version': '16.0',
    'category': 'partner',
    'author': 'ERP Harbor Consulting Services',
    'depends': ['base', 'crm', 'sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'views/res_partner_view.xml',
        'views/crm_lead_views.xml',
        'views/crm_technology_views.xml',
        'views/crm_type_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/erp_software_views.xml',
    ],
    "assets": {
        'web.assets_backend': [
            'ehcs_custom_extended/static/src/xml/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
