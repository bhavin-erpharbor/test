# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Ehcs Wizard import data',
    'version': '16.0',
    'category': 'partner',
    'author': 'ERP Harbor Consulting Services',
    'depends': ['contacts', 'partner_firstname', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'data/product_demo.xml',
        'wizard/wiz_import_data_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
