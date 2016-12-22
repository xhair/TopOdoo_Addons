# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, exceptions


class syt_oa_gld_template(models.Model):
    _name = "syt.oa.gld.template"
    _description = u'工联单模板'

    name = fields.Char(string=u"模板名称", required=True)
    temp_type = fields.Many2one('syt.oa.gld.template.type', string=u"模板分类", required=True, index=True)
    is_valid = fields.Boolean(string=u"是否有效", default=True)
    emergency = fields.Selection([('urgent', u'特急'), ('anxious', u'急'), ('general', u'一般')],
                                 string=u'紧急程度', required=True)
    subject = fields.Char(string=u"标题", required=True)
    content = fields.Html(string=u"正文")
    # content = fields.Text(string=u"正文")
    approval_suggest = fields.Char(string=u"审批建议")
    copy_suggest = fields.Char(string=u"抄送建议")

    # _sql_constraints = [
    #     ('syt_oa_gld_template_uniq', 'unique (name)', u'模板名称不能重复!'), ]

    @api.model
    def create(self, vals):
        obj = self.search([('name', '=', str(vals["name"]).lstrip().rsplit())])
        if len(obj) >= 1:
            raise exceptions.Warning(u'模板名称不能重复')
        else:
            vals["name"] = vals["name"]
            vals["temp_type"] = vals["temp_type"]
            vals["is_valid"] = vals["is_valid"]
            vals["emergency"] = vals["emergency"]
            vals["subject"] = vals["subject"]
            vals["content"] = vals["content"]
            vals["approval_suggest"] = vals["approval_suggest"]
            vals["copy_suggest"] = vals["copy_suggest"]
            return super(syt_oa_gld_template, self).create(vals)