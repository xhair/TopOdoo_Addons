# -*- coding: utf-8 -*-
from openerp import models, api, fields, exceptions


class SytOaGldTransfer(models.TransientModel):
    _name = 'gld.transfer'
    _description = u'工联单交接'

    surrender_employee_id = fields.Many2one('hr.employee', string=u'交出员工', required=True)
    accept_employee_id = fields.Many2one('hr.employee', string=u'接受员工', required=True)

    @api.multi
    def sure(self):
        if self.surrender_employee_id and self.accept_employee_id:
            if int(self.surrender_employee_id) == int(self.accept_employee_id):
                raise exceptions.Warning(u'请选择不同的员工进行交接！')
            else:
                self.env['gld'].transfer(int(self.surrender_employee_id),int(self.accept_employee_id))
