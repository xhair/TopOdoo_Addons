# -*- coding: utf-8 -*-

import time

from openerp import models, api, fields, exceptions

class WechatGldOpinion(models.Model):
    _inherit = 'gld.opinion'
    _description = u'审批意见微信版'

    @api.multi
    def save_opinion(self):
        '''
        保存审批意见：同意
        :return:
        '''
        # 修改工联单的状态为“审批中”
        print('wechat save_opinion')
        gld_bean = self.env['gld'].sudo().search([('id', '=', self._context.get('gld_id'))])
        if gld_bean:
            # gid = 0
            if gld_bean['state'] == 'draft':
                raise exceptions.Warning(u"该工联单已经被置为草稿！")
            if gld_bean['state'] in ('n_through', 'through', 'cancel'):
                raise exceptions.Warning(u"该工联单已经被置为完成！")
            else:
                employee = self.env['gld.common'].get_login_user()
                self.save_opinion_service(self._context.get('gld_id'), self.opinion, self._context.get('check_state'),
                                          employee, 1)
                title = u'单号：%s' % gld_bean.name
                if self.opinion == False:
                    self.opinion = u'无'
                description = u"%s审核了单号为%s的工联单，审批意见为：%s。请点击查看全文！" % (self.approver.name, gld_bean.name, self.opinion)
                user = gld_bean.sponsor.user_id.login
                icp = self.env['ir.config_parameter']
                insur_str = icp.get_param('web.base.url')
                agentid = self.env['wechat.enterprise.app'].sudo().search([('name', '=', u'工联单')])
                url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                    gld_bean.name, '2', gld_bean.sponsor.id)  # 跳转地址，需要和微信保持一致
                self.env['wechat.enterprise.send.message'].sudo().send_news_message(user, agentid.agentid,
                                                                                    title, description, url)

