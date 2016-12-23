# -*- coding: utf-8 -*-
# © <2016> <gld liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, exceptions
import time


class SytOaGldOpinion(models.Model):
    _name = "gld.opinion"
    _description = u'审批意见'

    gld_id = fields.Many2one('gld', string=u"工联单", index=True)
    appov_date = fields.Datetime(string=u"审批时间", default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    approver = fields.Many2one('hr.employee', string=u"审批人",
                               default=lambda self: self.env['gld.common'].get_login_user()["id"], index=True)
    mobile_phone = fields.Char(related='approver.mobile_phone', string=u"联系手机", readonly=True, store=True)
    approver_dept = fields.Char(string=u"审批部门",
                                default=lambda self: self.env['gld.common'].get_login_user()["department_id"][
                                    "name"])
    opinion = fields.Text(string=u"审批意见")
    company_id = fields.Char(string=u"公司")

    @api.multi
    def save_opinion(self):
        """
        保存审批意见：同意
        :return:
        """
        # 修改工联单的状态为“审批中”
        gld_bean = self.env['gld'].sudo().search([('id', '=', self._context.get('gld_id'))])
        if gld_bean:
            # gid = 0
            if gld_bean['state'] == 'draft':
                raise exceptions.Warning(u"该工联单已经被置为草稿！")
            if gld_bean['state'] in ('n_through', 'through', 'cancel'):
                raise exceptions.Warning(u"该工联单已经被置为完成！")
            else:
                employee = self.env['gld.common'].get_login_user()
                self.save_opinion_service(self._context.get('gld_id'), self.opinion, self._context.get('check_state'),
                                          employee, 1)
                title = u'单号：%s' % gld_bean.name
                if self.opinion == False:
                    self.opinion = u'无'
                # description = u"%s审核了单号为%s的工联单，审批意见为：%s。请点击查看全文！" % (self.approver.name, gld_bean.name, self.opinion)
                # 调用 微信版发送消息

    def save_opinion_service_wechat(self, gld_id=None, opinion=None, check_state=None, employee=None, shuzi=None):
        """
        保存审批意见：同意
        :return:
        """
        # 修改工联单的状态为“审批中”
        # gld_bean = self.env['gld'].sudo().search([('id', '=', self._context.get('gld_id'))])
        gld_bean = self.env['gld'].sudo().search([('id', '=', gld_id)])
        if gld_bean:
            # gid = 0
            if gld_bean['state'] == 'draft':
                return "2"
            if gld_bean['state'] in ('n_through', 'through', 'cancel'):
                return "3"
            else:
                self.sudo().save_opinion_service(gld_id, opinion, check_state,
                                                 employee, shuzi)
        return "1"

    def save_opinion_service(self, gld_id, opinion, check_state, employee, shuzi):
        """
        保存审批意见：同意
        :return:
        """
        # 修改工联单的状态为“审批中”
        gld_bean = self.env['gld'].sudo().search([('id', '=', gld_id)])
        if gld_bean:
            opinion_list = self.sudo().search([('gld_id', '=', gld_bean.id), ('approver', '=', employee.id)])
            if opinion_list:
                if opinion == False:
                    opinion = check_state
                opinion_list.write(
                    {'appov_date': time.strftime('%Y-%m-%d %H:%M:%S'), 'opinion': check_state + ':' + opinion})
                apprs = []
                apprs.append((4, employee.id))
            else:
                val = {}
                if shuzi == 1:
                    company_name = self.env['gld.common'].sudo().get_login_user()["company_id"]['name']
                    val['approver'] = self.env['gld.common'].sudo().get_login_user()["id"]
                else:
                    company_name = employee.name
                    val['approver'] = employee.id
                val['gld_id'] = gld_id
                val['opinion'] = opinion
                val['company_id'] = company_name
                val['appov_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
                self.create(val)
            if opinion == False or opinion == u'不同意' or opinion == u'不允许' or opinion == u'不接受' or opinion == u'不通过':
                opinion = check_state
            # 处理判断此工联单是否已经审批完成
            self.env['gld.service'].find_is_appo_finish(gld_id, gld_bean, check_state + ':' + opinion, shuzi,
                                                               employee)
            gld_bean.write(
                {'yi_approver_user_ids': apprs, 'approver': [(3, employee.id)]})  # 回写  已审批人id（新增） 审批人id（删除）

    def add_opinion(self, vals):
        """
        保存审批意见：工联单保存时
        :return:
        """
        gld_bean = self.env['gld'].sudo().search([('id', '=', int(vals['gld_id']))])
        opinion_bean = self.env['gld.opinion'].sudo().search(
            [('gld_id', '=', int(vals['gld_id'])), ('approver', '=', int(vals['approver']))])
        opinion_id = 0
        if gld_bean:
            if gld_bean['state'] in ('n_through', 'through', 'cancel'):
                raise exceptions.Warning(u"该工联单已经被置为完成！")
            else:
                if not opinion_bean:
                    opinion_id = self.create(vals)
            return opinion_id

