# -*- coding: utf-8 -*-
import logging
from openerp import models, api, fields, exceptions
import time


_logger = logging.getLogger(__name__)


class SytOaGld(models.Model):
    _name = "gld"
    _description = u'工联单主页面'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name desc'

    def get_login_user(self):
        return self.env['gld.common'].sudo().get_login_user()

    def _get_isapproval_value(self):
        """
        默认方法 用来判断：工联单审批人里面是否有当前登录人、当前登录用户是否为编制人、当前登录用户是否可审批、当前登录用户是否为抄送人、当前登录用户是否已阅、当前工联单是否全部同意
        :return:
        """
        gld = ''
        for item in self:
            gld = self.search([('id', '=', item.id)])
        strs = u'不同意'
        if gld:
            # 当前登录人是否为编制人
            if self.env["gld.common"].get_login_user()["id"] == gld.sponsor.id:
                self.curr_approver_is_luser = True
            for opina in gld.approver_opinions:
                # 审批人是否为当前登录人
                if self.env['hr.employee'].search([('id', '=', opina.approver.id)])["user_id"]["id"] == self.env.uid:
                    self.is_approval = True
                    # 没有审批意见
                    if not opina.opinion:
                        self.uid_is_approval = True
                # 判断工联单是全部同意
                if opina.opinion:
                    if str(opina.opinion.encode('utf-8')).find(strs.encode('utf-8')) > -1:
                        self.curr_gld_through = False
            for copy in gld.copy_users:
                if copy and self.env['hr.employee'].search([('id', '=', copy.id)])["user_id"]["id"] == self.env.uid:
                    self.uid_is_copy = True
            for copy in gld.copy_users_yy_ids:
                if int(self.env['hr.employee'].search([('id', '=', copy.id)])["id"]) == copy.id:
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
                if not opin.opinion:
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
        """
        已阅
        :return:
        """
        if gld['state'] == 'through' and gld['copy_users_dy_ids']:
            if_cs = False
            for dy in gld['copy_users_dy_ids']:
                if int(self.env["gld.common"].get_login_user()["id"]) == dy.id:
                    if_cs = True
                    break
            if if_cs:
                employee_id = self.env["gld.common"].get_login_user()["id"]
                apprs = [(4, int(employee_id))]
                gld.write({'copy_users_dy_ids': [(3, employee_id)], 'copy_users_yy_ids': apprs})
                if shuzi == 2:
                    employee_name = employee.name
                    gld.send_mess_gld(employee_name + u'已阅工联单')
                else:
                    pass

    def _auto_read(self):
        """
        自动已阅
        :return:
        """
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
                retdict[gld['id']] = ','.join(ret)
            return retdict

    def _get_report_content(self):
        """
        如果内容的一行超过了100字符（中文算两个，英文/数字/空格 等算一个）则插入‘\n’ 报表中显示的内容
        :return:
        """
        glds = self.read({})
        retdict = {}
        for gld in glds:
            content = gld['content']
            retdict[gld['id']] = content
        return retdict

    # 计算字段  是否过了截止时间
    def _get_now_time(self):
        for gld_obj in self:
            glds = self.browse(gld_obj.id)
            ret = {}
            for gld in glds:
                # 当前登录人是否为编制人
                # colors="red:now_time=='1';blue:now_time=='2'"
                ret[gld.id] = {'now_time': ''}
                if gld.state not in ['n_through', 'through', 'cancel'] and gld.expiration < time.strftime('%Y-%m-%d',time.localtime()):
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
        """
        工联单模板选择,当选择模板带出基本信息
        :return:
        """
        temp_obj = self.env['gld.template'].search([('id', '=', self.gld_temp.id)])
        if temp_obj:
            self.subject = temp_obj.subject
            self.content = temp_obj.content
            self.emergency = temp_obj.emergency
            self.approval_suggest = temp_obj.approval_suggest
            self.copy_suggest = temp_obj.copy_suggest

    @api.multi
    def gld_state_sent(self):
        """
        提交审批
        :return:
        """
        for bill in self:
            self.gld_state_sent_service(bill, bill.approver)

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
                        # 调用微信版补丁发送消息
                        gld.message_post(gld.sponsor.name + u' 提交工联单')
                        return service_obj

    @api.multi
    def gld_state_cancel(self):
        """
        作废
        :return:
        """
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

    def gld_state_cancel_service(self, gld):
        """
        作废
        :return:
        """
        if gld:
            gld.write({'state': 'cancel', 'approvals_user_ids': False, 'copy_users_dy_ids': False})
            gld.message_post(self.env['gld.common'].get_login_user()["name"] + u' 将此工联单作废')

    @api.multi
    def create_gld_from_other(self):
        """
        提供接口：为所有业务单据提供创建工联单的接口
        :return:
        """
        self.env['gld.service'].create_gld_from_other()

    @api.multi
    def gld_state_draft(self):
        """
        置为草稿
        :return:
        """
        for gld in self:
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                # s = gld_bean.approver
                if gld_bean.state != 'pending':
                    raise exceptions.Warning(u"只有待审状态下才能追回！")
                else:
                    self.gld_state_draft_service(gld)

    def gld_state_draft_service(self, gld):
        """
        置为草稿
        :return:
        """
        if gld:
            for appr in gld.approver:
                gld.write({'state': 'draft', 'approvals_user_ids': ','})
            gld.message_post(self.env['gld.common'].get_login_user()["name"] + u' 将此工联单置为草稿')

    @api.multi
    def waiver(self):
        """
        不在本人审批范围
        :return:
        """
        for gld in self:
            # 由于删除了待审中的uid,无权限,所以先查出此工联单的创建人替换uid
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                self.waiver_service(gld_bean)

    def waiver_service(self, gld, open_id=None, employee=None):
        """
        不在本人审批范围
        :return:
        """
        if gld:
            # 由于删除了待审中的uid,无权限,所以先查出此工联单的创建人替换uid
            # gld_create_uid = gld.create_uid
            class_name = 'gld.service'  # 获得对象类名
            method_name = 'delete_approver_by_uid'  # 获得对象的方法
            objfunc = getattr(self.env[class_name], method_name)
            if open_id:
                objfunc(gld.id, open_id)
            else:
                objfunc(gld.id)
            method_name = 'find_is_appo_finish'  # 获得对象的方法
            objfunc = getattr(self.env[class_name], method_name)
            return objfunc(gld.id, gld, '', 2, employee)

    @api.multi
    def unlink(self):
        for gld in self:
            gld_datas = gld.search([('id', '=', gld.id)])
            if gld_datas:
                unlink_ids = []
                user_id = self.env["gld.common"].get_login_user()["id"]
                if gld_datas['state'] == 'draft' and gld_datas['sponsor'][0].id == user_id:
                    unlink_ids.append(gld_datas['id'])
                else:
                    raise exceptions.Warning(u'只能删除自己发起的且状态为【草稿】的工联单。')
                return super(SytOaGld, self).unlink()

    @api.model
    def create(self, vals, pc_wechat=None):
        """
        重写创建方法 把创建的审批人列表写到 意见表去中
        :return:
        """
        # 验证数据
        class_name = 'gld.service'  # 获得对象类名
        method_name = 'employee_vali'  # 获得对象的方法  检查约束
        objfunc = getattr(self.env[class_name], method_name)
        objfunc(vals)
        # 保存数据
        gld_id = super(SytOaGld, self).create(vals)
        self.message_post(self.env['gld.common'].get_login_user()["name"] + u' 创建工联单')
        if gld_id:
            # 创建业务单据
            class_name = 'gld.service'  # 获得对象类名
            method_name = 'create_service'  # 获得对象的方法  创建的业务单据返回单号
            objfunc = getattr(self.env[class_name], method_name)
            write_val = objfunc(gld_id, pc_wechat)
        # 更新业务
            gld_id.write({'name': write_val['name']})
            return gld_id

    # 增加工联单消息
    def send_mess_gld(self, body):
        # self.message_post(ids, body=_(body))
        self.message_post(body)

    @api.multi
    def gld_finish_to_pass(self):
        """
        继续审批
        :return:
        """
        for gld in self:
            gld_bean = self.search([('id', '=', gld.id)])
            if gld_bean:
                self.gld_finish_to_pass_service(gld_bean)

    def gld_finish_to_pass_service(self, gld):
        """
        继续审批
        :return:
        """
        if gld:
            vals = {'state': 'pass'}
            gld.write(vals)
            gld.message_post(self.env['gld.common'].get_login_user()["name"] + u' 将此工联单置为继续审批')
            return {}

    # 菜单数字显示
    @api.model
    def _needaction_domain_get(self):
        if self._needaction:
            dom = [
                '|', ('state', 'not in', ['n_through', 'through', 'cancel']),
                '&', ('copy_users_dy_ids.user_id', '=', self.env.uid), ('state', '=', 'through')
            ]
            return dom
        return []

    @api.multi
    def get_approver(self):
        """
        默认加载审批人
        :return:
        """
        approver = self.env['gld.service'].get_approver(self.env.uid)
        employee_list = []
        for appr in approver:
            employee = self.env['hr.employee'].sudo().search([('id', '=', int(appr))], limit=5)
            employee_list.append((4, int(employee.id)))
        return employee_list

    @api.model
    def add_approver_service(self, gld_data, approver, shuzi):
        """
        保存单证，添加新的审批人
        :return:
        """
        if gld_data:
            opinion_obj = self.env['gld.opinion']  # 获取审批意见业务对象
            employee_obj = self.env['hr.employee']  # 获取员工业务对象
            wizard = approver
            apprs = []
            appr_names = ''
            # 判断添加的审批人是否已经在工联单中存在，存在则提示错误
            approver_id = ''  # 审批人id
            for appr in wizard:
                if not appr.work_email:
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
    def transfer(self,surrender_employee_id , accept_employee_id):
        """
        :param surrender_employee_id: 交出员工
        :param accept_employee_id: 接受员工
        :return:
        """
        self._cr.execute('insert into syt_oa_gld_yiyue_rel select distinct a.id,%s from syt_oa_gld a left join syt_oa_gld_yiyue_rel b on a.id=b.gld_id where a.sponsor = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=a.id and employee_id=%s) ;',
        (accept_employee_id, surrender_employee_id, accept_employee_id))
        # 2：交接：往抄送人表添加数据 （条件：交出员工所已审批的工联单，接受员工）
        self._cr.execute('insert into syt_oa_gld_yiyue_rel select distinct b.id,%s from syt_oa_gld_opinion a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_yiyue_rel c on b.id=c.gld_id where a.approver = %s and b.sponsor != %s and b.state not in(%s,%s)  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
        (accept_employee_id, surrender_employee_id, surrender_employee_id, 'pending', 'pass',accept_employee_id))
        # 3：交接：往待审批的人中间表添加数据 （条件：交出员工所未审批的工联单，接受员工）
        self._cr.execute('insert into syt_oa_gld_appover_rel select distinct b.id,%s from syt_oa_gld_opinion a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_appover_rel c on b.id=c.gld_id where a.approver = %s and b.sponsor != %s and b.state in(%s,%s) and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
        (accept_employee_id, surrender_employee_id, surrender_employee_id, 'pending', 'pass',accept_employee_id))
        # 4：交接：往抄送人表添加数据 （条件：交出员工所被抄送的工联单(待阅)，接受员工）
        self._cr.execute('insert into syt_oa_gld_yiyue_rel select distinct a.gld_id,%s from syt_oa_gld_daiyue_rel a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_yiyue_rel c on b.id=c.gld_id where a.employee_id = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
        (accept_employee_id, surrender_employee_id, accept_employee_id))
        # 5：交接：往抄送人表添加数据 （条件：交出员工所被抄送的工联单(已阅)，接受员工）
        self._cr.execute('insert into syt_oa_gld_yiyue_rel select distinct a.gld_id,%s from syt_oa_gld_yiyue_rel a left join syt_oa_gld b on a.gld_id = b.id where a.employee_id = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
        (accept_employee_id, surrender_employee_id, accept_employee_id))
        # 6：交接完成后，修改（审批意见表）交出员工未审批的所有工联单的现有审批人为接受员工，已审批的不改变
        self._cr.execute('update syt_oa_gld_opinion set approver =%s where approver=%s and opinion is null;',
        (accept_employee_id, surrender_employee_id))
        # 7：交接完成后，修改（未审批人表）交出员工未审批的所有工联单的现有审批人为接受员工，已审批的不改变
        self._cr.execute('delete from syt_oa_gld_appover_rel where employee_id=%s;',(surrender_employee_id,))
        # 获取工联单的微信编号 只发送到工联单模块里面

    temp_type = fields.Many2one('gld.template.type', string=u"模板类型", index=True)
    gld_temp = fields.Many2one('gld.template', string=u"模板", index=True)
    company_id = fields.Many2one('res.company', related='sponsor.company_id', store=True, index=True)
    sponsor = fields.Many2one('hr.employee', string=u"编制人",
                              default=lambda self: self.env['gld.common'].get_login_user()["id"], index=True)
    dept = fields.Char(string=u"制发部门", select=True,
                       default=lambda self: self.env['gld.common'].get_login_user()["department_id"]["name"])
    started = fields.Datetime(string=u"日期", select=1, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    name = fields.Char(string=u"名称")
    subject = fields.Char(string=u"标题")
    emergency = fields.Selection([('urgent', u'特急'), ('anxious', u'急'), ('general', u'一般')], string=u'紧急程度',
                                 required=True, default='general')
    content = fields.Html(string=u"正文")
    state = fields.Selection(
        [('draft', u'草稿'), ('pending', u'待审'), ('pass', u'审批中'), ('through', u'审核通过'), ('n_through', u'审核不通过'),
         ('cancel', u'作废')], string=u'状态', default='draft')

    approval_suggest = fields.Char(related='gld_temp.approval_suggest', string=u"建议添加的审批人", readonly=True, store=True)
    copy_suggest = fields.Char(related='gld_temp.copy_suggest', string=u"建议添加的抄送人", readonly=True, store=True)
    approver_opinions = fields.One2many('gld.opinion', 'gld_id', string=u"审批意见")
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
    is_approval = fields.Boolean(string=u"工联单审批人里面是否有当前登录人", compute='_get_isapproval_value')
    curr_approver_is_luser = fields.Boolean(string=u"当前登录用户是否为编制人", compute='_get_isapproval_value')
    uid_is_approval = fields.Boolean(string=u"当前登录用户是否可审批", compute='_get_isapproval_value')
    uid_is_copy = fields.Boolean(string=u"当前登录用户是否为抄送人", compute='_get_isapproval_value')
    uid_is_read_gld = fields.Boolean(string=u"当前登录用户是否已阅", compute='_get_isapproval_value')
    curr_gld_through = fields.Boolean(string=u"当前工联单是否全部同意", compute='_get_isapproval_value')
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


    @api.multi
    def delete_appover(self):
        """
        删除历史数据 审批人
        :return:
        """
        self._cr.execute(
            "select  DISTINCT(a.*)  from syt_oa_gld_appover_rel  a right join syt_oa_gld_opinion b on a.gld_id =b.gld_id where a.gld_id=b.gld_id and  b.opinion is not null  and b.approver=a.employee_id order by gld_id")
        configured_cmp = [r[0] for r in self._cr.fetchall()]
