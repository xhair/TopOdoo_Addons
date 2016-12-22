# -*- coding: utf-8 -*-
__author__ = 'suntao'

from openerp import api,models,fields,_
from wechat_enterprise_basic import WeChatEnterprise
import logging
import json
from openerp.http import request
from json import *

_logger = logging.getLogger(__name__)

class WechatEnterpriseAppMenu(models.Model):
    _name = 'wechat.enterprise.app.menu'
    _description = 'Wechat Enterprise App Menu Manage'


    agentid = fields.Many2one('wechat.enterprise.app',u'企业应用',required=True)
    partner_menu_id = fields.Many2one('wechat.enterprise.app.menu', u'上级菜单')
    type = fields.Selection([('sub_button', u'跳转至子菜单'),('click', u'点击推事件'), ('view', u'跳转URL'), ('scancode_push', u'扫码推事件'), ('scancode_waitmsg', u'扫码推事件且弹出“消息接收中”提示框')
                                , ('pic_sysphoto', u'弹出系统拍照发图'), ('pic_photo_or_album', u'弹出拍照或者相册发图'), ('pic_weixin', u'弹出微信相册发图器'),
                             ('location_select', u'弹出地理位置选择器')], u'按钮的类型', required=True, default='view')
    name = fields.Char(u'菜单标题', required=True)
    key = fields.Char(u'菜单KEY值')
    url = fields.Char(u'网页链接')

    @api.one
    @api.constrains('partner_menu_id','name')
    def _check_menu_name_length(self):
        if self.name and self.partner_menu_id and len(self.name)>7:
            raise Warning(_(u'二级菜单显示名称不能超过14个字符或7个汉字.'))
        elif self.name and not self.partner_menu_id and len(self.name)>4:
            raise Warning(_(u'一级菜单显示名称不能超过8个字符或4个汉字.'))
        else:
            return True

    @api.constrains('agentid')
    def check_menu_number(self):
        '''
        取得一个app的一级菜单量
        :param account_id:
        :return:
        '''
        menus_ids = self.sudo().search([('agentid', '=', self.agentid['name']), ('partner_menu_id', '=', False)])

        if menus_ids and len(menus_ids)>3:
            raise Warning(_(u'公众号的一级菜单数据不能超过3个.'))

        return True

    @api.constrains('partner_menu_id')
    def check_submenu_number(self):
        '''
        取得一个一级菜单的子菜单数量
        :param menu_id:
        :return:
        '''

        sub_menus_ids = self.sudo().search([('partner_menu_id', '=', self.partner_menu_id['name']), ('partner_menu_id', '!=', False)])

        if  sub_menus_ids and len(sub_menus_ids)>5:
            raise Warning(_(u'一级菜单的二级子菜单数据不能超过5个.'))

        return True







