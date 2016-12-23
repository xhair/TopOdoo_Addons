# -*- coding: utf-8 -*-
# © <2016> <gld liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, exceptions
from types import ListType
import time
import logging
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
import os
from openerp import tools
from PIL import Image, ImageDraw, ImageFont

_logger = logging.getLogger(__name__)


class syt_oa_gld_service(models.Model):
    _inherit = "gld.service"
    _description = u'工联单服务微信补丁'

    @api.model
    def create_gld_from_other(self, business_bill_number, subject, content, approver, emergency, business_class):
        # def create_gld_from_other(self):
        '''
        提供接口：为所有业务单据提供创建工联单的接口
        :param business_bill_number: 业务单据编号
        :param subject: 标题
        :param content: 正文
        :param approval: 审批人
        :param emergency: 优先级（急、特急、一般）
        :param business_class:来自于哪个业务类（比如你当前操作的业务对象类，odoo类）
        :return:此方法返回一个工联单对象
        回写方法名：from_gld_message(工联单业务对象，业务单据编号)
        '''

        # business_bill_number = 'QJ001'  # 业务单据编号
        # subject = u'关于刘晶请假的申请'  # 标题
        # content = u'尊敬的领导，您好，本人于2016年2月28日请年假一天，望批准。'  # 正文
        # approver = 1  # 审批人
        # emergency = u'general'  # 优先级（急、特急、一般）
        # business_class = 'yewulei'  # 来自于哪个业务类（比如你当前操作的业务对象类，odoo类）
        #
        # approver = [2, 4, 3]
        apprs = []
        approver_id = ''  # 审批人id
        for appr in approver:
            approver_id += str(appr) + ','
            apprs.append((4, appr))
        vals = {}
        vals['subject'] = subject
        vals['content'] = content
        vals['approver'] = apprs  # 审批人
        vals['emergency'] = emergency
        vals['expiration'] = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400 * 3))  # 截止时间
        vals['relevant_documents'] = business_bill_number
        vals['approvals_user_ids'] = approver_id
        vals['business_object'] = business_class

        # 保存数据
        gld_id = self.env['gld'].create(vals)
        if gld_id:
            # 创建业务单据  返回单号
            write_val = self.create_service(gld_id)
        # 更新业务单号
        gld_id.write({'name': write_val['name'], 'state': 'pending'})
        # 发送消息给审批人
        agentid = self.env['wechat.enterprise.app'].sudo().search([('name', '=', u'工联单')])
        icp = self.env['ir.config_parameter']
        insur_str = icp.get_param('web.base.url')
        for item in approver:
            employee = self.env['hr.employee'].search([('id', '=', int(item))], limit=1)
            if employee:
                descrpition = u"你收到了一张标题为“%s”的工联单，需要您进行审批，请点击查看全文，马上处理！" % (gld_id.subject)
                url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                    gld_id.name, '2', employee.user_id.id)  # 跳转地址，需要和微信保持一致
                employee.send_news_message(agentid.agentid, subject, descrpition, url)
                print('wechat_create_gld_from_other')
                print(employee.id)
        return gld_id

    def find_is_appo_finish(self, gld_id, gld, opinion, shuzi, employee=None):
        '''
        处理判断此工联单是否已经审批完成
        :param gld_id: 工联单ID
        :param gld: 工联单对象
        :return:
        '''
        if gld:
            # 如果没有审批人
            if len(gld.approver) == 0 and len(gld.approver_opinions) == 0:
                # 状态置为草稿
                state_str = u'作废'
                if gld.business_object and gld.relevant_documents:
                    gld.sudo().write({"state": "cancel"})

                else:
                    gld.sudo().write({"state": "draft"})
                    state_str = u'草稿'

                gld.message_post(u"无审批人,系统自动置为[%s]状态." % state_str)
                icp = self.env['ir.config_parameter']
                insur_str = icp.get_param('web.base.url')
                url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                    gld.name, '2', gld.sponsor.user_id.id)
                # url = insur_str + '/WechatGLD/xiangqing?name=%s' % (gld.name)
                title = u'单号：' + gld.name
                description = u'该工联单状态发生改变，已置为[%s]，点击查看全文！' % state_str
                self.env['gld'].get_gld_agentid(gld.sponsor,
                                                       title, description, url)
                # gld.get_gld_agentid(gld.sponsor,
                #                     title,description, url)
                self.return_to_other_document(gld)
                return {}

        # 是否全审批
        a = True
        # 是否全同意
        b = True
        # 判断是否所有人都完成审批
        strs = u'不同意'
        for opin in gld.approver_opinions:
            if opin.opinion == False:
                a = False
            if opin.opinion and str(opin.opinion.encode('utf-8')).find(strs.encode('utf-8')) > -1:
                b = False
        state = 'pass'
        if a:
            # 同意
            if b:
                state = 'through'
            # 不同意
            else:
                state = 'n_through'

        gld.sudo().write({'state': state})
        # SNS信息
        gld_state = gld.state
        employee_name = ''
        if shuzi == 2:
            if employee:
                employee_name = employee.name
        else:
            employee_name = self.env['gld.common'].get_login_user()["name"]
        if gld_state == "through":
            gld.message_post(employee_name + u'审批工联单,审批意见为：' + opinion + u',所有审批人审批完毕')
        else:
            if opinion:
                gld.message_post(employee_name + u'审批工联单,审批意见为：' + opinion)
            else:
                gld.message_post(employee_name + u'审批工联单,审批意见为：不在审批范围')

        dq_state = ''
        icp = self.env['ir.config_parameter']
        insur_str = icp.get_param('web.base.url')
        title = u'单号：' + gld.name
        if gld.state == "pass":
            dq_state = u"审批中"
        elif gld.state == "through":
            dq_state = u"通过"
            for appr in gld.approver:
                url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (gld.name, '2', appr.user_id.id)
                description = u'标题为“%s”的工联单已审核通过，点击查看全文！' % gld.subject
                self.env['gld'].get_gld_agentid(appr,
                                                       title, description, url)
            description = u'标题为“%s”的工联单已审核通过，点击查看全文！' % gld.subject
            urls = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                gld.name, '2', gld.sponsor.user_id.id)
            self.env['gld'].get_gld_agentid(gld.sponsor,
                                                   title, description, urls)
        elif gld.state == "n_through":
            dq_state = u"不通过"
            for appr in gld.approver:
                url_ = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (gld.name, '2', appr.user_id.id)
                description = u'标题为“%s”的工联单审核不通过，点击查看全文' % gld.subject
                self.env['gld'].get_gld_agentid(appr, title, description, url_)
            description = u'标题为“%s”的工联单审核不通过，点击查看全文' % gld.subject
            urls = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                gld.name, '2', gld.sponsor.user_id.id)
            self.env['gld'].get_gld_agentid(gld.sponsor,
                                                   title, description, urls)
        self.return_to_other_document(gld)
