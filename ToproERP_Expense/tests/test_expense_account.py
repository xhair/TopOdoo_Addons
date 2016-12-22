# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestExpenseAccount(TransactionCase):
    """This class extends the base TransactionCase, test ToproERP_Expense
    """

    post_install = True
    at_install = False

    def setUp(self):
        super(TestExpenseAccount, self).setUp()
        self.set_expense_account = self.env['set.expense.account'].create({  # 报销类型
            'name': u'食宿'
        })
        self.relevance_account = self.env['relevance.account'].create({  # 银行账户
            'name': 'testAccount',
            'relevance_account': 'testBank'
        })
        expense_account_details = [(0, 0, {  # 费用明细
            'details_name': 'things1',
            'details_expenses': 199.00,
            'details_remark': 'remark1',
        }), (0, 0, {
            'details_name': 'thing2',
            'details_expenses': 200.00,
            'details_remark': 'remark2',
        })]
        self.expense_account = self.env['expense.account'].create({  # 主单据
            'type_ids': self.set_expense_account.id,
            'relevance_account_ids': self.relevance_account.id,
            'details_ids': expense_account_details,
            'state': 'draft'
        })
        self.confirm = self.env['confirm'].create({
            'actual_pay': 200.00,
            'should_pay': 200.00,
        })

    def test_expenses(self):
        self.assertEquals(self.expense_account.expenses_sum, 399.00)  # 测试总金额

        self.assertEquals(self.expense_account.type_ids.name, u'食宿')  # 测试报销类型

        self.assertEquals(self.expense_account.relevance_account_ids.name, 'testAccount')  # 测试银行账户

    def test_submit(self):  # 测试submit方法
        if self.expense_account.state == 'draft':
            self.expense_account.button_submit()
            submit_value = self.env['syt.oa.gld'].search(
                [('relevant_documents', '=', self.expense_account.name)]  # 测试报销单是否在工联单创建
            )
            if submit_value:
                self.assertEquals(submit_value.state, 'pending')
                self.assertEquals(self.expense_account.state, 'pending_approval')  # 测试报销单状态是否为待审批
            else:
                raise exceptions.ValidationError(u"submit_value不能为null!")
        else:
            raise exceptions.ValidationError(u"当前状态不为draft!")

    def test_recall(self):  # 测试追回方法
        self.expense_account.button_submit()
        recall_value = self.env['syt.oa.gld'].search(
            [('relevant_documents', '=', self.expense_account.name)])
        if recall_value:
            if self.expense_account.state == 'pending_approval':
                self.expense_account.button_recall()
                self.assertEquals(recall_value.state, 'cancel')
                self.assertEquals(self.expense_account.state, 'draft')  # 测试报销单状态是否为草稿
            else:
                raise exceptions.ValidationError(u"当前状态不为pending_approval!")
        else:
            raise exceptions.ValidationError(u"recall_value不能为null!")

    def test_confirm(self):  # 测试确认付款
        self.expense_account.button_submit()
        confirm_value = self.env['syt.oa.gld'].search(
            [('relevant_documents', '=', self.expense_account.name)])
        agree = self.env['syt.oa.gld.opinion'].with_context(gld_id=confirm_value.id, check_state=u'通过').create({
            # 'opinion': u'通过'
        })
        agree.save_opinion()
        if confirm_value:
            if self.expense_account.state == 'approval_pass':
                confirm = self.env['confirm'].create({
                    'actual_pay': 200.00,
                    'confirm_id': self.expense_account.id
                })
                confirm.confirm()
                self.assertEquals(self.expense_account.state, 'advanced')
            else:
                raise exceptions.ValidationError(u"当前状态不为approval_pass!")
        else:
            raise exceptions.ValidationError(u"confirm_value不能为null!")

    def test_approval_reject(self):  # 测试审批驳回
        self.expense_account.button_submit()
        return_value = self.env['syt.oa.gld'].search([(
            'relevant_documents', '=', self.expense_account.name
        )])
        if return_value:
            return_value.gld_state_cancel()
            self.assertEquals(self.expense_account.state, 'approval_reject')
        else:
            raise exceptions.ValidationError(U"return_value不能为null!")

