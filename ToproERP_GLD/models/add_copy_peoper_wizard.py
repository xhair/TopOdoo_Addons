# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, exceptions


class add_copy_peoper_wizard(models.TransientModel):
    _name = 'syt.oa.gld.add.peoper.wizard'  # 对象名称
    _description = u'添加工联单抄送人向导'  # 对象描述  中文加 U

    def get_context_copy_suggest(self):
        '''
        获取建议添加的抄送人
        :return:
        '''
        if (self._context.has_key('gld_id')):
            gld_obj = self.env['syt.oa.gld']
            gld = gld_obj.search([('id', '=', self._context.get('gld_id'))])
            return gld.copy_suggest
        return False

    gld_id = fields.Many2one('syt.oa.gld', string=u"工联单")
    copy_users = fields.Many2many('hr.employee', 'syt_oa_gld_copyuser_wizard_rel', string=u"抄送人", required=True)
    copy_declare = fields.Text(string=u"抄送说明")
    copy_suggest = fields.Char(string=u"建议添加的抄送人", default=get_context_copy_suggest)

    # @api.multi
    # def add_copy_peoper(self):
    #     '''
    #     添加抄送人
    #     :return:
    #     '''
    #
    #     wizard = self.copy_users
    #     gld_obj = self.env['syt.oa.gld']
    #     employee_obj = self.env['hr.employee']  # 获取员工业务对象
    #     gld_data = gld_obj.search([('id', '=', self._context.get('gld_id'))])
    #     apprs = []
    #     appr_names = ''
    #     # 判断添加的抄送人是否已经在工联单中存在，存在则提示错误
    #     msg_u_ids = []
    #     message_follower_ids = []
    #     if gld_data:
    #         copy_users_id = ''  # 抄送人id
    #         for appr in wizard:
    #             # copy_users中是员工ID，这里需要转换成用户ID
    #             # copy_uid = self.get_user_by_employee(appr.id)
    #             employee = employee_obj.search([('id', '=', appr.id)])
    #             copy_uid = employee.user_id.id
    #
    #             copy_users_id += str(appr.id) + ','
    #             exis_copy_users = False
    #             for gld_copy_users in gld_data.copy_users:
    #                 in_sz = []
    #                 in_sz.append(gld_copy_users.id)
    #                 if appr.id in in_sz:
    #                     exis_copy_users = True
    #             if exis_copy_users:
    #                 raise exceptions.Warning(u'您选择的【 ' + appr.name + u' 】已经为抄送人，不能重复添加。！')
    #             if copy_uid == False:
    #                 raise exceptions.Warning(u"您选择" + appr.name + u"没有所属用户！")
    #
    #             appr_names += appr.name + ","
    #             apprs.append((4, appr.id))
    #
    #         gld_vals = {}
    #         gld_vals['copy_users'] = apprs
    #         if self.copy_declare:
    #             if gld_data.copy_declare == False:
    #                 gld_vals['copy_declare'] = self.copy_declare + ';'
    #             else:
    #                 gld_vals['copy_declare'] = gld_data.copy_declare + self.copy_declare + ';'
    #         gld_data.write(gld_vals)
    #         # 修改工联单 的抄送人 待阅已阅字段
    #         write_copy_peoper_uids = self.write_copy_peoper_uids(gld_data.id)
    #         gld_data.write({'copy_users_dy_ids': write_copy_peoper_uids})
    #
    #         gld_obj.send_mess_gld(u"添加新的抄送人:" + appr_names[:-1])

    @api.multi
    def add_copy_peoper(self):
        '''
        添加抄送人
        :return:
        '''
        gld_obj = self.env['syt.oa.gld']
        gld_data = gld_obj.search([('id', '=', self._context.get('gld_id'))])
        if gld_data:
            self.add_copy_peoper_service(gld_data, self.copy_users, self.copy_declare, 1)
            # 修改工联单 的抄送人 待阅已阅字段
            write_copy_peoper_uids = self.write_copy_peoper_uids(gld_data.id)
            gld_data.write({'copy_users_dy_ids': write_copy_peoper_uids})

    def add_copy_peoper_service(self, gld, copy_users, copy_declare, shuzi):
        '''
        添加抄送人
        :return:
        '''
        wizard = copy_users
        if gld:
            if gld.state == u"through":
                for people in copy_users:
                    icp = self.env['ir.config_parameter']
                    insur_str = icp.get_param('web.base.url')
                    url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                        gld.name, '2', people.user_id.id)  # 跳转地址，需要和微信保持一致

                    description = u"%s抄送了一张标题为“%s”的工联单给您，请点击查看全文，马上处理！" % (self.env['toproerp.common'].get_login_user()["name"], gld.subject)
                    self.env['syt.oa.gld'].get_gld_agentid(people, u'单号：' + gld.name, description, url)
            employee_obj = self.env['hr.employee']  # 获取员工业务对象
            apprs = []
            appr_names = ''
            # 判断添加的抄送人是否已经在工联单中存在，存在则提示错误
            copy_users_id = ''  # 抄送人id
            for appr in wizard:
                if appr.work_email == False:
                    if shuzi == 1:
                        raise exceptions.Warning(u'您选择的【 ' + appr.name + u' 】没有关联用户。！')
                    else:
                        return "3"
                # copy_users中是员工ID，这里需要转换成用户ID
                employee = employee_obj.sudo().search([('id', '=', appr.id)])
                copy_uid = employee.user_id.id
                copy_users_id += str(appr.id) + ','
                exis_copy_users = False
                for gld_copy_users in gld.copy_users:
                    in_sz = []
                    in_sz.append(gld_copy_users.id)
                    if appr.id in in_sz:
                        exis_copy_users = True
                if shuzi == 1:
                    if exis_copy_users:
                        raise exceptions.Warning(u'您选择的【 ' + appr.name + u' 】已经为抄送人，不能重复添加。！')
                    if copy_uid == False:
                        raise exceptions.Warning(u"您选择" + appr.name + u"没有所属用户！")
                else:
                    if exis_copy_users:
                        return "2"
                    if copy_uid == False:
                        return "3"
                appr_names += appr.name + ","
                apprs.append((4, int(appr.id)))
            gld_vals = {}
            gld_vals['copy_users'] = apprs
            if copy_declare:
                if gld.copy_declare == False:
                    gld_vals['copy_declare'] = copy_declare + ';'
                else:
                    gld_vals['copy_declare'] = gld.copy_declare + copy_declare + ';'

            gld_vals['copy_users_dy_ids'] = apprs
            gld.write(gld_vals)
            # if shuzi == 1:
            #     gld.send_mess_gld(self.env['toproerp.common'].get_login_user()["name"] + u"添加新的抄送人:" + appr_names[:-1])
            gld.send_mess_gld(self.env['toproerp.common'].get_login_user()["name"] + u"添加新的抄送人:" + appr_names[:-1])

    def write_copy_peoper_uids(self, gld_id):
        '''
        抄送人权限字段组装，防止出现抄送人列表里面的抄送人不能看见工联单
        :param gld_id: 工联单id
        :return:
        '''
        gld_obj = self.env["syt.oa.gld"]
        copy_user_wizrd = self.copy_users
        gld_bean = gld_obj.search([('id', '=', gld_id)])
        # 默认应该是工联单的待阅ID
        # copy_users_dy_ids = gld_bean.copy_users_dy_ids
        copy_users_dy_ids = []

        for copyer in copy_user_wizrd:  # 向导里应该是新增加的待阅人员，但是发起这个向导的人应该从待阅的名单中去除
            copy_users_dy_ids.append((4, int(copyer.id)))
        return copy_users_dy_ids
