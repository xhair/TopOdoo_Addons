# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import models, api, fields, exceptions
import time

_logger = logging.getLogger(__name__)


class syt_oa_gld(models.Model):
    _name = "syt.oa.gld"
    _description = u'工联单主页面'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    # _order = 'name desc,started desc,expiration desc'
    _order = 'name desc'

    def get_gld_agentid(self, user_list, content, description, url):
        '''
        根据工联单名字获取授权方应用ID  并发送信息给微信中
        :param user_list:发送给谁，员工id
        :param content: 发送内容
        :return:
        '''
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

    def get_login_user(self):
        return self.env['toproerp.common'].sudo().get_login_user()

    def _get_isApproval_value(self):
        '''
        默认方法 用来判断：工联单审批人里面是否有当前登录人、当前登录用户是否为编制人、当前登录用户是否可审批、当前登录用户是否为抄送人、当前登录用户是否已阅、当前工联单是否全部同意
        :return:
        '''
        gld = ''
        for item in self:
            gld = self.search([('id', '=', item.id)])
        ret = {}
        strs = u'不同意'
        if gld:
            employee_id = self.env['toproerp.common'].get_login_user()["user_id"]["id"]  # 获取员工的 id
            # 当前登录人是否为编制人
            if (self.env["toproerp.common"].get_login_user()["id"] == gld.sponsor.id):
                self.curr_approver_is_luser = True
            for opina in gld.approver_opinions:
                # 审批人是否为当前登录人
                if (self.env['hr.employee'].search([('id', '=', opina.approver.id)])["user_id"]["id"] == self.env.uid):
                    self.is_approval = True
                    # 没有审批意见
                    if (opina.opinion == False):
                        self.uid_is_approval = True
                # 判断工联单是全部同意
                if opina.opinion:
                    if str(opina.opinion.encode('utf-8')).find(strs.encode('utf-8')) > -1:
                        self.curr_gld_through = False
            for copy in gld.copy_users:
                if (copy and (self.env['hr.employee'].search([('id', '=', copy.id)])["user_id"]["id"] == self.env.uid)):
                    self.uid_is_copy = True
            for copy in gld.copy_users_yy_ids:
                if int(self.env['hr.employee'].search([('id', '=', copy.id)])["id"]) == copy.id:
                    # if ',' + str(self.env.uid) + ',' in gld.copy_users_yy_ids:
                    self.uid_is_read_gld = True

    @api.multi
    def gld_state_finish(self):
        gld = self.sudo().search([('name', '=', self.name)])
        if gld:
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
            gld.sudo().write({"state": state})
            if state == 'through':
                gld.message_post(u"该工联单审批人已全部审批，置为已完成")

    # 抄送人阅读工联单后，将用户ID存入“copy_users_yy_ids”
    # 如果当前用户在抄送人列表中，则在“copy_users_dy_ids”中删除用户ID，在“copy_users_yy_ids”中添加用户ID
    @api.multi
    def read_gld(self):
        for gld in self:
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                self.read_gld_service(gld_bean, 1)

    def read_gld_service(self, gld, shuzi=None, employee=None):
        '''
        已阅
        :return:
        '''
        if (gld['state'] == 'through' and gld['copy_users_dy_ids']):
            if_cs = False
            for dy in gld['copy_users_dy_ids']:
                if int(self.env["toproerp.common"].get_login_user()["id"]) == dy.id:
                    if_cs = True
                    break
            if if_cs:
                # gld.send_mess_gld(self.env['toproerp.common'].get_login_user()["name"] + u"已阅工联单")
                employee_id = self.env["toproerp.common"].get_login_user()["id"]
                apprs = []
                apprs.append((4, int(employee_id)))
                gld.write({'copy_users_dy_ids': [(3, employee_id)], 'copy_users_yy_ids': apprs})
                if shuzi == 2:
                    employee_name = employee.name
                    gld.send_mess_gld(employee_name + u'已阅工联单')
                else:
                    employee_name = self.env['toproerp.common'].get_login_user()["name"]
                    # gld.message_post(self.env['toproerp.common'].get_login_user()["name"] + u' 已阅工联单')

    def _auto_read(self):
        '''
        自动已阅
        :return:
        '''
        for gld in self:
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                self.read_gld_service(gld_bean, 1)

    # 计算字段 抄送人名称
    def _get_copy_user_names(self):
        for gld in self:
            glds = self.search([('id', '=', gld.id)])
            retdict = {}
            user_obj = self.env['hr.employee']
            for gld in glds:
                ret = []
                for cuid in gld['copy_users']:
                    ret.append(user_obj.search([('id', '=', cuid)]))
                    # ret.append(user_obj.read(cuid, {'name_related'})['name_related'])
                retdict[gld['id']] = ','.join(ret)
            return retdict

    def _get_report_content(self):
        '''
        如果内容的一行超过了100字符（中文算两个，英文/数字/空格 等算一个）则插入‘\n’ 报表中显示的内容
        :return:
        '''

        glds = self.read({})
        retdict = {}
        for gld in glds:
            ret = []
            content = gld['content']
            retdict[gld['id']] = content
        return retdict

    # 计算字段  是否过了截止时间
    def _get_now_time(self):
        for gld in self:
            glds = self.browse(gld.id)
            ret = {}
            for gld in glds:
                # 当前登录人是否为编制人
                # colors="red:now_time=='1';blue:now_time=='2'"
                ret[gld.id] = {'now_time': ''}
                if ((gld.state not in ['n_through', 'through', 'cancel']) and gld.expiration < time.strftime('%Y-%m-%d',
                                                                                                             time.localtime())):
                    ret[gld.id]['now_time'] = '2'
                elif ((gld.state not in ['n_through', 'through', 'cancel']) and gld.expiration == time.strftime(
                        '%Y-%m-%d',
                        time.localtime())):
                    ret[gld.id]['now_time'] = '1'
                else:
                    ret[gld.id]['now_time'] = '0'
            return ret

    @api.onchange('gld_temp')
    def onchange_gld_temp_share(self):
        '''
        工联单模板选择,当选择模板带出基本信息
        :return:
        '''
        temp_obj = self.env['syt.oa.gld.template'].search([('id', '=', self.gld_temp.id)])
        v = {}
        if (temp_obj):
            self.subject = temp_obj.subject
            self.content = temp_obj.content
            self.emergency = temp_obj.emergency
            self.approval_suggest = temp_obj.approval_suggest
            self.copy_suggest = temp_obj.copy_suggest

    # @api.onchange('approver')
    # def check_approver_work_email(self):
    #     if self.approver:
    #         work_email = False
    #         user = ''
    #         for appr in self.approver:
    #             if not appr.work_email:
    #                 work_email = True
    #                 user = appr
    #         if work_email:
    #             raise exceptions.Warning(u'您选择的【 ' + user + u' 】没有关联用户。！')

    @api.multi
    def gld_state_sent(self):
        '''
        提交审批
        :return:
        '''

        for bill in self:
            self.gld_state_sent_service(bill, self.approver)
            # bill.message_post(self.env['toproerp.common'].get_login_user()["name"] + u' 提交工联单')

    def gld_state_sent_service(self, gld, approver):
        '''
        提交审批
        :return:
        '''
        if gld:
            if len(approver) <= 0:
                raise exceptions.Warning(u"当前工联单没有审批人，不允许提交审批！")
            else:
                state = gld[0].state
                if (state != 'draft'):
                    raise exceptions.Warning(u"工联单已提交，当前操作不允许！")
                approvals_user_ids = ','
                if approver:
                    gld_opinion = self.env['syt.oa.gld.opinion'].sudo().search(
                        [('gld_id', '=', gld.id)])
                    for o in gld_opinion:
                        o.sudo().unlink()
                    for appr in approver:
                        _logger.info(u'当前要保存的审批人是(%s)' % appr)
                        service_obj = self.env['syt.oa.gld.service'].create_opinion_gld(gld.id, appr)
                        # employee = self.env['hr.employee'].sudo().search([('id', '=', appr.id)])
                        # approvals_user_ids += str(employee.id) + ','
                        # company_name = employee.company_id.name
                        # self.env['syt.oa.gld.opinion'].search([('gld_id', '=', gld.id)]).write(
                        #     {'company_id': company_name})
                        gld.write({'state': 'pending', 'approvals_user_ids': approvals_user_ids})
                        icp = self.env['ir.config_parameter']
                        insur_str = icp.get_param('web.base.url')
                        url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                            gld.name, '2', appr.user_id.id)  # 跳转地址，需要和微信保持一致
                        description = u"%s提交了一张标题为“%s”的工联单，需要您进行审批，请点击查看全文，马上处理！" % (
                            self.env['toproerp.common'].get_login_user()["name"], gld.subject)
                        self.get_gld_agentid(appr, u'单号：' + gld.name, description, url)
                    gld.message_post(gld.sponsor.name + u' 提交工联单')
                    return service_obj

    @api.multi
    def gld_state_cancel(self):
        '''
        作废
        :return:
        '''
        for gld in self:
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                self.gld_state_cancel_service(gld_bean)
                if gld.relevant_documents:
                    application = self.env[gld.business_object].sudo()
                    if gld.state == 'through':
                        application.from_gld_message(gld, gld.relevant_documents)
                    elif gld.state == 'n_through':
                        application.from_gld_message(gld, gld.relevant_documents)
                    elif gld.state == 'cancel':
                        application.from_gld_message(gld, gld.relevant_documents)

                        # self.message_post(self.env['toproerp.common'].get_login_user()["name"] + u' 将此工联单作废')

    def gld_state_cancel_service(self, gld):
        '''
        作废
        :return:
        '''
        if gld:
            gld.write({'state': 'cancel', 'approvals_user_ids': False, 'copy_users_dy_ids': False})
            gld.message_post(self.env['toproerp.common'].get_login_user()["name"] + u' 将此工联单作废')

    @api.multi
    def create_gld_from_other(self):
        '''
        提供接口：为所有业务单据提供创建工联单的接口
        :return:
        '''
        self.env['syt.oa.gld.service'].create_gld_from_other()

    @api.multi
    def gld_state_draft(self):
        '''
        置为草稿
        :return:
        '''
        for gld in self:
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                s = gld_bean.approver
                if gld_bean.state != 'pending':
                    raise exceptions.Warning(u"只有待审状态下才能追回！")
                else:
                    self.gld_state_draft_service(gld)

    def gld_state_draft_service(self, gld):
        '''
        置为草稿
        :return:
        '''
        if gld:
            for appr in gld.approver:
                gld.write({'state': 'draft', 'approvals_user_ids': ','})
            # icp = self.env['ir.config_parameter']
            #     insur_str = icp.get_param('web.base.url')
            #     url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (gld.name, '2', appr.user_id.id)
            #     description = u'该工联单状态发生改变,当前状态变为草稿，请点击查看全文！'
            #     title = u'单号：' + gld.name
            #     self.get_gld_agentid(gld.approver, title, description, url)
            gld.message_post(self.env['toproerp.common'].get_login_user()["name"] + u' 将此工联单置为草稿')

    @api.multi
    def waiver(self):
        '''
        不在本人审批范围
        :return:
        '''
        # process_obj = self.pool.get('syt.oa.gld.processe')
        for gld in self:
            # 由于删除了待审中的uid,无权限,所以先查出此工联单的创建人替换uid
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                self.waiver_service(gld_bean)

                # if gld_bean.state != 'through' or gld_bean.state != 'n_through':
                #     if gld_bean.relevant_documents:
                #         if gld_bean.relevant_documents[0:3] == 'QJD':
                #             self.env['toproerp.leave'].draft_leave(gld_bean.relevant_documents)

    def waiver_service(self, gld, open_id=None, employee=None):
        '''
        不在本人审批范围
        :return:
        '''
        if gld:
            # 由于删除了待审中的uid,无权限,所以先查出此工联单的创建人替换uid
            gld_create_uid = gld.create_uid
            class_name = 'syt.oa.gld.service'  # 获得对象类名
            method_name = 'delete_approver_by_uid'  # 获得对象的方法
            objFunc = getattr(self.env[class_name], method_name)
            if open_id:
                objFunc(gld.id, open_id)
            else:
                objFunc(gld.id)
            # gld_bean = self.sudo().search([('id', '=', gld.id)])
            method_name = 'find_is_appo_finish'  # 获得对象的方法
            objFunc = getattr(self.env[class_name], method_name)
            return objFunc(gld.id, gld, '', 2, employee)

    @api.multi
    def unlink(self):
        for gld in self:
            gld_datas = gld.search([('id', '=', gld.id)])
            if gld_datas:
                unlink_ids = []
                sponsor_uid = str(self.env["toproerp.common"].get_user_by_employee(gld_datas['sponsor'][0].id))
                user_id = self.env["toproerp.common"].get_login_user()["id"]
                if (gld_datas['state'] == 'draft' and gld_datas['sponsor'][0].id == user_id):
                    unlink_ids.append(gld_datas['id'])
                else:
                    raise exceptions.Warning(u'只能删除自己发起的且状态为【草稿】的工联单。')
                return super(syt_oa_gld, self).unlink()

    @api.model
    def create(self, vals, pc_wechat=None):
        '''
        重写创建方法 把创建的审批人列表写到 意见表去中
        :return:
        '''
        # 验证数据
        class_name = 'syt.oa.gld.service'  # 获得对象类名
        method_name = 'employee_vali'  # 获得对象的方法  检查约束
        objFunc = getattr(self.env[class_name], method_name)
        objFunc(vals)
        # 保存数据
        gld_id = super(syt_oa_gld, self).create(vals)
        self.message_post(self.env['toproerp.common'].get_login_user()["name"] + u' 创建工联单')
        if gld_id:
            # 创建业务单据
            class_name = 'syt.oa.gld.service'  # 获得对象类名
            method_name = 'create_service'  # 获得对象的方法  创建的业务单据返回单号
            objFunc = getattr(self.env[class_name], method_name)
            write_val = objFunc(gld_id, pc_wechat)
        # 更新业务
        gld_id.write({'name': write_val['name']})
        return gld_id

    # @api.multi
    # def write(self, vals):
    #     gld_id = super(syt_oa_gld, self).write(vals)
    #     return gld_id

    # @api.multi
    # 增加工联单消息
    def send_mess_gld(self, body):
        # self.message_post(ids, body=_(body))
        self.message_post(body)

    @api.multi
    def gld_finish_to_pass(self):
        '''
        继续审批
        :return:
        '''
        for gld in self:
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                self.gld_finish_to_pass_service(gld_bean)

    def gld_finish_to_pass_service(self, gld):
        '''
        继续审批
        :return:
        '''
        if gld:
            vals = {}
            # vals['copy_users_dy_ids'] = ','
            # vals['copy_users_yy_ids'] = ','
            vals['state'] = 'pass'
            gld.write(vals)
            gld.message_post(self.env['toproerp.common'].get_login_user()["name"] + u' 将此工联单置为继续审批')
            return {}

    # 菜单数字显示
    @api.model
    def _needaction_domain_get(self):
        # employee_id = self.env['toproerp.common'].get_login_user()["id"]
        dom1 = [
            '|',
            '&', ('copy_users_dy_ids.user_id', '=', self.env.uid), ('state', '=', 'through'),
            '&', ('approver.user_id', '=', self.env.uid), ('state', 'in', ('pending', 'pass'))
        ]
        if self._needaction:
            dom = [
                '|', ('state', 'not in', ['n_through', 'through', 'cancel']),
                '&', ('copy_users_dy_ids.user_id', '=', self.env.uid), ('state', '=', 'through')
            ]
            return dom
        return []

    @api.multi
    def get_approver(self):
        '''
        默认加载审批人
        :return:
        '''
        approver = self.env['syt.oa.gld.service'].get_approver(self.env.uid)
        employee_list = []
        for appr in approver:
            employee = self.env['hr.employee'].sudo().search([('id', '=', int(appr))], limit=5)
            employee_list.append((4, int(employee.id)))
        return employee_list

    temp_type = fields.Many2one('syt.oa.gld.template.type', string=u"模板类型", index=True)
    gld_temp = fields.Many2one('syt.oa.gld.template', string=u"模板", index=True)
    company_id = fields.Many2one('res.company', related='sponsor.company_id', store=True, index=True)
    sponsor = fields.Many2one('hr.employee', string=u"编制人",
                              default=lambda self: self.env['toproerp.common'].get_login_user()["id"], index=True)
    dept = fields.Char(string=u"制发部门", select=True,
                       default=lambda self: self.env['toproerp.common'].get_login_user()["department_id"]["name"])
    started = fields.Datetime(string=u"日期", select=1, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    name = fields.Char(string=u"名称")
    subject = fields.Char(string=u"标题")
    emergency = fields.Selection([('urgent', u'特急'), ('anxious', u'急'), ('general', u'一般')], string=u'紧急程度',
                                 required=True, default='general')
    content = fields.Html(string=u"正文")
    state = fields.Selection(
        [('draft', u'草稿'), ('pending', u'待审'), ('pass', u'审批中'), ('through', u'审核通过'), ('n_through', u'审核不通过'),
         ('cancel', u'作废')], string=u'状态', default='draft')
    # default=get_approver
    approval_suggest = fields.Char(related='gld_temp.approval_suggest', string=u"建议添加的审批人", readonly=True, store=True)
    copy_suggest = fields.Char(related='gld_temp.copy_suggest', string=u"建议添加的抄送人", readonly=True, store=True)
    approver_opinions = fields.One2many('syt.oa.gld.opinion', 'gld_id', string=u"审批意见")
    approver = fields.Many2many('hr.employee', 'syt_oa_gld_appover_rel', 'gld_id', 'employee_id', string=u"未审批的人")
    yi_approver_user_ids = fields.Many2many('hr.employee', 'syt_oa_gld_yishenpi_appover_rel', 'gld_id', 'employee_id',
                                            string=u"已审批人id")
    approvals_user_ids = fields.Char(string=u"审批人id")
    copy_users = fields.Many2many('hr.employee', 'syt_oa_gld_copyuser_rel', string=u"抄送人")
    copy_users_name = fields.Char(string=u"抄送人名称", default=_get_copy_user_names)
    copy_users_yy_ids = fields.Many2many('hr.employee', 'syt_oa_gld_yiyue_rel', 'gld_id', 'employee_id',
                                         string=u"已阅人id")
    copy_users_dy_ids = fields.Many2many('hr.employee', 'syt_oa_gld_daiyue_rel', 'gld_id', 'employee_id',
                                         string=u"待阅人id")  # 抄送人id
    attachment_ids = fields.Many2many('ir.attachment', 'syt_oa_gld_ir_attchment_rel',
                                      string=u"附件")
    att_names = fields.Char(string=u"附件名称")
    is_approval = fields.Boolean(string=u"工联单审批人里面是否有当前登录人", compute='_get_isApproval_value')
    curr_approver_is_luser = fields.Boolean(string=u"当前登录用户是否为编制人", compute='_get_isApproval_value')
    uid_is_approval = fields.Boolean(string=u"当前登录用户是否可审批", compute='_get_isApproval_value')
    uid_is_copy = fields.Boolean(string=u"当前登录用户是否为抄送人", compute='_get_isApproval_value')
    uid_is_read_gld = fields.Boolean(string=u"当前登录用户是否已阅", compute='_get_isApproval_value')
    curr_gld_through = fields.Boolean(string=u"当前工联单是否全部同意", compute='_get_isApproval_value')
    is_init = fields.Boolean(string=u"是否第一次加载", default=True)
    content_report = fields.Char(string=u"报表中显示的内容", default=_get_report_content)
    expiration = fields.Date(string=u"截止时间", default=time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400 * 3)))
    copy_declare = fields.Text(string=u"抄送说明")
    create_uid = fields.Many2one('res.users', 'Owner', index=True)
    now_time = fields.Char(string=u"是否过了截止时间", default=_get_now_time)
    processe_type = fields.Char(string=u"类型")
    processe_class = fields.Char(string=u"类名")
    processe_name = fields.Char(string=u"单据name(唯一标识)")
    relevant_documents = fields.Char(string=u"相关单据")
    business_object = fields.Char(string=u"业务对象")
    auto_read = fields.Boolean(string=u'自动已阅', compute='_auto_read')
    u_id = fields.Integer(default=lambda self: self.env.uid)  # (作废)
    will_copy_users = fields.Many2many('hr.employee', 'syt_oa_gld_will_copyuser_rel', string=u"预设抄送人")  # (作废)
    user_id_gld = fields.Integer(string=u"用户id")  # (作废)
    approve_type = fields.Char(string=u"approve_type")  # (作废)
    ordey_by = fields.Integer(string=u"ordey_by")  # (作废)
    numebr = fields.Char(string=u"编号")  # (作废)
    # copy_users_dy_ids = fields.Char(string=u"待阅人id", default=',')  (作废)
    # copy_users_yy_ids = fields.Char(string=u"已阅人id", default=',')  (作废)
    # content = fields.Text(string=u"正文") #(作废)
    # approval_suggest = fields.Char(related='gld_temp.name', string=u"建议添加的审批人", readonly=True, store=True)#(作废)
    # copy_suggest = fields.Char(related='gld_temp.name', string=u"建议添加的抄送人", readonly=True, store=True)#(作废)

    @api.multi
    def delete_appover(self):
        '''
        删除历史数据 审批人
        :return:
        '''
        self._cr.execute(
            "select  DISTINCT(a.*)  from syt_oa_gld_appover_rel  a right join syt_oa_gld_opinion b on a.gld_id =b.gld_id where a.gld_id=b.gld_id and  b.opinion is not null  and b.approver=a.employee_id order by gld_id")
        configured_cmp = [r[0] for r in self._cr.fetchall()]
