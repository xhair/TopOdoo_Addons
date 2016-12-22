# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': u'工联单',
    'version': '0.1',
    'website': 'https://www.movdy.com',
    'category': u'行政办公',
    "author": u"ToproERP Development Team（feast）",
    'sequence': 2,
    'summary': u'包括：我发起的工联单、待办工联单、已办工联单',
    'description': u'主要包括：我发起的工联单、等待我处理的工联单、我已处理的工联单',
    'depends': ['hr', 'mail', 'ToproERP_Base', 'ToproERP_Wechat_Enterprises'],  # 依赖的模块
    'data': [
        "security/sys_oa_security.xml",
        "security/ir.model.access.csv",
        "wizard/syt_oa_gld_opinion.xml",  # 审批意见向导
        "wizard/add_approver_wizard.xml",  # 添加审批人向导
        "wizard/add_copy_peoper_wizard.xml",  # 添加抄送人向导
        "views/syt_oa_gld_template_type_view.xml",
        "views/syt_oa_gld_template_view.xml",
        "views/syt_oa_gld.xml",
        "views/syt_oa_gld_transfer_view.xml",
        'report/toproerp_service_order_report.xml',
        'report/toproerp_service_order_report_view.xml'
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
