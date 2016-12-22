# -*- coding: utf-8 -*-
__author__ = 'suntao'

from openerp import api, models, exceptions,fields, _
import json
from json import *
from wechat_enterprise_basic import WeChatEnterprise
import logging
from openerp.http import request

_logger = logging.getLogger(__name__)

from openerp import fields, models, api

class WechatEnterpriseDepartment(models.Model):
    _inherit = "hr.department"

    @api.model
    def create(self, vals):
        d = super(WechatEnterpriseDepartment, self).create(vals)
        wechat_department_id = str(d.company_id.id) + str(100000+d.id)[1:]
        d.sudo().write({'wechat_department_id':wechat_department_id})
        print d
        if d.parent_id == False:
            self.create_current_department(d.name, d.company_id.id, d.wechat_department_id, False)
        else:
            self.create_current_department(d.name, d.company_id.id, d.wechat_department_id, d.parent_id.wechat_department_id)
        return d

    @api.multi
    def unlink(self):
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            for data in self:
                wechat.delete_department(data.wechat_department_id)
        return super(WechatEnterpriseDepartment, self).unlink()

    @api.multi
    def write(self, vals):
        d = super(WechatEnterpriseDepartment, self).write(vals)
        self.update_current_department(self.parent_id)
        return d


    wechat_department_id = fields.Char(string=u'微信部门编号',readonly=True)

    # 为微信号创建并更新所有部门
    @api.multi
    def create_department(self):
        '''
        为微信号创建新并更新所有部门
        :return:
        创建部门
        参数	必须	说明
        access_token	是	调用接口凭证
        id	是	部门id
        name	否	更新的部门名称。长度限制为1~64个字符。修改部门名称时指定该参数
        parentid	否	父亲部门id。根部门id为1
        order	否	在父部门中的次序。从1开始，数字越大排序越靠后
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        departments = self.env['hr.department'].search([])
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

        if wechat and departments:
            lists_two = ''
            for department in departments:
                if department['wechat_department_id'] == False or department['wechat_department_id'] == '':
                    wechat_department_id = str(department.company_id.id) + str(100000+department.id)[1:]
                    department.sudo().write({'wechat_department_id':wechat_department_id})
                    # lists_two += '、'+department['name']
                if department['parent_id']['id']:
                    wechat.create_department(department['name'],department['parent_id']['wechat_department_id'],department['wechat_department_id'])
                else:
                    wechat.create_department(department['name'],department['company_id']['id'],department['wechat_department_id'])
            for department in departments:
                if department['parent_id']['id']:
                    wechat.update_department(department['wechat_department_id'],department['name'],department['parent_id']['wechat_department_id'])
                else:
                    wechat.update_department(department['wechat_department_id'],department['name'],department['company_id']['id'])
            # print lists_two
            # if len(lists_two)>0:
            #     raise exceptions.Warning(u"%s 的微信部门编号不存在，请重新创建该部门后再次更新！" % lists_two[1:])
        else:
            raise exceptions.Warning(u"企业号尚未配置或无部门")
        # except Exception, e:
        #     raise exceptions.Warning(u"更新部门失败")
        #     _logger.warning(u'更新部门失败,原因：%s', e.message)
        #     print e.message
        #     raise Warning(_(u'更新部门失败,原因：%s', e.message))

    # 为微信号创建当前部门
    def create_current_department(self,name,company_id,wechat_department_id,parent_id):
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            if wechat_department_id == False or not wechat_department_id:
                raise exceptions.Warning(u"微信部门编号不存在，无法更新，请重新创建该部门")
            if parent_id == False:
                wechat.create_department(name, company_id, wechat_department_id)
            else:
                wechat.create_department(name,parent_id, wechat_department_id)
            if parent_id == False:
                wechat.update_department(wechat_department_id, name, company_id)
            else:
                wechat.update_department(wechat_department_id, name, parent_id)
        else:
            return 1

    def update_current_department(self,parent_id):
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            if parent_id:
                wechat.update_department(self.wechat_department_id, self.name, self.parent_id.wechat_department_id)
            else:
                wechat.update_department(self.wechat_department_id, self.name, self.company_id.id)
        else:
            return 1
