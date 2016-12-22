# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, exceptions
import re
import logging

_logger = logging.getLogger(__name__)


class ToproerpUsers(models.Model):
    _inherit = "res.users"
    _description = u'根据公司、权限组ID获取用户列表'

    allow_export = fields.Boolean(u'是否允许导出', default=False)

    def get_jurisdiction(self, name):
        '''
        根据权限组名称获取权限
        :param name: 权限组名称，例如："预约专员"
        :return: 返回当前对象的id ,此Id为权限组id
        '''
        jurisdiction_obj = self.sudo().env["res.groups"].search([('name', '=', name)], limit=1)
        return jurisdiction_obj.id

    def get_users(self, company_id=None, jurisdiction_id=None):
        '''
        根据公司、权限组ID 获取用户
        :param company_id: 公司Id
        :param jurisdiction_id: 权限组id
        :return:返回 用户列表
        '''
        users = self.search([('company_id', '=', int(company_id))])
        users_ids = []  # 当前公司下的用户id 集合
        # group_ids = []  # 当前公司下、满足当前权限组的用户id 集合
        for user in users:
            users_ids.append(int(user.id))
        # groups_users_obj = self.env["res_groups_users_rel"].sudo().search([('gid', '=', int(jurisdiction_id))])
        users_ids = str(users_ids).replace('[', '(').replace(']', ')')
        self._cr.execute(
            "select uid from res_groups_users_rel where gid =%s and uid in " + users_ids + "", (int(jurisdiction_id),))
        groups_users_obj = [r[0] for r in self._cr.fetchall()]
        user_obj = self.search([('id', 'in', groups_users_obj)])
        return user_obj

    def get_users_list(self, company_id=None, jurisdiction_id=None):
        '''
        根据公司、权限组ID 获取用户
        :param company_id: 公司Id
        :param jurisdiction_id: 权限组id
        :return:返回 用户列表
        '''
        group = self.env['res.groups'].sudo().search([('id', '=', jurisdiction_id)], limit=1)
        _logger.warning(u"the back group id：%s" % group.id)
        users = self.env["res.users"].sudo().search(
            [('company_id', '=', int(company_id)), ('groups_id', '=', group.id)])
        _logger.warning(u"the back users：%s" % users)
        return users
