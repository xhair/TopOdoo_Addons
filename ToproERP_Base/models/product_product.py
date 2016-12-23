# -*- coding: utf-8 -*-

from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    # @api.multi
    # def name_get(self):
    #     product = self.with_context(display_default_code=False)
    #     return super(ProductProduct, product).name_get()


    @api.multi
    @api.depends('name', 'remark')
    def name_get(self):
        '''
        客户名称显示：名称+电话+车牌
        :return:
        '''
        code = self._context.get('display_default_code', True) or False
        result = []
        remark = ''
        default_code = '/'
        for item in self:
            if code:
                if item.default_code:
                    default_code = item.default_code
                if item.remark:
                    remark = item.remark
                    name = '[' + default_code + ']' + item.name + '&' + remark
                else:
                    name = '[' + default_code + ']' + item.name
                result.append((item.id, name))
            else:
                result.append((item.id, '[' + default_code + ']' + item.name))
        return result

    remark = fields.Char(string=u'备注(适用车型)', select=True)
