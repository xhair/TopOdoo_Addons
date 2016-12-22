# -*- coding: utf-8 -*-
__author__ = 'suntao'

from openerp import api, models, exceptions, fields, _
from openerp import api, models, fields, _ , tools
import logging
from  exceptions import Warning
import time,datetime
from datetime import datetime,timedelta
from json import *
import base64
import urllib2
_logger = logging.getLogger(__name__)

class WechatEnterpriseEmployee(models.Model):
    _inherit = "hr.employee"
    _description = 'employee'

    @api.model
    def create(self, vals):
        d = super(WechatEnterpriseEmployee, self).create(vals)
        if vals.get('name') or vals.get('user_id') or vals.get('department_id') or vals.get('work_phone') or vals.get('mobile_phone'):
            if d:
                self.create_current_employee(d,state=1)
        return d

    @api.multi
    def write(self, vals):
        d = super(WechatEnterpriseEmployee, self).write(vals)
        data = self
        if vals.get('name') or vals.get('user_id') or vals.get('department_id') or vals.get('work_phone') or vals.get('mobile_phone'):
            if data:
                self.create_current_employee(data,state=2)
        return d


    @api.multi
    def unlink(self):
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            for data in self:
                if data.user_id:
                    wechat.delete_user(data.user_id.login)
                else:
                    wechat.delete_user(data.work_email)
        return super(WechatEnterpriseEmployee, self).unlink()

    wechat_contacts_id = fields.Char(string=u'微信用户ID',readonly=True)

 # 更新所有成员至微信通讯录
    @api.multi
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
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=1)
        employees = self.env['hr.employee'].search([])
        if wechat and employees:
            peoples = ''
            number = 0
            for employee in employees:
                employee_data = {}
                if employee['user_id']:
                    employee_data['userid'] = employee['user_id']['login']
                else:
                    employee_data['userid'] = employee['work_email']
                employee_data['name'] = employee['name_related']
                if employee['mobile_phone']:
                    employee_data['mobile'] = employee['mobile_phone']
                else:
                    employee_data['mobile'] = employee['work_phone']
                if employee['gender'] == "male":
                    employee_data['gender'] = "1"
                else:
                    employee_data['gender'] = "2"
                if employee['department_id']:
                    lists = []
                    departments = employee['department_id']
                    for department in departments:
                        lists.append(department['wechat_department_id'])
                    employee_data['department'] = lists
                if employee['job_id']:
                    employee_data['position'] = employee['job_id']['name']
                if employee['work_email']:
                    employee_data['email'] = employee['work_email']
                if employee_data['name']==False or employee_data['userid']==False or\
                        employee_data['mobile']==False or employee_data['department']==False:
                    peoples += '、'+employee['name']
                number = number + 1
                print "have been upload:%s people" % number
                wechat.create_user(employee_data)
            if len(peoples) > 0:
                raise exceptions.Warning(u"%s 的姓名，邮箱，手机号和关联部门信息不完整，请填写完整后再次更新！" % peoples[1:] )
        else:
            raise exceptions.Warning(u"更新成员失败")

    # 获取微信头像
    @api.multi
    def get_employee_image(self):
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        customer = wechat.get_user(self.user_id.login)
        print customer
        if not "avatar" in customer[1]:
            raise Warning(u"当前员工尚未关注微信企业号")
        else:
            print customer[1]['avatar']
            self.image = base64.encodestring(urllib2.urlopen(customer[1]['avatar']).read())

    # 更新当前员工至微信
    def create_current_employee(self,d,state):
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
        #wechat = WeChatEnterprise(agentid=1)
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            employee_data = {}
            if d.user_id:
                employee_data['userid'] = d.user_id.login
            else:
                employee_data['userid'] = d.work_email
            employee_data['name'] = d.name_related
            if d.mobile_phone:
                employee_data['mobile'] = d.mobile_phone
            else:
                employee_data['mobile'] = d.work_phone
            if d.gender == "male":
                employee_data['gender'] = "1"
            else:
                employee_data['gender'] = "2"
            if d.department_id:
                lists = []
                departments = d.department_id
                for department in departments:
                    if not department.wechat_department_id:
                        wechat_department_id = str(department.company_id.id) + str(100000+department.id)[1:]
                        department.sudo().write({'wechat_department_id':wechat_department_id})
                        lists.append(department.wechat_department_id)
                    else:
                        lists.append(department.wechat_department_id)
                employee_data['department'] = lists
            if d.job_id:
                employee_data['position'] = d.job_id.name
            if d.work_email:
                employee_data['email'] = d.work_email
            if employee_data['name']==False or employee_data['userid']==False or\
                    employee_data['mobile']==False or employee_data['department']==False:
                raise exceptions.Warning(u"员工姓名，邮箱，手机号，部门信息不完整")
            else:
                if state == 1:
                    wechat.create_user(employee_data)
                    return 1
                elif state == 2:
                    wechat.create_user(employee_data)
                    wechat.update_user(employee_data)
                    return 1
        else:
            return 1

    # 在微信通讯录删除此员工
    @api.multi
    def delete_current_employee(self):
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
        if wechat:
            if self.user_id:
                wechat.delete_user(self.user_id.login)
            else:
                wechat.delete_user(self.work_email)
        # else:
        #     raise exceptions.Warning(u"企业号尚未配置")

    # 发送文本消息给关注企业号的用户
    def send_text_message(self, content, agentid = None, partyid = None):
        '''
        发送文本消息给关注企业号的用户
        :return:
        发送消息
        参数	必须	说明
            msgtype	是	消息类型，此时固定为：text
            agentid	否	企业应用的id，整型。默认为企业小助手
            partyid	否	部门id，整型。
            content	是	消息内容
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0
        '''
        # 实例化 wechatEnterprise
        try:
            if agentid == None:
                agentid = "0"
            wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid)
            if wechat:
                data = {}
                data['safe'] = u"0"
                data['msgtype'] = u"text"
                if agentid == None:
                    data['agentid'] = "0"
                else:
                    data['agentid'] = agentid
                if self.user_id:
                    data['touser'] = self.user_id.login
                else:
                    data['touser'] = self.work_email
                data['toparty'] = partyid
                data['content'] = content
                wechat.send_msg_to_user(data)
                return self
            else:
                raise exceptions.Warning(u"初始化企业号失败")
        except Exception, e:
            return u'发送消息失败,原因：%s' % e.message

    # 发送图文消息给关注企业号的用户
    def send_news_message(self, agentid=None, title=None, description=None, url=None, picurl=None,partyid=None):
        '''
        发送图文消息给关注企业号的用户
        :return:
        发送消息
        参数	必须	说明
            msgtype	是	消息类型，此时固定为：news
            agentid	是	企业应用的id，整型。可在应用的设置页面查看
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0
            title	否	标题
            description	否	描述
            url	否	点击后跳转的链接。
            picurl	否	图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图640*320，小图80*80。如不填，在客户端不显示图片
            partyid	否	部门ID列表，hr_department的id，多个接收者用‘|’分隔。当touser为@all时忽略本参数
        '''
        # 实例化 wechatEnterprise
        try:
            if agentid == None:
                agentid = "0"
            wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid)
            if wechat:
                data = {}
                data['safe'] = u"0"
                data['msgtype'] = u"news"
                if agentid == None:
                    data['agentid'] = "0"
                else:
                    data['agentid'] = agentid
                if self.user_id:
                    data['touser'] = self.user_id.login
                else:
                    data['touser'] = self.work_email
                data['toparty'] = partyid
                data['url'] = url
                data['title'] = title
                data['description'] = description
                data['picurl'] = picurl
                wechat.send_msg_to_user(data)
                return self
            else:
                raise exceptions.Warning(u"初始化企业号失败")
        except Exception, e:
            return u'发送消息失败,原因：%s' % e.message
