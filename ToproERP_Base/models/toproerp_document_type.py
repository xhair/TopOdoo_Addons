# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)..

import logging

from openerp import fields, models

_logger = logging.getLogger(__name__)


class ToproerpDocumentType(models.Model):
    _name = 'toproerp.document.type'
    _description = u'文档类型'

    document_type_no = fields.Char(string=u'类型编码', required=True, size=20)
    name = fields.Char(string=u'文档名称', required=True, size=20)
    note = fields.Text(string=u'备注')
    active = fields.Boolean(string=u'是否有效', default=True)

    #数据库唯一约束
    _sql_constraints = [
        ('toproerp_document_type_no_uniq', 'unique (document_type_no)', u'类型编码不能重复!'),]