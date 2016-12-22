# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class Confirm(models.TransientModel):
    _name = 'confirm'
    _description = u'确认放款'

    def _get_confirm_id(self):
        return self.env['expense.account'].browse(self._context.get('active_id', []))

    @api.onchange('confirm_id')
    def _get_should_pay(self):
        if self.confirm_id:
            self.should_pay = self.confirm_id.expenses_sum or 0.0
            self.actual_pay = self.confirm_id.expenses_sum or 0.0

    confirm_id = fields.Many2one('expense.account', string=u'确认放款', default=_get_confirm_id,
                                 readonly=True)
    advance_way = fields.Selection([('cash', u'现金'), ('transfer', u'转账')], string=u'放款方式', default='cash',
                                   required=True)  # 放款方式
    should_pay = fields.Float(string=u'应放款金额', readonly=True)
    actual_pay = fields.Float(string=u'实放款金额', required=True)

    def confirm(self):
        self.confirm_id.state = 'advanced'
        self.confirm_id.advance_way = self.advance_way
