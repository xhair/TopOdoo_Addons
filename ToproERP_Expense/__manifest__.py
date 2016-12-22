# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': "Expense account",
    'version': '0.1',
    'category': 'Marketing',
    'description': """
This module is to study module for python.
==============================================================

    """,
    'author': 'Cupid',
    'website': 'https://www.baidu.com',
    'depends': ['hr', 'base', 'ToproERP_GLD'],
    'data': [
        'security/security.xml',
        'wizard/expense_wizard_view.xml',
        'views/expense_account_view.xml',
        'views/expense_set_view.xml',
        'views/expense_account_me_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}
