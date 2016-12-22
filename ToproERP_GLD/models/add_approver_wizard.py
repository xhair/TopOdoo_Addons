# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, exceptions


class add_approver_wizard(models.TransientModel):
    _name = "syt.oa.gld.add.approver.wizard"
    _description = u'添加审批人向导'

    def get_context_user(self):
        '''
        获取工联单单号
        :return:
        '''
        if (self._context.has_key('gld_id')):
            return self._context['gld_id']
        return False

    gld_id = fields.Many2one('syt.oa.gld', string=u"工联单", default=get_context_user)
    approvers = fields.Many2many('hr.employee', 'syt_oa_gld_appover_wizard_rel', string=u"审批人")

    # @api.multi
    # def add_approver(self):
    #     '''
    #     保存单证，添加新的审批人
    #     :return:
    #     '''
    #
    #     gld_obj = self.env['syt.oa.gld']  # 获取工联单业务对象
    #     opinion_obj = self.env['syt.oa.gld.opinion']  # 获取审批意见业务对象
    #     employee_obj = self.env['hr.employee']  # 获取员工业务对象
    #     service_obj = self.env['syt.oa.gld.service']  # 获取工联单服务业务对象
    #     wizard = self.approvers
    #     gld_data = gld_obj.search([('id', '=', self._context.get('gld_id'))])
    #     approvals_user_ids = gld_data['approvals_user_ids']
    #     opinionsid = ''
    #     apprs = []
    #     appr_names = ''
    #     # 判断添加的审批人是否已经在工联单中存在，存在则提示错误
    #     if gld_data:
    #         approver_id = ''  # 审批人id
    #         for appr in wizard:
    #             approver_id += str(appr.id) + ','
    #             appr_names += appr.name_related + ","
    #             exis_approver = False
    #             for gld_approver in gld_data.approver:
    #                 in_sz = []
    #                 in_sz.append(gld_approver.id)
    #                 if appr.id in in_sz:
    #                     exis_approver = True
    #             if exis_approver:
    #                 raise exceptions.Warning(u'您选择的【 ' + appr.name + u' 】已经为审批人，不能重复添加。！')
    #
    #             apprs.append((4, appr.id))
    #             employee = employee_obj.search([('id', '=', appr.id)])
    #             # 把审批人 写到审批意见表里面去
    #             vals = {}
    #             vals['approver'] = appr.id
    #             vals['approver_dept'] = employee['department_id'].name
    #             vals['gld_id'] = gld_data.id
    #             vals['company_id'] = appr.company_id.name
    #             opinionsid = opinion_obj.add_opinion(vals)
    #             approvals_user_ids = approvals_user_ids + str(
    #                 gld_obj.get_user_by_employee(employee['id'])) + ','
    #         # 日志SNS
    #         self.env['syt.oa.gld'].send_mess_gld(u"添加新的审批人:" + appr_names[:-1])
    #         gld_vals = {}
    #         gld_vals['approvals_user_ids'] = gld_data.approvals_user_ids + approver_id
    #         gld_vals['approver'] = apprs
    #         gld_vals['gld_id'] = gld_data.id
    #         gld_data.write(gld_vals)

    @api.multi
    def add_approver(self):
        '''
        保存单证，添加新的审批人
        :return:
        '''
        gld_data = self.env['syt.oa.gld'].search([('id', '=', self._context.get('gld_id'))])
        if gld_data:
            obj = self.add_approver_service(gld_data, self.approvers, 1)

    def add_approver_service(self, gld_data, approver, shuzi):
        '''
        保存单证，添加新的审批人
        :return:
        '''
        if gld_data:
            gld_obj = self.env['syt.oa.gld']  # 获取工联单业务对象
            opinion_obj = self.env['syt.oa.gld.opinion']  # 获取审批意见业务对象
            employee_obj = self.env['hr.employee']  # 获取员工业务对象
            service_obj = self.env['syt.oa.gld.service']  # 获取工联单服务业务对象
            wizard = approver
            approvals_user_ids = gld_data['approvals_user_ids']
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
                    self.env['toproerp.common'].get_login_user()["name"], gld_data.subject)
                    self.env['syt.oa.gld'].get_gld_agentid(appr, title, description, url_)
                    apprs.append((4, appr.id))
                    employee = employee_obj.sudo().search([('id', '=', appr.id)])
                    # 把审批人 写到审批意见表里面去
                    vals = {}
                    vals['approver'] = appr.id
                    vals['approver_dept'] = employee['department_id'].name
                    vals['gld_id'] = gld_data.id
                    vals['company_id'] = appr.company_id.name
                    opinionsid = opinion_obj.add_opinion(vals)
                    # approvals_user_ids = approvals_user_ids + str(gld_obj.get_user_by_employee(employee['id'])) + ','
            # if shuzi == 1:
            #     gld_data.send_mess_gld(
            #         self.env['toproerp.common'].get_login_user()["name"] + u"添加新的审批人:" + appr_names[:-1])

            gld_data.send_mess_gld(
                self.env['toproerp.common'].get_login_user()["name"] + u"添加新的审批人:" + appr_names[:-1])
            gld_vals = {}
            # gld_vals['approvals_user_ids'] = gld_data.approvals_user_ids + approver_id
            gld_vals['approver'] = apprs
            gld_vals['gld_id'] = gld_data.id
            gld_data.write(gld_vals)
