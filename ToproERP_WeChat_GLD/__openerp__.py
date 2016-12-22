# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': u'工联单微信版',
    'version': '0.1',
    'website': 'https://www.movdy.com',
    'category': u'行政办公',
    "author" : u"ToproERP Development Team（feast）",
    'sequence': 2,
    'summary': u'包括：新建工联单、待办、已办、我的工联',
    'description': u'主要包括：新建工联单、待办、已办、我的工联单',
    'depends' : ['ToproERP_GLD'],  # 依赖的模块
    'data': [
        "views/wechat_gld_view.xml",
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    # 'css':[
    #     'static/src/css/my.css',
    # ],
    # 'js':[
    #     'static/src/js/gld_add_button.js',
    # ],
    # 'qweb': [ 'static/src/xml/gld_add_button_template.xml' ],
}
