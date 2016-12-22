# -*- coding: utf-8 -*-
__author__ = 'suntao'

from openerp import api, models, exceptions, fields, _
from wechat_enterprise_basic import WeChatEnterprise
import logging
import json
from json import *

_logger = logging.getLogger(__name__)


class WechatEnterpriseSendMessage(models.Model):
    _name = 'wechat.enterprise.send.message'
    _description = 'Wechat Enterprise Send Message Manage'

    touser = fields.Many2many('hr.employee', 'send_message_to_hr_employee_ref',
                              'wechat_contacts_id', 'touser', u'成员列表')
    toparty = fields.Many2many('hr.department', 'send_message_to_hr_department_ref',
                               'id', 'toparty', u'部门列表')
    totag = fields.Many2many('wechat.enterprise.contact.tag', 'send_message_to_contact_tag_ref',
                             'tagid', 'totag', u'标签列表')
    msgtype = fields.Selection([('text', u'文字消息'), ('image', u'图片消息'), ('voice', u'语音消息'), ('video', u'视频消息')
                                   , ('file', u'文件消息'), ('news', u'图文消息'), ('mpnews', u'微信后台图文消息')], u'消息类型',
                               required=True, default='text')
    agentid = fields.Many2one('wechat.enterprise.app', u'发送消息的企业应用',required=True)
    content = fields.Char(u'消息内容')
    media_id = fields.Char(u'媒体文件')
    title = fields.Char(u'标题')
    description = fields.Text(u'描述')
    articles = fields.Char(u'图文消息')
    url = fields.Char(u'点击后跳转的链接')
    picurl = fields.Char(u'图文消息的图片链接')
    thumb_media_id = fields.Char(u'图文消息缩略图')
    author = fields.Char(u'图文消息的作者')
    content_source_url = fields.Char(u'图文消息点击“阅读原文”之后的页面链接')
    news_content = fields.Char(u'图文消息的内容，支持html标签')
    digest = fields.Char(u'图文消息的描述')
    show_cover_pic = fields.Selection([('0', u'否'), ('1', u'是')], u'是否显示封面', default='0')
    safe = fields.Selection([('0', u'否'), ('1', u'是')], u'是否是保密消息', required=True, default='0')

    # 发送消息给关注企业号的用户
    @api.one
    def send_message(self):
        '''
        发送消息给关注企业号的用户
        :return:
        发送消息
        参数	必须	说明
            touser	否	员工ID列表（消息接收者，多个接收者用‘|’分隔）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            toparty	否	部门ID列表，多个接收者用‘|’分隔。当touser为@all时忽略本参数
            totag	否	标签ID列表，多个接收者用‘|’分隔。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：text
            agentid	是	企业应用的id，整型。可在应用的设置页面查看
            content	是	消息内容
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0
        '''
        users = ""
        i = 0
        if self.touser and len(self.touser)>0:
            for data in self.touser:
                i = i + 1
                if i == len(self.touser):
                    if data['user_id']:
                        users = users + data['user_id']["login"]
                    elif data["work_email"]:
                        users = users + data['work_email']
                else:
                    if data['user_id']:
                        users = users + data['user_id']["login"] + "|"
                    elif data["work_email"]:
                        users = users + data['work_email'] + "|"
        partys = ""
        m = 0
        if self.toparty and len(self.toparty)>0:
            for data in self.toparty:
                m = m + 1
                if m == len(self.toparty):
                    partys = partys + str(data['id'])
                else:
                    partys = partys + str(data['id']) + "|"

        if self.msgtype == "news":
            data = {}
            data['touser'] = [(6, 0, self.touser.ids)]
            data['toparty'] = [(6, 0, self.toparty.ids)]
            data['agentid'] = self.agentid['id']
            data['msgtype'] = "news"
            data['title'] = self.title
            data['description'] = self.description
            data['url'] = self.url
            data['picurl'] = self.picurl
            self.create(data)
            self.send_news_message(users,self.agentid['agentid'], self.title, self.description, self.url, self.picurl, partys)
        elif self.msgtype == "text":
            data = {}
            data['touser'] = [(6, 0, self.touser.ids)]
            data['toparty'] = [(6, 0, self.toparty.ids)]
            data['agentid'] = self.agentid['id']
            data['msgtype'] = "text"
            data['content'] = self.content
            self.create(data)
            self.send_text_message(users, self.agentid['agentid'], self.content,partys)

    # 发送文本消息给关注企业号的用户
    def send_text_message(self, userid, agentid, content,partyid = None):
        '''
        发送文本消息给关注企业号的用户
        :return:
        发送消息
        参数	必须	说明
            userid	否	员工ID列表（消息接收者，多个接收者用‘|’分隔）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            msgtype	是	消息类型，此时固定为：text
            agentid	是	企业应用的id，整型。可在应用的设置页面查看
            content	是	消息内容
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid)
        if wechat:
            data = {}
            data['safe'] = u"0"
            data['msgtype'] = u"text"
            data['agentid'] = agentid
            data['touser'] = userid
            data['toparty'] = partyid
            data['content'] = content
            wechat.send_msg_to_user(data)
        else:
            raise exceptions.Warning(u"初始化企业号失败")


    # 发送图文消息给关注企业号的用户
    def send_news_message(self, userid, agentid, title=None, description=None, url=None, picurl=None,partyid=None):
        '''
        发送图文消息给关注企业号的用户
        :return:
        发送消息
        参数	必须	说明
            userid	否	hr.employee关联的res_user的login_email（消息接收者，多个接收者用‘|’分隔）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
            partyid	否	部门ID列表，hr_department的id，多个接收者用‘|’分隔。当touser为@all时忽略本参数
            msgtype	是	消息类型，此时固定为：text
            agentid	是	企业应用的id，整型。可在应用的设置页面查看
            safe	否	表示是否是保密消息，0表示否，1表示是，默认0
            title	否	标题
            description	否	描述
            url	否	点击后跳转的链接。
            picurl	否	图文消息的图片链接，支持JPG、PNG格式，较好的效果为大图640*320，小图80*80。如不填，在客户端不显示图片
        '''
        # 实例化 wechatEnterprise
        wechat = self.env['wechat.enterprise.config'].sudo().get_wechat(agentid)
        if wechat:
            data = {}
            data['safe'] = u"0"
            data['msgtype'] = u"news"
            data['agentid'] = agentid
            data['touser'] = userid
            data['toparty'] = partyid
            data['url'] = url
            data['title'] = title
            data['description'] = description
            data['picurl'] = picurl
            wechat.send_msg_to_user(data)
        else:
            raise exceptions.Warning(u"初始化企业号失败")





