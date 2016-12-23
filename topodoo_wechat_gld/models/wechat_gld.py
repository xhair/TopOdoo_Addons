# -*- coding: utf-8 -*-
# © <2016> <gld liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, api, exceptions

_logger = logging.getLogger(__name__)


class WechatGld(models.Model):
    _description = u'工联单微信版'
    _inherit ='gld'
    _order = 'name desc'

    def get_gld_agentid(self, user_list, content, description, url):
        """
        根据工联单名字获取授权方应用ID  并发送信息给微信中
        :param user_list:发送给谁，员工id
        :param content: 发送内容
        :return:
        """
        # 获取工联单的微信编号 只发送到工联单模块里面
        agentid = self.env['wechat.enterprise.app'].sudo().search([('name', '=', u'工联单')])
        if agentid:
            wechat_address_number = ''  # 微信通讯录编号
            for appr in user_list:
                employee = self.env['hr.employee'].sudo().search([('id', '=', appr.id)])
                user = self.env['res.users'].sudo().search([('id', '=', employee.user_id.id)])
                wechat_address_number += user.login + '|'
            self.env['wechat.enterprise.send.message'].send_news_message(wechat_address_number[:-1], agentid.agentid,
                                                                         content, description, url)
            return 1
        else:
            return 0

    def gld_state_sent_service(self, gld, approver):
        """
        提交审批
        :return:
        """
        if gld:
            if len(approver) <= 0:
                raise exceptions.Warning(u"当前工联单没有审批人，不允许提交审批！")
            else:
                state = gld[0].state
                if state != 'draft':
                    raise exceptions.Warning(u"工联单已提交，当前操作不允许！")
                approvals_user_ids = ','
                if approver:
                    gld_opinion = self.env['gld.opinion'].sudo().search(
                        [('gld_id', '=', gld.id)])
                    for o in gld_opinion:
                        o.sudo().unlink()
                    for appr in approver:
                        _logger.info(u'当前要保存的审批人是(%s)' % appr)
                        service_obj = self.env['gld.service'].create_opinion_gld(gld.id, appr)
                        gld.write({'state': 'pending', 'approvals_user_ids': approvals_user_ids})
                        insur_str = self.env['ir.config_parameter'].get_param('web.base.url')
                        url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                            gld.name, '2', appr.user_id.id)  # 跳转地址，需要和微信保持一致
                        description = u"%s提交了一张标题为“%s”的工联单，需要您进行审批，请点击查看全文，马上处理！" % (
                            self.env['gld.common'].get_login_user()["name"], gld.subject)
                        self.get_gld_agentid(appr, u'单号：' + gld.name, description, url)
                    gld.message_post(gld.sponsor.name + u' 提交工联单')
                    return service_obj

    @api.model
    def add_approver_service(self, gld_data, approver, shuzi):
        """
        保存单证，添加新的审批人
        :return:
        """
        if gld_data:
            employee_obj = self.env['hr.employee']  # 获取员工业务对象
            wizard = approver
            apprs = []
            appr_names = ''
            # 判断添加的审批人是否已经在工联单中存在，存在则提示错误
            approver_id = ''  # 审批人id
            for appr in wizard:
                if appr.work_email == False:
                    if shuzi == 1:
                        raise exceptions.Warning(u'您选择的【 ' + appr.name + u' 】没有关联用户。！')
                    else:
                        return "3"
                approver_id += str(appr.id) + ','
                appr_names += appr.name_related + ","
                exis_approver = False
                for gld_approver in gld_data.approver:
                    in_sz = []
                    in_sz.append(gld_approver.id)
                    if appr.id in in_sz:
                        exis_approver = True
                if exis_approver:
                    if shuzi == 1:
                        raise exceptions.Warning(u'您选择的【 ' + appr.name + u' 】已经为审批人，不能重复添加。！')
                    else:
                        return "2"
                else:
                    icp = self.env['ir.config_parameter']
                    insur_str = icp.get_param('web.base.url')
                    url_ = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                        gld_data.name, '2', appr.user_id.id)
                    title = u'单号：' + gld_data.name
                    description = u'%s添加了您为“%s”工联单的审批人，请点击查看全文，马上处理！' % (
                        self.env['gld.common'].get_login_user()["name"], gld_data.subject)
                    self.env['gld'].get_gld_agentid(appr, title, description, url_)
                    apprs.append((4, appr.id))
                    employee = employee_obj.sudo().search([('id', '=', appr.id)])
                    # 把审批人 写到审批意见表里面去
                    vals = {}
                    vals['approver'] = appr.id
                    vals['approver_dept'] = employee['department_id'].name
                    vals['gld_id'] = gld_data.id
                    vals['company_id'] = appr.company_id.name

            gld_data.send_mess_gld(
                self.env['gld.common'].get_login_user()["name"] + u"添加新的审批人:" + appr_names[:-1])
            gld_vals = {}
            gld_vals['approver'] = apprs
            gld_vals['gld_id'] = gld_data.id
            gld_data.write(gld_vals)

    @api.model
    def transfer(self, surrender_employee_id, accept_employee_id):
        """
        :param surrender_employee_id: 交出员工
        :param accept_employee_id: 接受员工
        :return:
        """
        super(WechatGld).transfer(surrender_employee_id, accept_employee_id)
        agentid = self.env['wechat.enterprise.app'].sudo().search([('name', '=', u'工联单')])
        if agentid:
            wechat_address_number = ''  # 微信通讯录编号
            accept_employee_obj = self.env['hr.employee'].sudo().search([('id', '=', int(accept_employee_id))])
            surrender_employee_obj = self.env['hr.employee'].sudo().search([('id', '=', int(surrender_employee_id))])
            user = self.env['res.users'].sudo().search([('id', '=', accept_employee_obj.user_id.id)])
            wechat_address_number += user.login + '|'
            surrender_name = ''
            if surrender_employee_obj:
                surrender_name = surrender_employee_obj.name
            self.env['wechat.enterprise.send.message'].send_news_message(wechat_address_number[:-1],
                                                                         agentid.agentid,
                                                                         u'您已经接收到 ' + surrender_name + u' 的所有工联单，请及时查看! ',
                                                                         '', '')

