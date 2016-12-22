# -*- coding: utf-8 -*-
__author__ = 'suntao'

from openerp import api, models, exceptions, fields, _
import json
from json import *
import logging
from openerp.http import request

_logger = logging.getLogger(__name__)

from openerp import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = u'员工'

    # @api.onchange('company_id')
    # def check_company(self):
    #     print self.env.user.company_id.name
    #     self.company_id = self.env.user.company_id.id
    #     department = request.env['hr.department'].search([('company_id', '=', self.company_id.id)], limit=1)
    #     self.department_id = department.id

    # @api.onchange('department_id')
    # def check_department(self):
    #     manager = request.env['hr.employee'].search([('department_id', '=', self.department_id.id)], limit=1)
    #     self.parent_id = manager.id

    company_id = fields.Many2one('res.company', string=u"公司", required=True, index=True)
    department_id = fields.Many2one('hr.department', string=u"部门", required=True, index=True)
    job_id = fields.Many2one('hr.job', string=u"职位", required=True, index=True)

    def get_users(self, company_id=None, jurisdiction_name=None):
        '''
        根据公司id、权限组名称获取满足该条件的员工
        :param company_id: 公司id
        :param jurisdiction_name:权限组名称
        :return: 返回员工列表
        '''
        # 权限组的id
        jurisdiction_id = self.env["res.users"].sudo().get_jurisdiction(jurisdiction_name)
        # 根据权限Id、公司查询的用户
        user_obj = self.env["res.users"].sudo().get_users(company_id, jurisdiction_id)
        # 根据用户做匹配，匹配到每一个员工
        users_ids = []
        for user in user_obj:
            users_ids.append(int(user.id))
        employee_obj = self.sudo().search([('user_id', 'in', users_ids)])
        print employee_obj
        return employee_obj
