# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # 为type属性增加两个值
    # @api.multi
    # def _add_product_template_type(self):
    #    res = super(ProductTemplate, self)._get_product_template_type()
    #    res.append(('accessories', u'配件'))
    #    return res

    # _get_product_template_type_wrapper = lambda self, *args, **kwargs: self._add_product_template_type(*args, **kwargs)

    # type = fields.Selection(_get_product_template_type_wrapper, string=u'类型',required=True)


    default_code = fields.Char(string=u'内部编码', default='/', required=True, help='内部编码')
    factory_code = fields.Char(string=u'原厂编码', select=True)
    is_part = fields.Boolean(u'这是配件', default=False)
    brands_id = fields.Many2one('toproerp.brands', string=u'品牌', index=True)
    apply_to_brand_ids = fields.Many2many('toproerp.brands', string=u'适用的品牌')
    appy_to_car_brands_count = fields.Integer(string=u'适用品牌总数(作废)')
    replace_part_ids = fields.Many2many('product.product', 'product_temp_replace_rel', 'product_id', 'replace_id',
                                        string=u'可替换配件', domain=[('type', '<>', 'services'), ('is_part', '=', True)])

