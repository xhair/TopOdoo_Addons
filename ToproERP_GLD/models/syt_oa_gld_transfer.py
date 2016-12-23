# -*- coding: utf-8 -*-
import xlrd
import re

from openerp import models, api, fields, exceptions
from openerp.exceptions import Warning, ValidationError


class SytOaGldTransfer(models.TransientModel):
    _name = 'syt.oa.gld.transfer'
    _description = u'工联单交接'

    surrender_employee_id = fields.Many2one('hr.employee', string=u'交出员工', required=True)
    accept_employee_id = fields.Many2one('hr.employee', string=u'接受员工', required=True)

    @api.multi
    def sure(self):
        if self.surrender_employee_id and self.accept_employee_id:
            if int(self.surrender_employee_id) == int(self.accept_employee_id):
                raise exceptions.Warning(u'请选择不同的员工进行交接！')
            else:
                # 交出员工
                surrender_employee_id = int(self.surrender_employee_id)
                # 接受员工
                accept_employee_id = int(self.accept_employee_id)

                # count = 0
                # # 查询总条数
                # # 1:条件：交出员工所发起的工联单，接受员工
                # self._cr.execute(
                #     'select distinct count(a.id) from syt_oa_gld a left join syt_oa_gld_yiyue_rel b on a.id=b.gld_id where a.sponsor = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=a.id and employee_id=%s) ;',
                #     (surrender_employee_id, accept_employee_id))
                # one_count = [r[0] for r in self._cr.fetchall()]
                # print 'one_count:%s' % one_count[0]
                #
                # # 2:条件：交出员工所已审批的工联单，接受员工
                # self._cr.execute(
                #     'select distinct count(b.id) from syt_oa_gld_opinion a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_yiyue_rel c on b.id=c.gld_id where a.approver = %s and b.sponsor != %s and b.state not in(%s,%s)  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
                #     (surrender_employee_id, surrender_employee_id, 'pending', 'pass',
                #      accept_employee_id))
                # two_count = [r[0] for r in self._cr.fetchall()]
                # print 'two_count:%s' % two_count[0]
                #
                # # 3:条件：交出员工所未审批的工联单，接受员工
                # self._cr.execute(
                #     'select distinct count(b.id) from syt_oa_gld_opinion a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_appover_rel c on b.id=c.gld_id where a.approver = %s and b.sponsor != %s and b.state in(%s,%s) and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
                #     (surrender_employee_id, surrender_employee_id, 'pending', 'pass',
                #      accept_employee_id))
                # three_count = [r[0] for r in self._cr.fetchall()]
                # print 'three_count:%s' % three_count[0]
                #
                # # 4:条件：交出员工所被抄送的工联单(待阅)，接受员工
                # self._cr.execute(
                #     'select distinct count(a.gld_id) from syt_oa_gld_daiyue_rel a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_yiyue_rel c on b.id=c.gld_id where a.employee_id = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
                #     (surrender_employee_id, accept_employee_id))
                # four_count = [r[0] for r in self._cr.fetchall()]
                # print 'four_count:%s' % four_count[0]
                #
                # # 5:条件：交出员工所被抄送的工联单(已阅)，接受员工
                # self._cr.execute(
                #     'select distinct count(a.gld_id) from syt_oa_gld_yiyue_rel a left join syt_oa_gld b on a.gld_id = b.id where a.employee_id = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
                #     (surrender_employee_id, accept_employee_id))
                # five_count = [r[0] for r in self._cr.fetchall()]
                # print 'five_count:%s' % five_count[0]
                #
                # count = one_count[0] + two_count[0] + three_count[0] + four_count[0] + five_count[0]
                # print 'count:%s' % count

                # 1：交接：往抄送人表添加数据 （条件：交出员工所发起的工联单，接受员工）
                self._cr.execute(
                    'insert into syt_oa_gld_yiyue_rel select distinct a.id,%s from syt_oa_gld a left join syt_oa_gld_yiyue_rel b on a.id=b.gld_id where a.sponsor = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=a.id and employee_id=%s) ;',
                    (accept_employee_id, surrender_employee_id, accept_employee_id))

                # 2：交接：往抄送人表添加数据 （条件：交出员工所已审批的工联单，接受员工）
                self._cr.execute(
                    'insert into syt_oa_gld_yiyue_rel select distinct b.id,%s from syt_oa_gld_opinion a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_yiyue_rel c on b.id=c.gld_id where a.approver = %s and b.sponsor != %s and b.state not in(%s,%s)  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
                    (accept_employee_id, surrender_employee_id, surrender_employee_id, 'pending', 'pass',
                     accept_employee_id))

                # 3：交接：往待审批的人中间表添加数据 （条件：交出员工所未审批的工联单，接受员工）
                self._cr.execute(
                    ' insert into syt_oa_gld_appover_rel select distinct b.id,%s from syt_oa_gld_opinion a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_appover_rel c on b.id=c.gld_id where a.approver = %s and b.sponsor != %s and b.state in(%s,%s) and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
                    (accept_employee_id, surrender_employee_id, surrender_employee_id, 'pending', 'pass',
                     accept_employee_id))

                # 4：交接：往抄送人表添加数据 （条件：交出员工所被抄送的工联单(待阅)，接受员工）
                self._cr.execute(
                    'insert into syt_oa_gld_yiyue_rel select distinct a.gld_id,%s from syt_oa_gld_daiyue_rel a left join syt_oa_gld b on a.gld_id = b.id left join syt_oa_gld_yiyue_rel c on b.id=c.gld_id where a.employee_id = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
                    (accept_employee_id, surrender_employee_id, accept_employee_id))

                # 5：交接：往抄送人表添加数据 （条件：交出员工所被抄送的工联单(已阅)，接受员工）
                self._cr.execute(
                    'insert into syt_oa_gld_yiyue_rel select distinct a.gld_id,%s from syt_oa_gld_yiyue_rel a left join syt_oa_gld b on a.gld_id = b.id where a.employee_id = %s  and not exists(select 1 from syt_oa_gld_yiyue_rel where gld_id=b.id and employee_id=%s) ;',
                    (accept_employee_id, surrender_employee_id, accept_employee_id))

                # 6：交接完成后，修改（审批意见表）交出员工未审批的所有工联单的现有审批人为接受员工，已审批的不改变
                self._cr.execute(
                    'update syt_oa_gld_opinion set approver =%s where approver=%s and opinion is null;',
                    (accept_employee_id, surrender_employee_id))

                # 7：交接完成后，修改（未审批人表）交出员工未审批的所有工联单的现有审批人为接受员工，已审批的不改变
                # insert into syt_oa_gld_appover_rel select b.gld_id,%s from syt_oa_gld_appover_rel a inner join syt_oa_gld_opinion b on a.gld_id = b.gld_id where a.employee_id = b.approver and b.opinion is null;
                self._cr.execute(
                    'delete from syt_oa_gld_appover_rel where employee_id=%s;',
                    (surrender_employee_id,))
                # self._cr.execute(
                #     'update syt_oa_gld_appover_rel set employee_id =%s from syt_oa_gld_appover_rel a inner join syt_oa_gld_opinion b on a.gld_id = b.gld_id where a.employee_id = b.approver and b.opinion is null;',(accept_employee_id,))

                # 获取工联单的微信编号 只发送到工联单模块里面
                agentid = self.env['wechat.enterprise.app'].sudo().search([('name', '=', u'工联单')])
                if agentid:
                    wechat_address_number = ''  # 微信通讯录编号
                    accept_employee_obj = self.env['hr.employee'].sudo().search([('id', '=', int(accept_employee_id))])
                    surrender_employee_obj = self.env['hr.employee'].sudo().search(
                        [('id', '=', int(surrender_employee_id))])
                    user = self.env['res.users'].sudo().search([('id', '=', accept_employee_obj.user_id.id)])
                    wechat_address_number += user.login + '|'
                    surrender_name = ''
                    if surrender_employee_obj:
                        surrender_name = surrender_employee_obj.name
                    self.env['wechat.enterprise.send.message'].send_news_message(wechat_address_number[:-1],
                                                                                 agentid.agentid,
                                                                                 u'您已经接收到 ' + surrender_name + u' 的所有工联单，请及时查看! ',
                                                                                 '', '')
