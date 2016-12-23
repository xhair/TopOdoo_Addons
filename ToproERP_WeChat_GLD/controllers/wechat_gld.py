# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from json import *
import logging
import string
import hashlib
import urllib2
from openerp import http
from openerp.http import request
import Cookie
import base64
import pytz
import datetime
from time import time, localtime
from ToproERP_Wechat_Enterprises.models.wechat_enterprise_basic import WeChatEnterprise
import time, json, random
from ToproERP_Wechat_Enterprises.models import wechat_enterprise
import urlparse

import werkzeug.utils
import werkzeug.wrappers

_logger = logging.getLogger(__name__)


class WechatGLD(http.Controller):
    '''
    用于接收微信发过来的任何消息，并转发给相应的业务类进行处理
    '''

    __check_str = 'NDOEHNDSY#$_@$JFDK:Q{!'

    # 跳转SNS页面
    @http.route('/WechatGLD/get_sns_html', type='http', auth="public", csrf=False)
    def get_sns_html(self, name):
        values = {"name": name}
        return request.render('ToproERP_WeChat_GLD.get_sns_html', values)

    # 获得当前单据的日志SNS信息
    @http.route('/WechatGLD/get_sns', type='http', auth="public", csrf=False)
    def get_sns(self, gld_name):
        temp_list = []
        gld = request.env['syt.oa.gld'].sudo().search([('name', '=', gld_name)])
        message = request.env['mail.message'].sudo().search([('res_id', '=', gld.id), ('model', '=', 'syt.oa.gld')])
        if message:
            for value in message:
                temp_item = {}
                employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(value.create_uid))])
                # temp_item['operator'] = employee.name  # 操作人
                temp_item['id'] = employee.id  # 员工id
                temp_item['name'] = employee.name  # 操作人
                temp_item['email'] = employee.work_email  # 员工邮箱
                temp_item['body'] = str(value.body).replace("<p>", "").replace("</p>", "")  # 内容
                timeArray = time.strptime(str(value.create_date), "%Y-%m-%d %H:%M:%S")
                timeStamp = int(time.mktime(timeArray))
                create_time = timeStamp + 8 * 60 * 60  # 加8个小时
                timeArray = time.localtime(create_time)
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                temp_item['time'] = otherStyleTime  # 更新时间
                temp_list.append(temp_item)
            return JSONEncoder().encode(temp_list)

    # 获得当前登录人的个人信息：图片 公司 部门 姓名
    @http.route('/WechatGLD/get_user_image', type='http', auth="public", csrf=False)
    def get_user_image(self, userid):
        temp_list = []
        user = request.env['hr.employee'].sudo().search([('user_id', '=', int(userid))])
        image = '/web/binary/image?model=hr.employee&field=image&id=' + str(user.id) + '&resize='
        if user:
            temp_item = {}
            temp_item['image'] = image
            temp_item['id'] = user.id
            temp_item['name'] = user.name
            temp_item['company_name'] = user.department_id.company_id.name
            temp_item['dept'] = user.department_id.name
            temp_item['job_name'] = user.job_id.name
            temp_list.append(temp_item)
            return JSONEncoder().encode(temp_list)

    # 获取我的工联单第一个页面：模板类型 模板 标题 正文 下一步
    @wechat_enterprise.wechat_login
    @http.route('/WechatGLD/get_add_gld_first_page', type='http', auth="public", csrf=False)
    def get_add_gld_first_page(self, *args, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.session['uid'])])
        temp_type = request.env['syt.oa.gld.template.type'].sudo().search([])
        return request.render('ToproERP_WeChat_GLD.get_add_gld_first_page', {"user": user, "temp_type": temp_type})

    # 获取我的工联单第二个页面：紧急程度 添加附件 添加审批人 添加抄送人 保存  保存并提交审批
    @http.route('/WechatGLD/get_add_gld_second_page', type='http', auth="public", csrf=False)
    def get_add_gld_second_page(self, template_type, template, title, text, emergency, userid):
        user = request.env['res.users'].sudo().search([('id', '=', int(userid))])
        return request.render('ToproERP_WeChat_GLD.get_add_gld_second_page',
                              {"template_type": template_type, "template": template,
                               "title": title, "text": text, "emergency": emergency, "user": user})

    # 我发起的工联单 页面
    @wechat_enterprise.wechat_login
    @http.route('/WechatGLD/list_faqi', type='http', auth="public", csrf=False)
    def list_faqi(self, *args, **kw):
        data = request.env['syt.oa.gld'].sudo().search([('sponsor.user_id', '=', request.session['uid'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.session['uid'])])
        return request.render('ToproERP_WeChat_GLD.list_faqi', {"user": user, "data": data})

    # 待办工联单列表 页面
    @wechat_enterprise.wechat_login
    @http.route('/WechatGLD/list_daiban', type='http', auth="public", csrf=False)
    def list_daiban(self, *args, **kw):
        data = request.env['syt.oa.gld'].sudo().search(
            ['|',
             '&', ('copy_users_dy_ids.user_id', '=', request.session['uid']), ('state', '=', 'through'),
             '&', ('approver.user_id.id', '=', request.session['uid']), ('state', 'in', ('pending', 'pass'))])
        user = request.env['res.users'].sudo().search([('id', '=', request.session['uid'])])
        return request.render('ToproERP_WeChat_GLD.list_daiban', {"user": user, "data": data})

    # 已办工联单列表 页面
    @wechat_enterprise.wechat_login
    @http.route('/WechatGLD/list_yiban', type='http', auth="public", csrf=False)
    def list_yiban(self, *args, **kw):
        data = request.env['syt.oa.gld'].sudo().search([('yi_approver_user_ids.user_id', '=', request.session['uid'])])
        user = request.env['res.users'].sudo().search([('id', '=', request.session['uid'])])
        return request.render('ToproERP_WeChat_GLD.list_yiban', {"user": user, "data": data})

    # 工联单列表的展示（我的，待办，已办）
    def onload_list(self, obj, user_id, copy_users=None):
        temp_type_list = []
        if obj:
            for value_obj in obj:
                temp_type_list.append(self.get_list(user_id, value_obj, copy_users))
        if copy_users:
            for value_copy in copy_users:
                temp_type_list.append(self.get_list(user_id, value_copy, copy_users))
        return JSONEncoder().encode(temp_type_list)

    def get_list(self, user_id, value, copy_users):
        temp_item = {}
        temp_item['user_id'] = user_id  # user_id
        temp_item['id'] = value.create_uid.id  # 创建员工ID
        temp_item['user_name'] = value.create_uid.name  # 创建员工姓名
        temp_item['name'] = value.name  # 单号
        temp_item['company_name'] = value.company_id.name  # 公司
        temp_item['dept'] = value.subject  # 标题
        timeArray = time.strptime(str(value.write_date), "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        create_time = timeStamp + 8 * 60 * 60  # 加8个小时
        timeArray = time.localtime(create_time)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        temp_item['write_date'] = otherStyleTime  # 创建更新时间
        temp_item['state'] = value.state  # 状态
        if copy_users:
            temp_item['copy_users'] = 'yes'  # 区别 判断是抄送人还是审批人
        else:
            temp_item['copy_users'] = 'no'  # 区别 判断是抄送人还是审批人
        return temp_item

    # 我发起的工联单 数据展示
    @http.route('/WechatGLD/get_faqi_list', type='http', auth="public", csrf=False)
    def get_faqi_list(self, userid):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(userid))])
        obj = request.env['syt.oa.gld'].sudo().search([('create_uid', '=', int(userid))], limit=5)
        return self.onload_list(obj, userid)

    # 我发起的工联单 每次添加5条数据
    @http.route('/WechatGLD/add_faqi_list', type='http', auth="public", csrf=False)
    def add_faqi_list(self, userid, number):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(userid))])
        obj = request.env['syt.oa.gld'].sudo().search([('create_uid', '=', int(userid))], limit=5, offset=int(number))
        return self.onload_list(obj, userid)

    # 保存审批意见 同意与不同意 按钮
    @http.route('/WechatGLD/save_opinion', type='http', auth="public", csrf=False)
    def save_opinion(self, wechat_gldid, opinion, check_state, userid):
        gld_bean = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(userid))])
        return request.env['syt.oa.gld.opinion'].sudo(userid).save_opinion_service_wechat(gld_bean.id, opinion,
                                                                                          check_state,
                                                                                          employee, 2)

    # 待办工联单列表 数据展示
    @http.route('/WechatGLD/get_daiban_list', type='http', auth="public", csrf=False)
    def get_daiban_list(self, userid):
        copy_users = request.env['syt.oa.gld'].sudo().search(
            [('copy_users_dy_ids.user_id', '=', int(userid)), ('state', '=', 'through')])
        obj = request.env['syt.oa.gld'].sudo().search(
            ['|',
             '&', ('copy_users_dy_ids.user_id', '=', userid), ('state', '=', 'through'),
             '&', ('approver.user_id.id', '=', userid), ('state', 'in', ('pending', 'pass'))])
        return self.onload_list(obj, userid, copy_users)

    # 待办工联单列表 每次添加5条数据
    @http.route('/WechatGLD/add_daiban_list', type='http', auth="public", csrf=False)
    def add_daiban_list(self, userid, number):
        copy_users = request.env['syt.oa.gld'].sudo().search(
            [('copy_users_dy_ids.user_id', '=', int(userid)), ('state', '=', 'through')])
        obj = request.env['syt.oa.gld'].sudo().search(
            ['|',
             '&', ('copy_users_dy_ids.user_id', '=', userid), ('state', '=', 'through'),
             '&', ('approver.user_id.id', '=', userid), ('state', 'in', ('pending', 'pass'))], limit=5,
            offset=int(number))
        return self.onload_list(obj, userid, copy_users)

    # 已办工联单列表 数据展示
    @http.route('/WechatGLD/get_yiban_list', type='http', auth="public", csrf=False)
    def get_yiban_list(self, userid):
        obj = request.env['syt.oa.gld'].sudo().search(
            ['|', ('copy_users_yy_ids.user_id', '=', int(userid)), ('yi_approver_user_ids.user_id', '=', int(userid))],
            limit=5)
        return self.onload_list(obj, userid)

    # 已办工联单列表 每次添加5条数据
    @http.route('/WechatGLD/add_yiban_list', type='http', auth="public", csrf=False)
    def add_yiban_list(self, userid, number):
        obj = request.env['syt.oa.gld'].sudo().search(
            ['|', ('copy_users_yy_ids.user_id', '=', int(userid)), ('yi_approver_user_ids.user_id', '=', int(userid))],
            limit=5,
            offset=int(number))
        return self.onload_list(obj, userid)

    # 根据输入的名称查询员工
    @http.route('/WechatGLD/get_user_by_name', type='http', auth="public", csrf=False)
    def get_user_by_name(self, name):
        obj = request.env['hr.employee'].sudo().search([('name', 'ilike', name)])
        temp_type_list = []
        if obj:
            for value in obj:
                temp_item = {}
                temp_item['id'] = value.id
                temp_item['name'] = value.name
                temp_item['company_name'] = value.company_id.name
                temp_item['dept'] = value.department_id.name
                temp_item['phone'] = value.mobile_phone
                temp_item['job_name'] = value.job_id.name
                image = '/web/binary/image?model=hr.employee&field=image&id=' + str(obj.id) + '&resize='
                temp_item['image'] = image
                temp_type_list.append(temp_item)
            return JSONEncoder().encode(temp_type_list)
        else:
            return "2"

    # 工联单详情页面路径
    @http.route('/WechatGLD/xiangqing', type='http', auth="public", csrf=False)
    def xiangqing(self, name, qubie=None, userid=None):
        gld_obj = request.env['syt.oa.gld'].sudo().search([('name', '=', name.lstrip())])
        if_cs = False
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(userid))])
        if gld_obj.state == 'through' and gld_obj.copy_users_dy_ids:
            for dy in gld_obj['copy_users_dy_ids']:
                if employee.id == dy.id:
                    if_cs = True
                    break
        if if_cs:
            request.env['syt.oa.gld'].sudo(userid).read_gld_service(gld_obj, 2, employee)
        message = request.env['mail.message'].sudo().search([('res_id', '=', gld_obj.id), ('model', '=', 'syt.oa.gld')])
        curr_approver_is_luser = False
        uid_is_approval = False
        if (employee.id == gld_obj.sponsor.id):
            curr_approver_is_luser = True
        # 审批人是否为当前登录人

        # 没有审批意见
        for opina in gld_obj.approver_opinions:
            if (request.env['hr.employee'].search([('id', '=', opina.approver.id)])["user_id"]["id"] == int(userid)):
                if (opina.opinion == False):
                    uid_is_approval = True

        return request.render('ToproERP_WeChat_GLD.xiangqing', {'gld_obj': gld_obj,
                                                                'userid': userid,
                                                                'attachment': len(gld_obj.attachment_ids),
                                                                'opinions': len(gld_obj.approver_opinions),
                                                                'copy_users': len(gld_obj.copy_users),
                                                                'messages': len(message),
                                                                'curr_approver_is_luser': curr_approver_is_luser,
                                                                'uid_is_approval': uid_is_approval})

    # 工联单详情审批意见页面路径
    @http.route('/WechatGLD/xiangqing_opinion', type='http', auth="public", csrf=False)
    def xiangqing_opinion(self, name, qubie=None):
        gld_obj = request.env['syt.oa.gld'].sudo().search([('name', '=', name.lstrip())])
        return request.render('ToproERP_WeChat_GLD.xiangqing_opinion', {'gld_obj': gld_obj})

    # 查询工联单审批意见的页面路径
    @http.route('/WechatGLD/select_opinion', type='http', auth="public", csrf=False)
    def select_opinion(self, name, qubie):
        values = {"name": name, "shuzi": qubie}
        gld_obj = request.env['syt.oa.gld'].sudo().search([('name', '=', name)])
        return request.render('ToproERP_WeChat_GLD.select_opinion',
                              {'value': values, 'opinion': gld_obj.approver_opinions})

    @http.route('/WechatGLD/get_enclosure', type='http', auth="public", csrf=False)
    def get_enclosure(self, name):
        gld_obj = request.env['syt.oa.gld'].sudo().search([('name', '=', name)])
        if gld_obj:
            attachment_list = []
            for attachment in gld_obj.attachment_ids:
                item = {}
                item['id'] = attachment.id
                fname, full_path = request.env['ir.attachment']._get_path('', attachment.checksum)
                item['db_datas'] = full_path
                attachment_list.append(item)
            return JSONEncoder().encode(attachment_list)
        else:
            return "2"

    # 查询工联单审批意见的数据展示
    @http.route('/WechatGLD/get_opinion', type='http', auth="public", csrf=False)
    def get_opinion(self, name, shuzi):
        opinion = request.env['syt.oa.gld.opinion'].sudo().search([('gld_id', '=', name)])
        if opinion:
            opinion_list = []
            for value in opinion:
                item = {}
                item['id'] = value.approver.id
                item['name'] = value.approver.name
                item['opinion'] = value.opinion
                timeArray = time.strptime(str(value.appov_date), "%Y-%m-%d %H:%M:%S")
                timeStamp = int(time.mktime(timeArray))
                create_time = timeStamp + 8 * 60 * 60  # 加8个小时
                timeArray = time.localtime(create_time)
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                item['time'] = otherStyleTime
                item['dept'] = value.approver.department_id.name
                item['company'] = value.approver.company_id.name
                opinion_list.append(item)
            return JSONEncoder().encode(opinion_list)
        else:
            return "2"

    # 工联单详情页面数据展示
    @http.route('/WechatGLD/get_gld_info', type='http', auth="public", csrf=False)
    def get_gld_info(self, name):
        temp_type = request.env['syt.oa.gld'].sudo().search([('name', '=', name.lstrip())])
        copy_users = request.env['syt.oa.gld'].sudo().search([('copy_users.user_id', '=', request.session['uid'])])
        temp_type_list = []
        if temp_type:
            for value in temp_type:
                temp_item = {}
                temp_item['name'] = value.name  # 单号
                temp_item['company_name'] = value.company_id.name  # 公司
                temp_item['dept'] = value.dept  # 部门
                temp_item['id'] = value.create_uid.id  # 创建员工ID
                temp_item['user_name'] = value.create_uid.name  # 创建员工姓名
                timeArray = time.strptime(str(value.create_date), "%Y-%m-%d %H:%M:%S")
                timeStamp = int(time.mktime(timeArray))
                create_time = timeStamp + 8 * 60 * 60  # 加8个小时
                timeArray = time.localtime(create_time)
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                temp_item['write_date'] = otherStyleTime  # 创建更新时间
                temp_item['state'] = value.state  # 状态
                temp_item['subject'] = value.subject  # 标题
                temp_item['content'] = value.content  # 正文
                if copy_users:
                    temp_item['copy_users'] = 'yes'  # 区别 判断是抄送人还是审批人
                else:
                    temp_item['copy_users'] = 'no'  # 区别 判断是抄送人还是审批人
                temp_type_list.append(temp_item)
            return JSONEncoder().encode(temp_type_list)

    # 获取模板类型
    @http.route('/WechatGLD/get_temp_type', type='http', auth="public", csrf=False)
    def get_temp_type(self):
        temp_type = request.env['syt.oa.gld.template.type'].sudo().search([])
        temp_type_list = []
        for value in temp_type:
            temp_item = {}
            temp_item['id'] = value.id
            temp_item['name'] = value.name
            temp_type_list.append(temp_item)
        json = JSONEncoder().encode(temp_type_list)
        return json

    # 根据模板类型获取模板
    @http.route('/WechatGLD/get_temp', type='http', auth="public", csrf=False)
    def get_temp(self, temp_type_id):
        temp = request.env['syt.oa.gld.template'].sudo().search([('temp_type', '=', int(temp_type_id))])
        temp_list = []
        for value in temp:
            temp_item = {}
            temp_item['id'] = value.id
            temp_item['name'] = value.name
            temp_list.append(temp_item)
        return JSONEncoder().encode(temp_list)

    # 保存工联单
    @http.route('/WechatGLD/save', type='http', auth="public", csrf=False)
    def save(self, template_type, template, title, text, urgency, approver, attachment_ids, userid):
        self.save_public(template_type, template, title, text, urgency, approver, attachment_ids, userid, 2)

    # 保存并提交工联单
    @http.route('/WechatGLD/save_and_submit', type='http', auth="public", csrf=False)
    def save_and_submit(self, template_type, template, title, text, urgency, approver, attachment_ids, userid):
        self.save_public(template_type, template, title, text, urgency, approver, attachment_ids, userid, 1)

    def save_public(self, template_type, template, title, text, urgency, approver, attachment_ids, userid, save_type):
        '''
        创建工联单的公共方法：为 保存、保存并提交的按钮提供创建工联单的方法
        :param template_type:模板类型
        :param template: 模板
        :param title: 标题
        :param text: 正文
        :param urgency: 紧急程序
        :param approver: 审批人
        :param attachment_ids: 附件
        :param userid: 用户Id
        :param save_type: 代表当前是通过保存还是保存并提交过来的
        :return:
        '''
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(userid))])
        approver_if_self = False  # 审批人中是否包含自己
        approver_arry = approver.split(",")
        apprs = []
        approver_id = ''  # 审批人id
        for appr in approver_arry:
            approver_id += str(appr) + ','
            if appr:
                apprs.append((4, int(appr)))
            if int(appr) == employee.id:
                approver_if_self = True
        if approver_if_self:
            return "3"
        vals = {}
        vals['sponsor'] = employee.id
        vals['dept'] = employee.department_id.name
        vals['message_follower_ids'] = False
        vals['message_ids'] = False
        vals['emergency'] = urgency
        vals['approver'] = apprs
        if template_type != "0":
            vals['temp_type'] = int(template_type)
        if template != "0":
            vals['gld_temp'] = int(template)
        vals['expiration'] = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400 * 3))  # 截止时间
        vals['subject'] = title
        text = str(text).replace("$", "<br>")
        vals['content'] = text
        # 附件图片
        if attachment_ids != "0":
            attachment_arry = attachment_ids.split(",")
            attachments = []
            for attachment in attachment_arry:
                if attachment != "":
                    attachments.append((4, int(attachment)))
            vals['attachment_ids'] = attachments

        request.uid = userid
        gld_bean = request.env['syt.oa.gld'].sudo(userid).create(vals, "wechat")
        if gld_bean:
            if gld_bean.attachment_ids:
                for attachment_ in gld_bean.attachment_ids:
                    # 给图片打水印
                    # self.make_watermark(attachment_, gld_bean.name)
                    # request.env['syt.oa.gld.service'].sudo().make_watermark(attachment_, gld_bean.name)
                    request.env['play.watermark'].make_watermark(obj=gld_bean, number=gld_bean.name)

        if save_type == 1:
            gld = request.env['syt.oa.gld'].sudo().search([('id', '=', int(gld_bean.id))])
            id = 0
            if gld:
                id = gld.sudo(userid).write({"state": "pending"})
                for appr in gld.approver:
                    icp = request.env['ir.config_parameter']
                    insur_str = icp.get_param('web.base.url')
                    url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                        gld.name, '2', appr.user_id.id)  # 跳转地址，需要和微信保持一致
                    description = u"%s提交了一张标题为“%s”的工联单，需要您进行审批，请点击查看全文，马上处理！" % (gld.sponsor.name, gld.subject)
                    request.env['syt.oa.gld'].get_gld_agentid(appr, u'单号：' + gld.name, description, url)
            if id:
                return "1"  # True
            else:
                return "0"  # False

    # 获得前五位审批意见不为空的审批人
    @http.route('/WechatGLD/get_approver', type='http', auth="public", csrf=False)
    def get_approver(self, user_id):
        approver = request.env['syt.oa.gld.service'].get_approver(user_id)
        employee_list = []
        for appr in approver:
            employee = request.env['hr.employee'].sudo().search([('id', '=', int(appr))], limit=5)
            employee_item = {}
            if employee.mobile_phone == False:
                employee.mobile_phone = "";
            employee_item['id'] = str(employee.id) + ','
            employee_item['name'] = employee.name
            employee_item['mobile_phone'] = employee.mobile_phone
            employee_item['company_name'] = employee.department_id.company_id.name
            employee_item['approver_dept'] = employee.department_id.name
            employee_list.append(employee_item)
        return JSONEncoder().encode(employee_list)

    # 根据模板类型获取标题、正文、紧急程度
    @http.route('/WechatGLD/get_title', type='http', auth="public", csrf=False)
    def get_title(self, temp_id):
        approver = request.env['syt.oa.gld.template'].sudo().search([('id', '=', int(temp_id))])
        temp_list = []
        for value in approver:
            temp_item = {}
            temp_item['subject'] = value.subject
            temp_item['content'] = value.content
            # temp_item['content'] = base64.encodestring(value.content)
            temp_item['emergency'] = value.emergency
            temp_list.append(temp_item)
        return JSONEncoder().encode(temp_list)

    # 提交审批按钮
    @http.route('/WechatGLD/gld_state_sent', type='http', auth="public", csrf=False)
    def gld_state_sent(self, wechat_gldid, userid):
        _logger.info(u'工联单单号(%s)' % wechat_gldid)
        gld_bean = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        _logger.info(u'微信点击提交审批时的工联单对象(%s)' % gld_bean)
        if gld_bean.approver_opinions:
            approver_ids = []
            for appr in gld_bean.approver_opinions:
                approver_ids.append(int(appr.approver.id))

            # approver_ids = str(approver_ids).replace('[', '(').replace(']', ')')
            employee_obj = request.env["hr.employee"].sudo().search([('id', 'in', approver_ids)])

            _logger.info(u'微信点击提交审批时的审批人列表(%s)' % employee_obj)
            request.env['syt.oa.gld'].sudo().gld_state_sent_service(gld_bean, employee_obj)
            return "1"
        else:
            return "2"

    # 继续审批按钮
    @http.route('/WechatGLD/gld_finish_to_pass', type='http', auth="public", csrf=False)
    def gld_finish_to_pass(self, wechat_gldid):
        gld_bean = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        request.env['syt.oa.gld'].gld_finish_to_pass_service(gld_bean)
        return "1"

    # 作废按钮
    @http.route('/WechatGLD/gld_state_cancel', type='http', auth="public", csrf=False)
    def gld_state_cancel(self, wechat_gldid, userid):
        gld_bean = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        request.env['syt.oa.gld'].sudo(userid).gld_state_cancel_service(gld_bean)
        return "1"

    # 已阅按钮
    @http.route('/WechatGLD/read_gld_service', type='http', auth="public", csrf=False)
    def read_gld_service(self, wechat_gldid, userid):
        gld_bean = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        request.env['syt.oa.gld'].sudo(userid).read_gld_service(gld_bean)
        return "1"

    # 置为草稿按钮
    @http.route('/WechatGLD/gld_state_draft', type='http', auth="public", csrf=False)
    def gld_state_draft(self, wechat_gldid, userid):
        gld_bean = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        if gld_bean:
            request.env['syt.oa.gld'].sudo(userid).gld_state_draft_service(gld_bean)
            return "1"
        else:
            return "2"

    # 不在本人审批范围按钮
    @http.route('/WechatGLD/waiver', type='http', auth="public", csrf=False)
    def waiver(self, wechat_gldid, userid):
        gld_bean = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', int(userid))])
        if gld_bean:
            request.env['syt.oa.gld'].sudo(userid).waiver_service(gld_bean, userid, employee)
            return "1"
        else:
            return "2"

    # 展示添加审批人页面
    @http.route('/WechatGLD/view_appr', type='http', auth="public", csrf=False)
    def view_appr(self, no, name, userid):
        values = {"no": no, "name": name, "userid": userid}
        return request.render('ToproERP_WeChat_GLD.view_appr', values)

    # 展示查看抄送人页面
    @http.route('/WechatGLD/select_appr_copy_user', type='http', auth="public", csrf=False)
    def select_appr_copy_user(self, no):
        values = {"no": no}
        gld = request.env['syt.oa.gld'].sudo().search([('name', '=', no)])
        return request.render('ToproERP_WeChat_GLD.select_appr_copy_user',
                              {'values': values, 'people': gld.copy_users})

    # 获得当前单据的所有抄送人
    @http.route('/WechatGLD/get_copy_user', type='http', auth="public", csrf=False)
    def get_copy_user(self, wechat_gldid):
        gld = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        temp_list = []
        if gld:
            for copy_user in gld.copy_users:
                # request.env['hr.employee'].search([('id', '=', int(employee_id))])
                temp_item = {}
                temp_item['name'] = copy_user.name
                temp_item['company_name'] = copy_user.department_id.company_id.name
                temp_item['dept'] = copy_user.department_id.name
                temp_item['job_name'] = copy_user.job_id.name
                image = '/web/binary/image?model=hr.employee&field=image&id=' + str(copy_user.id) + '&resize='
                temp_item['image'] = image
                temp_list.append(temp_item)
        return JSONEncoder().encode(temp_list)

    # 通过按钮添加审批人/抄送人 按钮
    @http.route('/WechatGLD/add_approver_service', type='http', auth="public", csrf=False)
    def add_approver_service(self, wechat_gldid, employee_id, name, userid):
        gld_bean = request.env['syt.oa.gld'].sudo().search([('name', '=', wechat_gldid)])
        employee = request.env['hr.employee'].sudo().search([('id', '=', int(employee_id))])
        request.uid = userid
        if name == u"添加抄送人":
            result = request.env['syt.oa.gld.add.peoper.wizard'].sudo(userid).add_copy_peoper_service(gld_bean,
                                                                                                      employee, '',
                                                                                                      2)
        elif name == u"添加审批人":
            result = request.env['syt.oa.gld.add.approver.wizard'].sudo(userid).add_approver_service(gld_bean, employee,
                                                                                                     2)
        if result == "2":
            return "2"
        elif result == "3":
            return "3"
        else:
            return "1"

    @http.route('/WechatGLD/get_signature', type='http', auth="public", csrf=False)
    def get_signature(self, url):
        '''
        获得微信的ticket 缓存起来
        :return:
        '''
        cookie = Cookie.SimpleCookie()
        # access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wx0046935c06f7c27e&corpsecret=fLuTp-KCwaG-HAPcsKZch0xNkNV2ahjMPmi1S4F_LnlP8rkJmsx7jVc931ljr46A'
        access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wxc1317b61e7e122aa&corpsecret=EGjHS5l3ee0gBSvr29zgZN2HqG4r2tPbtr-LBpRqgoEC-4EqQrvPqQQGXrc1QxpH'
        request_ = urllib2.Request(access_token_url)
        opener = urllib2.build_opener()
        conn = opener.open(request_)
        access_token_list = conn.read()
        access_token_list = json.loads(access_token_list)
        if len(cookie) == 0:
            cookie["access_token"] = access_token_list["access_token"]

        request.session['access_token'] = access_token_list["access_token"]
        if len(cookie) > 0:
            cookie_ticket = Cookie.SimpleCookie()
            ticket_url = 'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token=' + cookie[
                "access_token"].value
            request_ = urllib2.Request(ticket_url)
            opener = urllib2.build_opener()
            conn = opener.open(request_)
            ticket_list = conn.read()
            ticket_list = json.loads(ticket_list)
            if len(cookie_ticket) == 0:
                cookie_ticket["ticket"] = ticket_list["ticket"]
            ret_list = []
            ret = {}
            ret["nonceStr"] = self.__create_nonce_str()  # 创建随机字符串
            ret["jsapi_ticket"] = cookie_ticket["ticket"].value
            ret["timestamp"] = self.__create_timestamp()  # 创建时间戳
            ret["url"] = url
            signature = self.sign(ret)
            ret["signature"] = signature
            ret_list.append(ret)
            return JSONEncoder().encode(ret_list)

    def __create_nonce_str(self):
        '''
        创建随机字符串 nonceStr
        :return:
        '''
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        '''
        创建时间戳 timestamp
        :return:
        '''
        return int(time.time())

    def sign(self, ret):
        '''
        返回一个加密的signature 签名
        :return:
        '''
        string = '&'.join(['%s=%s' % (key.lower(), ret[key]) for key in sorted(ret)])
        signature = hashlib.sha1(string).hexdigest()
        return signature

    def _compute_checksum(self, bin_data):
        """ compute the checksum for the given datas
            :param bin_data : datas in its binary form
        """
        # an empty file has a checksum too (for caching)
        return hashlib.sha1(bin_data or '').hexdigest()

    @http.route('/WechatGLD/downloadImage', type='http', auth="public", csrf=False)
    def downloadImage(self, media_id):
        cookie = Cookie.SimpleCookie()
        # access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wx0046935c06f7c27e&corpsecret=fLuTp-KCwaG-HAPcsKZch0xNkNV2ahjMPmi1S4F_LnlP8rkJmsx7jVc931ljr46A'
        access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wxc1317b61e7e122aa&corpsecret=EGjHS5l3ee0gBSvr29zgZN2HqG4r2tPbtr-LBpRqgoEC-4EqQrvPqQQGXrc1QxpH'
        access_token_request = urllib2.Request(access_token_url)
        opener = urllib2.build_opener()
        conn = opener.open(access_token_request)
        access_token_list = conn.read()
        access_token_list = json.loads(access_token_list)
        if len(cookie) == 0:
            cookie["access_token"] = access_token_list["access_token"]
        downloadImage_url = 'https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token=' + cookie[
            "access_token"].value + '&media_id=' + media_id + ''
        # wechat = WeChatEnterprise(agentid=1)
        # file = wechat.get_media(media_id)

        wechat = request.env['wechat.enterprise.config'].get_wechat()
        file = wechat.get_media(media_id)
        url = downloadImage_url
        f = urllib2.urlopen(url)
        attachment = request.env['ir.attachment']
        verification_code = random.randint(1000, 9999)  # 4位随机码
        vals = {}
        vals["db_datas"] = file
        vals['datas'] = base64.encodestring(f.read())
        vals['name'] = str(verification_code) + ".jpg"
        vals['datas_fname'] = str(verification_code) + ".jpg"
        vals['type'] = "binary"
        vals['index_content'] = "(u'image',)"
        vals['mimetype'] = "image/jpeg"
        vals['res_model'] = "syt.oa.gld"
        attachment_bean = attachment.sudo().create(vals)
        attachment_bean_vals = {}
        if attachment_bean:
            attachment_bean_vals["attachment_id"] = attachment_bean.id
        else:
            attachment_bean_vals["attachment_id"] = "0"
        attachment_bean_vals["image_name"] = attachment_bean.name
        return JSONEncoder().encode(attachment_bean_vals)

    # 查询工联单附件的页面路径
    @http.route('/WechatGLD/view_enclosure', type='http', auth="public", csrf=False)
    def view_enclosure(self, name, *args, **kw):
        gld_obj = request.env['syt.oa.gld'].sudo().search(
            [('name', '=', name)])
        attachments = []
        if gld_obj:
            for atta_item in gld_obj.attachment_ids:
                attachments_obj = http.request.env['ir.attachment'].sudo().search(
                    [('id', '=', atta_item.id)])
                attachments.append(attachments_obj)
        # attachments_obj = http.request.env['ir.attachment'].sudo().search(
        #     [('id', '=', atta_item.id)])
        return http.request.render('ToproERP_WeChat_GLD.select_enclosure',
                                   {'attachments': attachments})

    # 取附件的详情页面 大图
    @http.route('/WechatGLD/enclosure_info', type='http', auth="public", csrf=False)
    def enclosure_info(self, id, *args, **kwargs):
        attachments = http.request.env['ir.attachment'].sudo().search(
            [('id', '=', id)])
        return http.request.render('ToproERP_WeChat_GLD.enclosure_info',
                                   {'attachments': attachments})

    def binary_content(xmlid=None, model='ir.attachment', id=None, field='datas', unique=False, filename=None,
                       filename_field='datas_fname', download=False, mimetype=None,
                       default_mimetype='application/octet-stream', env=None):
        return request.registry['ir.http'].binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field,
            download=download, mimetype=mimetype, default_mimetype=default_mimetype, env=env)

    @http.route(['/ToproERP_WeChat_GLD/content',
                 '/ToproERP_WeChat_GLD/content/<string:xmlid>',
                 '/ToproERP_WeChat_GLD/content/<string:xmlid>/<string:filename>',
                 '/ToproERP_WeChat_GLD/content/<int:id>',
                 '/ToproERP_WeChat_GLD/content/<int:id>/<string:filename>',
                 '/ToproERP_WeChat_GLD/content/<int:id>-<string:unique>',
                 '/ToproERP_WeChat_GLD/content/<int:id>-<string:unique>/<string:filename>',
                 '/ToproERP_WeChat_GLD/content/<string:model>/<int:id>/<string:field>',
                 '/ToproERP_WeChat_GLD/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http',
                auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas', filename=None,
                       filename_field='datas_fname', unique=None, mimetype=None, download=None, data=None, token=None):
        status, headers, content = self.binary_content(xmlid=xmlid, model=model, id=id, field=field, unique=unique,
                                                       filename=filename, filename_field=filename_field,
                                                       download=download, mimetype='application/pdf')
        if status == 304:
            response = werkzeug.wrappers.Response(status=status, headers=headers)
        elif status == 301:
            return werkzeug.utils.redirect(content, code=301)
        elif status != 200:
            response = request.not_found()
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        if token:
            response.set_cookie('fileToken', token)
        return response


        #
        #
        # def binary_content(xmlid=None, model='ir.attachment', id=None, field='datas', unique=False, filename=None,
        #                    filename_field='datas_fname', download=False, mimetype=None,
        #                    default_mimetype='application/octet-stream', env=None):
        #     return request.registry['ir.http'].binary_content(
        #         xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
        #         filename_field=filename_field,
        #         download=download, mimetype=mimetype, default_mimetype=default_mimetype, env=env)
        #
        # @http.route(['/web/content',
        #              '/web/content/<string:xmlid>',
        #              '/web/content/<string:xmlid>/<string:filename>',
        #              '/web/content/<int:id>',
        #              '/web/content/<int:id>/<string:filename>',
        #              '/web/content/<int:id>-<string:unique>',
        #              '/web/content/<int:id>-<string:unique>/<string:filename>',
        #              '/web/content/<string:model>/<int:id>/<string:field>',
        #              '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
        # def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas', filename=None,
        #                    filename_field='datas_fname', unique=None, mimetype=None, download=None, data=None, token=None):
        #     status, headers, content = self.binary_content(xmlid=xmlid, model=model, id=id, field=field, unique=unique,
        #                                                    filename=filename, filename_field=filename_field,
        #                                                    download=download, mimetype=mimetype)
        #     if status == 304:
        #         response = werkzeug.wrappers.Response(status=status, headers=headers)
        #     elif status == 301:
        #         return werkzeug.utils.redirect(content, code=301)
        #     elif status != 200:
        #         response = request.not_found()
        #     else:
        #         content_base64 = base64.b64decode(content)
        #         headers.append(('Content-Length', len(content_base64)))
        #         response = request.make_response(content_base64, headers)
        #     if token:
        #         response.set_cookie('fileToken', token)
        #     return response
