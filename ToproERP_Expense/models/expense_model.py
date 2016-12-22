# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, exceptions


# 报销明细
class ExpenseAccountDetails(models.Model):
    _name = 'expense.account.details'
    _description = u'费用明细'

    details_id = fields.Many2one('expense.account', u'费用报销申请单')
    details_name = fields.Char(string=u'事项名', required=True, default=u'please enter your things ')
    details_start = fields.Date(string=u'发生时间', required=True, default=lambda *a: fields.Date.today())
    details_expenses = fields.Float(string=u'费用金额', required=True)
    details_remark = fields.Char(string=u'备注', required=True, default=u'please enter remarks about your things ')

    @api.constrains('expense_account_details_expenses')
    def _check_expenses(self):
        if self.expense_account_details_expenses <= 0:
            raise exceptions.ValidationError(u"费用金额必须大于0!")


# 银行账户
class RelevanceAccount(models.Model):
    _name = 'relevance.account'
    _description = u'相关账户'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)  # 获取默认用户

    name = fields.Char(string=u'银行账号', required=True)
    account_name = fields.Many2one('hr.employee', string=u'用户名', required=True,
                                   default=_default_employee)  # 用户名
    relevance_account = fields.Char(string=u'开户银行', required=True)


# 设置报销类型
class SetExpenseAccount(models.Model):
    _name = 'set.expense.account'
    _description = u'设置报销类型'

    @api.model
    def create(self, vals):
        if vals.get('type_name', '/') == '/':
            vals['type_name'] = self.env['ir.sequence'].next_by_code('set.expense.account') or '/'
        return super(SetExpenseAccount, self).create(vals)

    type_name = fields.Char(string=u'类型编号', default='/', readonly=True)
    name = fields.Char(string=u'类型名称', required=True)


# 费用报销
class ExpenseAccount(models.Model):
    _name = 'expense.account'
    _description = u'费用报销单'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)  # 获取默认用户

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('expense.account') or '/'
        return super(ExpenseAccount, self).create(vals)

    def _get_default_account(self):  # 获取默认账户
        return self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        # return self.env['relevance.account'].search([('', '=', self.applicant_id)], limit=1)

    def _get_default_type(self):
        return self.env['set.expense.account'].search([('type_name', '=', 1)], limit=1)  # 获取默认报销类型

    name = fields.Char(string=u'报销单号', default='/', readonly=True)  # 报销单id
    applicant_id = fields.Many2one('hr.employee', string=u'制单人', required=True,
                                   default=_default_employee, readonly=True)  # 制单人
    date = fields.Date(string=u'制单时间', default=lambda *a: fields.Date.today())  # 制单时间
    details_ids = fields.One2many('expense.account.details', 'details_id',
                                  string=u'费用明细',
                                  ondelete='cascade', required=True)  # 费用明细
    type_ids = fields.Many2one('set.expense.account', string=u'报销类型', required=True, default=_get_default_type)  # 报销类型
    approval_ids = fields.Many2many('hr.employee',
                                    string=u'审批人',
                                    required=True, default=_default_employee)  # 审批人
    advance_way = fields.Selection([('cash', u'现金'), ('transfer', u'转账')], string=u'放款方式', default='cash',
                                   readonly=True)  # 放款方式
    attachment = fields.Many2many('ir.attachment', string=u'附件')  # 附件
    relevance_account_ids = fields.Many2one('relevance.account', string=u'银行账户',
                                            ondelete='cascade', required=True, default=_get_default_account)  # 银行账户
    expenses_sum = fields.Float(compute='_sum_expenses', string=u'总费用', readonly=True)  # 总费用
    create_state = fields.Boolean(string=u'是否为创建状态', default=True)  # 是否为创建状态
    state = fields.Selection([('draft', u'草稿'),
                              ('pending_approval', u'待审批'),
                              ('approval_pass', u'审批通过'), ('approval_reject', u'审批驳回'),
                              ('advanced', u'已完成')], default='draft',
                             string=u"当前状态", readonly=True)
    issue_gld_id = fields.Many2one('syt.oa.gld', string=u'工联单', readonly=True, store=True, index=True)
    boolean_user = fields.Boolean(string=u'判断是否为当前用户', compute='_get_boolean_user')

    @api.depends('details_ids')
    def _sum_expenses(self):
        self.expenses_sum = 0.0
        for line in self.details_ids:
            self.expenses_sum += line.details_expenses or 0.0

    @api.multi
    @api.depends('name')
    def _get_boolean_user(self):
        login_user = self._default_employee()
        applicant_user = self.applicant_id
        if login_user == applicant_user:
            self.boolean_user = True
        else:
            self.boolean_user = False

    @api.constrains('applicant_id')
    def _check_applicant_id(self):
        if len(self.applicant_id) == 0:
            raise exceptions.ValidationError(u"请将信息填写完整")

    def create_gld_message(self):
        """
        调用创建工联单的方法
        :return:
        """
        business_bill_number = self.name
        name = self.name
        title = u"报销单申请"
        applicant_id = self.applicant_id.name
        date = self.date
        things = self.details_ids
        expenses_sum = self.expenses_sum
        times = len(things)
        attachment_ids = self.attachment
        if times == 1:
            things = things.details_name
            price = self.details_ids.details_expenses
            remarks = self.details_ids.details_remark
            body = u"<p>您好:这是一份报销单申请，需要您的审批<br/>%s<br/>申请人: %s &nbsp;&nbsp;申请时间: %s &nbsp;&nbsp; 事项数量: %s <br/>&nbsp;&nbsp;&nbsp;&nbsp;事项名: %s &nbsp;&nbsp;金额: %s &nbsp;&nbsp;备注: %s<br/>总金额: %s <br/>请批准， 谢谢！<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-该工联单来自于报销申请单</p>" % (
                name, applicant_id, date, times, things, price, remarks, expenses_sum
            )
        else:
            value = []
            for item in things:
                things = item.details_name
                price = item.details_expenses
                remarks = item.details_remark
                result = u"<p>&nbsp;&nbsp;&nbsp;&nbsp;事项名: %s &nbsp;&nbsp;金额: %s &nbsp;&nbsp;备注: %s<br/></p>" % (
                    things, price, remarks)
                value.append(result)
            value = ''.join(value)
            body = u"<p>您好:这是一份报销单申请，需要您的审批<br/>%s<br/>申请人: %s &nbsp;&nbsp;申请时间: %s &nbsp;&nbsp; 事项数量: %s <br/>%s<br/>总金额: %s <br/>请批准， 谢谢！<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-该工联单来自于报销申请单</p>" % (
                name, attachment_ids, date, times, value, expenses_sum
            )
        approval = []
        for item in self.approval_ids:
            approval.append(item.id)
        emergency = 'anxious'
        business_class = 'expense.account'  # 自身的业务对象
        gld = self.env['syt.oa.gld.service']
        glds = gld.create_gld_from_other(business_bill_number, title, body, approval, emergency, business_class,
                                         attachment_ids)
        if glds:
            return glds

    def from_gld_message(self, gld, application_no):
        """
        :param gld: 工联单对象
        :param application_no: 发放申请编号
        :return:
        """
        issue_application = self.search([('name', '=', application_no)])
        if issue_application:
            for item in issue_application:
                if gld.state == 'through':
                    item.state = 'approval_pass'
                else:
                    item.state = 'approval_reject'

    @api.multi
    def back_func(self):
        """
        追回，变为草稿
        :return:
        """
        self.state = 'draft'
        if self.issue_gld_id:
            self.issue_gld_id.sudo(self.env.user.id).write({'state': 'cancel'})

    def button_submit(self):
        result = self.boolean_user
        if result:
            self.state = 'pending_approval'
            glds = self.create_gld_message()
            self.write({"issue_gld_id": glds.id})
            self.create_state = False
        else:
            raise exceptions.ValidationError(u"对不起,您只能提交自己的报销单!")

    def button_recall(self):
        result = self.boolean_user
        if result:
            self.back_func()
        else:
            raise exceptions.ValidationError(u"对不起,您只能追回自己的报销单!")

