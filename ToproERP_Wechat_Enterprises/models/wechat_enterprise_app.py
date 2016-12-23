# -*- coding: utf-8 -*-

from openerp import api,models,exceptions,fields,_
from wechat_enterprise_basic import WeChatEnterprise
import logging
import json
from json import *
from openerp.http import request

_logger = logging.getLogger(__name__)

class WechatEnterpriseApp(models.Model):
    _name = 'wechat.enterprise.app'
    _description = 'Wechat Enterprise App Manage'

    agentid = fields.Integer(string = u'应用ID', required=True)
    code = fields.Char(string = u'自定义代码')
    name = fields.Char(u'企业号应用名称')
    description = fields.Text(u'企业号应用详情')
    redirect_domain = fields.Char(u'企业应用可信域名')
    isreportuser = fields.Selection([('0',u'不接受'),('1',u'接收')],u'是否接收用户变更通知',required=True,default =
                            '0')
    isreportenter = fields.Selection([('0',u'不接受'),('1',u'接收')],u'是否上报用户进入应用事件',required=True,default =
                            '0')
    home_url = fields.Char(u'主页型应用url')
    square_logo_url = fields.Char(u'方形头像url')
    round_logo_url = fields.Char(u'圆形头像url')
    type = fields.Selection([('1',u'消息型'),('2',u'主页型')],u'应用类型',required=True,default =
                            '1')
    allow_userinfos = fields.Char(u'企业应用可见范围（人员）')
    allow_partys = fields.Char(u'企业应用可见范围（部门）')
    allow_tags = fields.Char(u'企业应用可见范围（标签）')
    report_location_flag = fields.Selection([('0',u'不上报'),('1',u'进入会话上报'),('2',u'持续上报')],u'企业应用是否打开地理位置上报',required=True,default =
                            '1')
    logo_mediaid = fields.Char(u'企业应用头像的mediaid')
    close = fields.Selection([('0',u'否'),('1',u'是')],u'是否禁用',required=True,default =
                            '0')
    app_menu_ids = fields.One2many('wechat.enterprise.app.menu','agentid',string=u'自定义菜单')
    Token = fields.Char(u'Token')
    EncodingAESKey = fields.Char(u'EncodingAESKey')

    # 同步app至微信企业号
    @api.one
    def sync_app(self):
        '''
        同步app到微信
        :return:
        '''
        # 实例化 wechatEnterprise
        #wechat = WeChatEnterprise(agentid = 1)
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        if wechat:
            try:
                for account in self:
                    app_json = {}
                    app_json['name'] = account.name
                    if account.description:
                        app_json['description'] = account.description
                    if account.redirect_domain:
                        app_json['redirect_domain'] = account.redirect_domain
                    app_json['agentid'] = int(account.agentid)
                    app_json['report_location_flag'] = int(account.report_location_flag)
                    if account.type == "1":    # 消息型应用
                        if account.name and account.agentid \
                                and account.isreportuser and account.isreportenter and account.report_location_flag:
                            app_json['isreportuser'] = int(account.isreportuser)
                            app_json['isreportenter'] = int(account.isreportenter)
                            print app_json
                            wechat.create_app(app_json)
                    elif account.type == "2":    # 主页型应用
                        if account.name and account.agentid \
                                 and account.report_location_flag and account.home_url:
                            app_json['home_url'] = account.home_url
                            print app_json
                            wechat.create_app(app_json)
            except Exception,e:
                _logger.warning(u'更新app失败,原因：%s',e.message)
                print e.message
                raise Warning(_(u'更新app失败,原因：%s',e.message))
        else:
            raise exceptions.Warning(u"初始化企业号失败")



    # 同步菜单至app
    @api.one
    def update_app_menu(self):
        '''
        同步菜单至app
        :return:
        '''
        # 实例化 wechatEnterprise
        #wechat = WeChatEnterprise(self.agentid)
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = self.agentid)
        menus = self.env['wechat.enterprise.app.menu'].sudo().search([("agentid","=",self.name)])
        wechat.delete_app_menu()   #删除已有的菜单
        menu_json = {'button':[]}
        button = []
        if wechat and menus:
            for menu in menus:
                menu_data = {}
                menu_data['name'] = menu['name']
                if not menu['partner_menu_id']:
                    sub_menus = request.env['wechat.enterprise.app.menu'].sudo().search([("agentid","=",self.name),("partner_menu_id","=",menu['name'])])
                    if sub_menus and len(sub_menus)>0 and len(sub_menus)<6:
                        sub_menu_list = []
                        for sub_menu in sub_menus:
                            sub_menu_data = {}
                            sub_menu_data['name'] = sub_menu['name']
                            if menu['type'] == 'view' or menu['type'] == 'sub_button':
                                sub_menu_data['type'] = sub_menu['type']
                                sub_menu_data['url'] = sub_menu['url']
                            else:
                                sub_menu_data['type'] = sub_menu['type']
                                sub_menu_data['key'] = sub_menu['key']
                            sub_menu_list.append(sub_menu_data)
                            menu_data['sub_button'] = sub_menu_list
                    else:
                        if menu['type'] == 'view' or menu['type'] == 'sub_button':
                            menu_data['type'] = menu['type']
                            menu_data['url'] = menu['url']
                        else:
                            menu_data['type'] = menu['type']
                            menu_data['key'] = menu['key']
                    button.append(menu_data)
            menu_json['button'] = button
            wechat.update_app_menu(menu_json)
        else:
            raise exceptions.Warning(u"初始化企业号失败或该应用无菜单")