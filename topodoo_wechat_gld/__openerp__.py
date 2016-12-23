# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': u'工联单微信补丁cn',
    'version': '0.1',
    'website': 'https://www.movdy.com',
    'category': u'行政办公',
    "author" : u"gld Development Team（feast）",
    'sequence': 2,
    'summary': u'包括：新建工联单、待办、已办、我的工联',
    'description': u'主要包括：新建工联单、待办、已办、我的工联单',
    'depends' : ['topodoo_gld','topodoo_wechat_enterprises'],  # 依赖的模块
    'data': [
        "views/wechat_gld_view.xml",
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
