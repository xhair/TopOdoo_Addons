# -*- coding: utf-8 -*-
# © <2016> <gld liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, exceptions


class GldTemplateType(models.Model):
    _name = "gld.template.type"
    _description = u'工联单模板类型'

    name = fields.Char(string=u"模板类型名称", required=True)
    remark = fields.Char(string=u"模板类型备注")

    _sql_constraints = [
        ('syt_oa_gld_template_type_uniq', 'unique (name)', u'模板类型名称不能重复!'), ]

    @api.model
    def create(self, vals):
        obj = self.search([('name', '=', str(vals["name"]).lstrip().rsplit())])
        if len(obj) >= 1:
            raise exceptions.Warning(u'模板类型名称不能重复')
        else:
            vals["name"] = vals["name"]
            vals["remark"] = vals["remark"]
            return super(GldTemplateType, self).create(vals)
