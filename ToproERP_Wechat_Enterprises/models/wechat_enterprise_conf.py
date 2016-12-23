# -*- coding: utf-8 -*

import logging
from openerp.http import request
from openerp import api,models,exceptions,fields,_
from wechat_enterprise_basic import WeChatEnterprise
from json import *
_logger = logging.getLogger(__name__)

class WechatEnterpriseConfigration(models.Model):

    _name = 'wechat.enterprise.config'

    name = fields.Char(u'企业号名称',required=True,help=u'为企业号去个好名字吧！')
    corp_id = fields.Char(u'CorpID',required=True,help=u'企业号ID，必填项')
    corp_secret = fields.Char(u'Secret',required=True,help=u'企业号secret,必填项')


    def get_wechat(self,agentid = 0):
        '''
        取得wechat enterprise的实例
        :param agentid:
        :return:
        '''

        conf = self.env['wechat.enterprise.config'].sudo().search([],limit=1)
        agent = self.env['wechat.enterprise.app'].sudo().search([("agentid","=",int(agentid))],limit=1)

        if conf:
            return WeChatEnterprise(conf.corp_id,conf.corp_secret,agentid,agent.Token,agent.EncodingAESKey)

    @api.one
    def get_app(self):
        '''
        从微信获取app列表
        :return:
        '''
        # 实例化 wechatEnterprise
        datas = self.env['wechat.enterprise.app'].search([])
        for item in datas:
            item.unlink()
        wechat = self.get_wechat(agentid = 0)
        if wechat:
            try:
                app_lists = wechat.get_app_lists()
                app_lists = app_lists[1]['agentlist']
                if app_lists:
                    for app_list in app_lists:
                        app_detail = wechat.get_app_details(app_list['agentid'])
                        app_detail = app_detail[1]
                        if app_detail:
                            data = {}
                            data['agentid'] = str(app_detail['agentid'])
                            my_app = request.env["wechat.enterprise.app"].search([("agentid", "=", str(app_detail['agentid']))])
                            if my_app and len(my_app)>0:
                                continue
                            data['name'] = app_detail['name']
                            data['square_logo_url'] = app_detail['square_logo_url']
                            data['round_logo_url'] = app_detail['round_logo_url']
                            data['description'] = app_detail['description']
                            data['close'] = str(app_detail['close'])
                            data['redirect_domain'] = app_detail['redirect_domain']
                            data['report_location_flag'] = str(app_detail['report_location_flag'])
                            data['isreportuser'] = str(app_detail['isreportuser'])
                            data['isreportenter'] = str(app_detail['isreportenter'])
                            data['type'] = str(app_detail['type'])
                            request.env["wechat.enterprise.app"].create(data)

            except Exception, e:
                _logger.warning(u'获取应用列表失败,原因：%s',e.message)
                print e.message
                raise Warning(_(u'获取应用列表失败,原因：%s',e.message))
        else:
            raise exceptions.Warning(u"获取应用列表失败")

    # 限制企业号的配置数量
    @api.constrains('name')
    def check_menu_number(self):
        '''
        :return:
        '''
        menus_ids = self.sudo().search([])

        if menus_ids and len(menus_ids)>1:
            raise Warning(_(u'只能定义1个企业号.'))
        return True

    @api.multi
    def get_data_param(self):
        account = self.sudo().search([], limit=1)
        if account:
            data = {}
            data['corp_id'] = account.corp_id
            data['corp_secret'] = account.corp_secret
            JSONEncoder().encode(data)
            return data
        else:
            return None