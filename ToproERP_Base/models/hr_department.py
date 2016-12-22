# -*- coding: utf-8 -*-
__author__ = 'suntao'

from openerp import api, models, exceptions,fields, _
import json
from json import *
import logging
from openerp.http import request

_logger = logging.getLogger(__name__)

from openerp import fields, models

class HrDepartment(models.Model):
    _inherit = "hr.department"
    _description = u'部门'


    #
    # @api.onchange('company_id')
    # def check_company(self):
    #     self.company_id = self.env.user.company_id.id

    company_id = fields.Many2one('res.company',string=u"公司",required=True, index=True)



