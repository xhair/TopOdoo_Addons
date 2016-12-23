# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : '微信/企业号',
    'version' : '9.0.0.1',
    'summary': '企业通讯录，消息处理，企业应用',
    'sequence': 30,
    "author" : 'ToproOdoo Development Team（ST）',
    'description': '''用于企业内部员工的管理，
ERP微信企业号模块
=====================================================
主要针对odoo使用微信进行管理，包括以下功能:
1) 公众号信息管理（企业号下多applicaiton管理）
2) 接收消息处理
3) 发送消息处理
4) 自定义菜单处理

....


本安装包使用了WechatEnterpriseSDK/wechat_sdk.py，在此表示感谢。
源代码可以访问github.地址如下：https://github.com/facert/WechatEnterpriseSDK

    ''',
    'category' : '基础信息',
    'website': 'https://www.movdy.com',
    'depends' : ['hr','ToproERP_Base'],
    'data': [
        'view/wechat_erterprise_menu.xml',
        'view/wechat_enterprise_config_view.xml',
        'view/wechat_enterprise_app_view.xml',
        'view/wechat_enterprise_contact_tag_view.xml',
        'view/wechat_enterprise_contact_user_in_tag_view.xml',
        'view/wechat_enterprise_send_message_view.xml',
        'view/wehcat_enterprise_app_menu_view.xml',
        'view/wechat_enterprise_receive_message_view.xml',
        'view/wechat_enterprise_receive_message_process_view.xml',
        'view/wechat_enterprise_templates.xml',
        "view/hr_employee_view.xml",
        "view/hr_department_view.xml",
        "view/res_company_view.xml",
    ],
    'demo': [
        #'demo/account_demo.xml',
    ],
    'qweb': [
        #"static/src/xml/base.xml",
        #"static/src/xml/account_payment.xml",
        #"static/src/xml/account_report_backend.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    #'post_init_hook': '_auto_install_l10n',
}
