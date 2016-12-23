# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class AccountTestUsers(TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(AccountTestUsers, self).setUp()
        self.res_user_model = self.env['res.users']
        self.hr_department_model = self.env['hr.department']

        self.template_type_model = self.env['gld.template.type']
        self.template_model = self.env['gld.template']
        self.gld_model = self.env['gld']
        base_group_user = self.env.ref('base.group_user')
        base_partner_manager = self.env.ref('base.group_partner_manager')
        # 建立用户部门
        department_t = self.hr_department_model.create({
            'name': u'测试部门',
        })
        self.user1 = self.res_user_model.with_context({'no_reset_password': True}).create(dict(
            name="user1",
            login="user1",
            email="user1@qq.com",
            department_id=department_t.id,
            groups_id=[(6, 0, [base_group_user.id, base_partner_manager.id])]
        ))
        self.user2 = self.res_user_model.with_context({'no_reset_password': True}).create(dict(
            name="user2",
            login="user2",
            email="user2@qq.com",
            department_id=department_t.id,
            groups_id=[(6, 0, [base_group_user.id, base_partner_manager.id])]
        ))
        self.user3 = self.res_user_model.with_context({'no_reset_password': True}).create(dict(
            name="user3",
            login="user3",
            email="user3@qq.com",
            department_id=department_t.id,
            groups_id=[(6, 0, [base_group_user.id, base_partner_manager.id])]
        ))
        self.user4 = self.res_user_model.with_context({'no_reset_password': True}).create(dict(
            name="user4",
            login="user4",
            email="user4@qq.com",
            department_id=department_t.id,
            groups_id=[(6, 0, [base_group_user.id, base_partner_manager.id])]
        ))
        # 创建模板 及模板类型
        self.template_type1=self.template_type_model.create({
            'name':'template_type1'
        })
        self.template1 = self.template_model.create({
            'name': 'template1',
            'temp_type': self.template_type1.id,
            'is_valid': True,
            'emergency': 'urgent',
            'subject': 'template1subject',
            'content': 'template1content'
        })
        self.gld1 = self.gld_model.create({

        })
