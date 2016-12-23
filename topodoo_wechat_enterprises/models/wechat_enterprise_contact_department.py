# -*- coding: utf-8 -*-

from openerp import api, models, fields, _, SUPERUSER_ID
import json
from json import *
from wechat_enterprise_basic import WeChatEnterprise
from openerp.http import request
import urllib3
import logging

_logger = logging.getLogger(__name__)


class WechatEnterpriseContactDepartment(models.Model):
    _name = 'wechat.enterprise.contact.department'
    _description = 'Wechat Enterprise Contact Department Manage'

    name = fields.Char(u'部门名称', required=True)
    parentid = fields.Many2one('wechat.enterprise.contact.department', string=u'父级部门id')
    order = fields.Char(u'在父部门中的次序值')
    department_id = fields.Integer(u'部门id')

    # 微信企业号获取部门通讯录
    @api.one
    def get_department(self):
        '''
        微信企业号获取部门通讯录
        :return:
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        try:
            self.sudo().unlink()
            init_datas = wechat.get_department_list()
            datas = init_datas[1]['department']
            for data in datas:
                department_data = {}
                department_data['name'] = data['name']
                if data['parentid']:
                    parent = self.sudo().search([("department_id", "=", data['parentid'])],limit=1)
                    if parent:
                        department_data['parentid'] = parent.id
                department_data['order'] = data['order']
                department_data['department_id'] = data['id']
                self.create(department_data)
        except Exception, e:
            _logger.warning(u'获取部门失败,原因：%s', e.message)
            print e.message
            raise Warning(_(u'获取部门失败,原因：%s', e.message))


    # 为微信号创建并更新部门
    @api.one
    def create_department(self):
        '''
        为微信号创建新并更新部门
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
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        # datas = self.search([])
        departments = self.env['hr.department'].search([])
        for department in departments:
            print department['name']
            print department['id']
            print department['parent_id']['id']
        try:
            for department in departments:
                if department['parent_id']['id']:
                    wechat.create_department(department['name'],department['parent_id']['id'],department['id'])
                else:
                    wechat.create_department(department['name'],1,department['id'])
            for department in departments:
                wechat.update_department(department['id'],department['name'],department['parent_id']['id'])
            # self.env['wechat.enterprise.contact.employee'].sudo().create_employee()
            # self.env['wechat.enterprise.contact.tag'].sudo().create_tag()
            # self.env['wechat.enterprise.contact.user.in.tag'].sudo().create_user_to_tag()
        except Exception, e:
            _logger.warning(u'更新部门失败,原因：%s', e.message)
            print e.message
            raise Warning(_(u'更新部门失败,原因：%s', e.message))

    # 为微信号创建当前部门
    @api.one
    def create_current_department(self):
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        self.parentid.department_id
        if self.parentid.department_id:
            wechat.create_department(self.name,self.parentid.department_id,self.department_id)
        else:
            wechat.create_department(self.name,1,self.department_id)

