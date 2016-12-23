# -*- coding: utf-8 -*-
__author__ = 'suntao'
from openerp import api, models, exceptions,fields, _
import json
from json import *
from wechat_enterprise_basic import WeChatEnterprise
import logging
from openerp.http import request
import openerp
from openerp.addons.base import res

_logger = logging.getLogger(__name__)

from openerp import fields, models


class WechatEnterpriseCompany(models.Model):
    _inherit = "res.company"
    _description = '公司'

    @api.model
    def create(self, vals):
        d = super(WechatEnterpriseCompany, self).create(vals)
        self.create_single_company(d.name, d.id, d.parent_id)
        return d

    @api.multi
    def unlink(self):
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            for data in self:
                wechat.delete_department(data.id)
        return super(WechatEnterpriseCompany, self).unlink()

    @api.multi
    def write(self, vals):
        d = super(WechatEnterpriseCompany, self).write(vals)
        self.update_single_company(self.parent_id)
        return d

    wechat_company_id = fields.Integer(string=u'微信公司编号',readonly=True)

    # 为微信号创建并更新所有公司
    @api.multi
    def create_company(self):
        '''
        为微信号创建新并更新所有公司
        :return:
        创建部门
        参数	必须	说明
        access_token	是	调用接口凭证
        id	是	部门id
        name	否	更新的公司名称。长度限制为1~64个字符。修改部门名称时指定该参数
        parentid	否	父亲公司id。根部门id为1
        order	否	在父公司中的次序。从1开始，数字越大排序越靠后
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        companys = self.env['res.company'].search([])
        if wechat and companys:
            for company in companys:
                if company['parent_id']['id']:
                    wechat.create_department(company['name'],company['parent_id']['id'],company['id'])
                else:
                    wechat.create_department(company['name'], 1, company['id'])
            for company in companys:
                if company['parent_id']['id']:
                    wechat.update_department(company['id'],company['name'],company['parent_id']['id'])
                else:
                    wechat.update_department(company['id'], company['name'], 1)
        else:
            raise exceptions.Warning(u"企业号尚未配置或无公司")

    # 为微信号创建并更新当前公司
    @api.multi
    def create_single_company(self, name, company_id, parent_id=None):
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            if parent_id:
                wechat.create_department(name, parent_id, company_id)
            else:
                wechat.create_department(name, 1, company_id)
        else:
            return 1

    def update_single_company(self,parent_id):
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            if not parent_id.id:
                wechat.update_department(self.id,self.name,1)
            else:
                wechat.update_department(self.id,self.name, self.parent_id.id)
        else:
            return 1