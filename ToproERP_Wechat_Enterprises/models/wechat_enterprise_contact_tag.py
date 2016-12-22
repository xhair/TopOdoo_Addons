# -*- coding:utf-8 -*-
__author__ = 'suntao'

from openerp import api, models, fields, _
import json
from json import *
from wechat_enterprise_basic import WeChatEnterprise
import logging

_logger = logging.getLogger(__name__)

class WechatEnterpriseContactTag(models.Model):
    _name = 'wechat.enterprise.contact.tag'
    _description = 'Wechat Enterprise Contact Tag Manage'

    @api.constrains('name')
    def tagname_check(self):
        data = self.search([('name', '=', self.name)])
        if len(data)>1:
            raise Warning(u'标签名称必须唯一')
    @api.multi
    def tagid_check(self):
        number = self.search([])
        return len(number)+1

    name = fields.Char(u'标签名称', required=True)
    tagid = fields.Integer(string=u'标签ID', default=tagid_check, readonly=True)

    # 更新标签至微信企业号
    @api.one
    def create_tag(self):
        '''
        更新标签至微信企业号
        :return:
        创建标签
        参数	必须	说明
        access_token	是	调用接口凭证
        tagname	是	标签名称，长度为1~64个字节，标签名不可与其他标签重名。
        tagid	否	标签id，整型，指定此参数时新增的标签会生成对应的标签id，不指定时则以目前最大的id自增。
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        datas = self.sudo().search([])
        try:
            for data in datas:
                wechat.create_tag(data['name'],data['tagid'])
            for data in datas:
                wechat.update_tag(data['tagid'],data['name'])
        except Exception, e:
            _logger.warning(u'更新app失败,原因：%s', e.message)
            print e.message
            raise Warning(_(u'更新app失败,原因：%s', e.message))

    # 微信企业号获取标签
    @api.one
    def get_tag(self):
        '''
        微信企业号获取标签
        :return:
        创建标签
        参数	必须	说明
        access_token	是	调用接口凭证
        tagname	是	标签名称，长度为1~64个字节，标签名不可与其他标签重名。
        tagid	否	标签id，整型，指定此参数时新增的标签会生成对应的标签id，不指定时则以目前最大的id自增。
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid = 0)
        tags = wechat.get_tag_list()
        tags = tags[1]['taglist']
        for tag in tags:
            tag_data = {}
            tag_data['tagid'] = tag['tagid']
            my_tag = self.search([("tagid","=",tag['tagid'])])
            if my_tag:
                continue
            tag_data['name'] = tag['tagname']
            self.create(tag_data)
