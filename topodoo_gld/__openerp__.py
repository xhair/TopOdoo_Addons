# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': u'工联单cn',
    'version': '1.0.0',
    'website': '',
    'category': u'行政办公',
    "author": u"gld Development Team（feast）",
    'sequence': 2,
    'summary': u'包括：我发起的工联单、待办工联单、已办工联单',
    'description': u'主要包括：我发起的工联单、等待我处理的工联单、我已处理的工联单',
    'depends': ['hr', 'mail'],  # 依赖的模块
    'data': [
        "security/sys_oa_security.xml",
        "security/ir.model.access.csv",
        "wizard/syt_oa_gld_opinion.xml",  # 审批意见向导
        "wizard/add_approver_wizard.xml",  # 添加审批人向导
        "wizard/add_copy_people_wizard.xml",  # 添加抄送人向导
        "views/syt_oa_gld_template_type_view.xml",
        "views/syt_oa_gld_template_view.xml",
        "views/syt_oa_gld.xml",
        "views/syt_oa_gld_transfer_view.xml",
        'report/gld_service_order_report.xml',
        'report/gld_service_order_report_view.xml'
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
