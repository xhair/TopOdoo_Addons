# -*- coding: utf-8 -*-

from openerp import api, models, fields, _
import json
from json import *
from wechat_enterprise_basic import WeChatEnterprise
import logging
from openerp.http import request

_logger = logging.getLogger(__name__)

class WechatEnterpriseContactEmployee(models.Model):

    _name = 'wechat.enterprise.contact.employee'
    _description = 'Wechat Enterprise Contact Employee Manage'

    # @api.constrains('userid')
    # def UserID_check(self):
    #     data = self.search([('userid', '=', self.userid)])
    #     if len(data)>1:
    #         raise Warning(u'UserID必须唯一')
    #
    # @api.constrains('mobile')
    # def mobile_check(self):
    #     data = self.search([('mobile', '=', self.mobile)])
    #     if len(data)>1:
    #         raise Warning(u'手机号码必须唯一')
    #
    # @api.constrains('weixinid')
    # def weixinid_check(self):
    #     data = self.search([('weixinid', '=', self.weixinid)])
    #     if len(data)>1:
    #         raise Warning(u'微信号必须唯一')
    #
    # @api.constrains('email')
    # def email_check(self):
    #     data = self.search([('email', '=', self.email)])
    #     if len(data)>1:
    #         raise Warning(u'邮箱必须唯一')

    userid = fields.Char(u'成员UserID',help=u"对应管理端的帐号，企业内必须唯一。长度为1~64个字节",required=True)
    name = fields.Char(u'成员名称',required=True)
    department = fields.Many2many('wechat.enterprise.contact.department','contact_employee_to_contact_department_ref',
                                'department_id','partylist',u'成员所属部门列表')
    position = fields.Char(u'职位信息')
    mobile =fields.Char(u'手机号码', required=True)
    gender = fields.Selection([('0',u'未定义'),('1',u'男性'),('2',u'女性')],u'性别',required=True,default =
                            '1')
    email = fields.Char(u'邮箱')
    weixinid = fields.Char(u'微信号')
    avatar_mediaid = fields.Char(u'成员头像的mediaid')
    extattr = fields.Char(u'扩展属性')
    status = fields.Selection([('1',u'已关注'),('2',u'已禁用'),('4',u'未关注')],u'关注状态',required=True,default =
                            '4')
    fetch_child = fields.Selection([('0',u'否'),('1',u'是')],u'是否递归获取子部门下面的成员',default = 0)
    department_id = fields.Char(u'获取的部门id')
    useridlist = fields.Char(u'成员UserID列表')
    enable = fields.Selection([('0',u'禁用成员'),('1',u'启用成员')],u'是否递归获取子部门下面的成员',default = 0)


    # 更新所有成员至微信通讯录
    @api.one
    def create_employee(self):
        '''
        更新所有成员至微信通讯录
        :return:
        创建部门
        参数	必须	说明
        access_token	是	调用接口凭证
        userid	是	成员UserID。对应管理端的帐号，企业内必须唯一。长度为1~64个字节
        name	是	成员名称。长度为1~64个字节
        department	否	成员所属部门id列表
        position	否	职位信息。长度为0~64个字节
        mobile	否	手机号码。企业内必须唯一，mobile/weixinid/email三者不能同时为空
        gender	否	性别。1表示男性，2表示女性
        email	否	邮箱。长度为0~64个字节。企业内必须唯一
        weixinid	否	微信号。企业内必须唯一。（注意：是微信号，不是微信的名字）
        avatar_mediaid	否	成员头像的mediaid，通过多媒体接口上传图片获得的mediaid
        extattr	否	扩展属性。扩展属性需要在WEB管理端创建后才生效，否则忽略未知属性的赋值
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        employees = self.env['hr.employee'].search([])
        try:
            for employee in employees:
                employee_data = {}
                employee_data['userid'] = employee['mobile_phone']
                employee_data['name'] = employee['name_related']
                employee_data['mobile'] = employee['mobile_phone']
                if employee['gender'] == "male":
                    employee_data['gender'] = "1"
                else:
                    employee_data['gender'] = "2"
                if employee['department_id']:
                    lists = []
                    departments = employee['department_id']
                    for department in departments:
                        lists.append(department['id'])
                    employee_data['department'] = lists
                if employee['job_id']:
                    employee_data['position'] = employee['job_id']['name']
                if employee['work_email']:
                    employee_data['email'] = employee['work_email']
                # if data['weixinid']:
                #     employee_data['weixinid'] = data['weixinid']
                print employee_data
                wechat.create_user(employee_data)
        except Exception, e:
            _logger.warning(u'更新app失败,原因：%s', e.message)
            print e.message
            raise Warning(_(u'更新app失败,原因：%s', e.message))

    # 从微信通讯录获取成员通讯录
    @api.one
    def get_employee(self):
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        employees = wechat.get_users_in_department_detail(1,1,0)   # 获得部门所有的成员
        employees = employees[1]['userlist']
        for employee in employees:
            employee_data = {}
            employee_data['userid'] = employee['userid']
            employee_data['name'] = employee['name']
            # for department_id in employee['department']:
            #     department = self.env['wechat.enterprise.contact.department'].sudo().search([("department_id","=",department_id)])
            #     employee_data['department'] = [(6,0,department.department_id)]
            #     print employee_data['department']
            employee_data['mobile'] = employee['mobile']
            employee_data['gender'] = employee['gender']
            employee_data['status'] = str(employee['status'])
            # if employee['email']:
            #     employee_data['email'] = employee['email']
            # if employee['weixinid'] is False:
            #     continue
            # else:
            #     employee_data['weixinid'] = employee['weixinid']
            # if employee['avatar'] is False:
            #     continue
            # else:
            #     employee_data['avatar'] = employee['avatar']
            # if employee['extattr'] is False:
            #     continue
            # else:
            #     employee_data['extattr'] = employee['extattr']
            self.create(employee_data)

    # 更新当前员工至微信
    @api.one
    def create_current_employee(self):
        '''
        更新当前成员至微信通讯录
        :return:
        创建部门
        参数	必须	说明
        access_token	是	调用接口凭证
        userid	是	成员UserID。对应管理端的帐号，企业内必须唯一。长度为1~64个字节
        name	是	成员名称。长度为1~64个字节
        department	否	成员所属部门id列表
        position	否	职位信息。长度为0~64个字节
        mobile	否	手机号码。企业内必须唯一，mobile/weixinid/email三者不能同时为空
        gender	否	性别。1表示男性，2表示女性
        email	否	邮箱。长度为0~64个字节。企业内必须唯一
        weixinid	否	微信号。企业内必须唯一。（注意：是微信号，不是微信的名字）
        avatar_mediaid	否	成员头像的mediaid，通过多媒体接口上传图片获得的mediaid
        extattr	否	扩展属性。扩展属性需要在WEB管理端创建后才生效，否则忽略未知属性的赋值
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        employee_data = {}
        employee_data['userid'] = self.userid
        employee_data['name'] = self.name
        employee_data['mobile'] = self.mobile
        employee_data['gender'] = self.gender
        if self.department:
            lists = []
            departments = self.department
            for department in departments:
                lists.append(department['department_id'])
            employee_data['department'] = lists
        if self.position:
            employee_data['position'] = self.position
        if self.email:
            employee_data['email'] = self.email
        if self.weixinid:
            employee_data['weixinid'] = self.weixinid
        if self.avatar_mediaid:
            employee_data['avatar_mediaid'] = self.avatar_mediaid
        if self.extattr:
            employee_data['extattr'] = self.extattr
        print employee_data
        wechat.create_user(employee_data)


