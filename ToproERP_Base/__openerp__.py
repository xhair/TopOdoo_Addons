# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': u'基础信息',
    'version': '0.1',
    'website': 'https://www.movdy.com',
    'category': u'基础信息',
    "author" : u"ToproERP Development Team（feast）",
    'sequence': 1,
    'summary': u'包括品牌、产品的管理',
    'description': u'包括'
                   u'品牌、产品、文档类型的管理，备注：会直接安装odoo自带的产品模块',
    'depends':['product','base','hr'],
    'data': [
        "security/ToproErp_Base_security.xml",
        "security/ir.model.access.csv",
        'views/parameters.xml',
        'views/toproerp_base_menu.xml',
        'views/base_css_js.xml',
        'views/toproerp_brands_view.xml',
        'views/toproerp_document_type_view.xml',
        'views/product_template_view.xml',
        'views/res_users_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/hr_department_view.xml',
        'views/hr_job_view.xml',
        'views/hr_employee_view.xml',
        'views/ir_module_module_views.xml',
    ],
    'test': [
    ],
    'demo':[
        'demo/toproerp_base_demo.xml',
    ],
    'qweb':[
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}
