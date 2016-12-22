# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import fields, models, api

_logger = logging.getLogger(__name__)


class ToproerpBrands(models.Model):
    _name = 'toproerp.brands'
    _description = u'品牌'

    brand_logo = fields.Binary(string=u"品牌logo")
    brands_no = fields.Char(string=u'品牌编码', required=True, size=20)
    name = fields.Char(string=u'品牌名称', required=True, size=20)
    active = fields.Boolean(string=u'是否有效', default=True)

    _sql_constraints = [
        ('toproerp_brands_no_uniq', 'unique (brands_no)', u'品牌编码不能重复!'), ]
