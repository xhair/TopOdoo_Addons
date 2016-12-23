# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class AddApproverWizard(models.TransientModel):
    _name = "gld.add.approver.wizard"
    _description = u'添加审批人向导'

    def get_context_user(self):
        """
        :return:
        获取工联单单号
        :return:
        """
        if 'gld_id' in self._context:
            return self._context['gld_id']
        return False

    gld_id = fields.Many2one('gld', string=u"工联单", default=get_context_user)
    approvers = fields.Many2many('hr.employee', 'syt_oa_gld_appover_wizard_rel', string=u"审批人")

    @api.multi
    def add_approver(self):
        """
        保存单证，添加新的审批人
        :return:
        """
        gld_data = self.env['gld'].search([('id', '=', self._context.get('gld_id'))])
        if gld_data:
            gld_data.add_approver_service(gld_data, self.approvers, 1)
