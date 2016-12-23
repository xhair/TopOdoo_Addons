# -*- coding:utf-8 -*-
__author__ = 'suntao'

from openerp import api, models, fields, _
import json
from json import *
from wechat_enterprise_basic import WeChatEnterprise
import logging

_logger = logging.getLogger(__name__)


class WechatEnterpriseContactUserInTag(models.Model):
    _name = 'wechat.enterprise.contact.user.in.tag'
    _description = 'Wechat Enterprise Contact User In Tag Manage'

    tagid = fields.Many2one('wechat.enterprise.contact.tag', string=u'标签名称',required=True)
    userid = fields.Integer(u'部门名称')
    name = fields.Char(u'员工姓名')
    partylist = fields.Many2many('hr.department', 'user_in_tag_to_hr_department_ref',
                                 'wechat_department_id', 'partylist', u'部门列表')
    companylist = fields.Many2many('res.company', 'user_in_tag_to_res_company_ref',
                                 'wechat_company_id', 'companylist', u'公司列表')
    userlist = fields.Many2many('hr.employee', 'user_in_tag_to_hr_employee_ref',
                                'wechat_employee_id', 'userlist', u'员工列表')
    # invalidlist = fields.Char(u'不在权限内的或者非法的成员ID列表，以“|”分隔')
    # invalidparty = fields.Char(u'不在权限内的部门ID列表')


    # 更新标签成员至微信企业号
    @api.one
    def create_user_to_tag(self):
        '''
        更新标签成员至微信企业号
        :return:
        创建标签成员
        参数	必须	说明
        access_token	是	调用接口凭证
        tagid	是	标签ID
        userlist	否	企业成员ID列表，注意：userlist、partylist不能同时为空，单次请求长度不超过1000
        partylist	否	企业部门ID列表，注意：userlist、partylist不能同时为空，单次请求长度不超过100
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        datas = self.sudo().search([])
        print datas
        try:
            for data in datas:
                user_data = {}
                user_data['tagid'] = data['tagid']['tagid']
                if data['userlist']:
                    lists = []
                    userlists = data['userlist']
                    for userlist in userlists:
                        lists.append(userlist['user_id']['login'])
                    user_data['userlist'] = lists
                if data['partylist']:
                    lists = []
                    partylists = data['partylist']
                    companylists = data['companylist']
                    for partylist in partylists:
                        lists.append(partylist['wechat_department_id'])
                    for companylist in companylists:
                        lists.append(companylist['id'])
                    user_data['partylist'] = lists
                wechat.add_users_to_tag(user_data)
        except Exception, e:
            _logger.warning(u'更新app失败,原因：%s', e.message)
            print e.message
            raise Warning(_(u'更新app失败,原因：%s', e.message))

    # 从企业号中获取标签成员列表
    @api.one
    def get_user_from_tag(self):
        print 333
