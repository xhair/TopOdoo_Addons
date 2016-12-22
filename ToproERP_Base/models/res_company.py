# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ToproerpCompany(models.Model):
    _inherit = "res.company"
    _description = u'公司'

    brands_ids = fields.Many2many('toproerp.brands', string=u'经营的品牌')

