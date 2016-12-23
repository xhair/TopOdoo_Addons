# -*- coding: utf-8 -*-
__author__ = 'suntao'

from openerp import api, models, exceptions, fields, _
import json
from json import *
import logging
from openerp.http import request

_logger = logging.getLogger(__name__)

from odoo import fields, models


class HrJob(models.Model):
    _inherit = "hr.job"
    _description = u'职位'

    # @api.onchange('company_id')
    # def check_company(self):
    #     print self.env.user.company_id.name
    #     self.company_id = self.env.user.company_id.id

    company_id = fields.Many2one("res.company", string=u"公司", required=True, index=True)
    department_id = fields.Many2one("hr.department", string=u"部门", required=True, index=True)
