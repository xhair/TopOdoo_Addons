# -*- coding: utf-8 -*-
__author__ = 'suntao'

from openerp import api,models,fields,_
from wechat_enterprise_basic import WeChatEnterprise
import logging, time, datetime, string
import json
from openerp.http import request
from json import *
import datetime
import time
import random
import base64
import urllib
_logger = logging.getLogger(__name__)

class WechatEnterpriseReceiveMessage(models.Model):
    _name = 'wechat.enterprise.receive.message'
    _description = 'Wechat Enterprise Receive Message Manage'

    name = fields.Char(required=True, index=True)
    ToUserName = fields.Char(u'企业号CorpID')
    FromUserName = fields.Char(u'成员UserID')
    CreateTime = fields.Char(u'消息创建时间')
    MsgId = fields.Char(u'消息id')
    AgentID = fields.Many2one('wechat.enterprise.app',u'企业应用')
    MsgType = fields.Selection([('text', u'文本'),
                                     ('voice', u'语音'),
                                     ('image', u'图片'),
                                     ('video', u'视频'),
                                     ('shortvideo', u'短视频'),
                                     ('location', u'位置'),
                                     ('link', u'链接'),
                                     ('subscribe', u'关注'),
                                     ('unsubscribe', u'取消关注'),
                                     ('view', u'自定义菜单链接跳转'),
                                     ('click', u'自定义菜单点击'),
                                     ('scan', u'扫描二维码'),
                                     ('scancode_waitmsg', u'扫描二维码并等待'),
                                     ('event', u'取消关注')],
                                    string=u'消息类型', required=True, default='text')
    Content = fields.Text(u'文本消息内容')
    state = fields.Selection([('1', u'未处理'), ('2', u'已处理'), ('3', u'处理失败')], u'状态', default='1')
    PicUrl = fields.Char(u'图片链接')
    MediaId = fields.Char(u'图片媒体文件id')
    Format = fields.Char(u'语音格式')
    ThumbMediaId = fields.Char(u'视频消息缩略图的媒体id')
    Location_X = fields.Char(u'地理位置纬度')
    Location_Y = fields.Char(u'地理位置经度')
    Scale = fields.Char(u'地图缩放大小')
    Label = fields.Char(u'地理位置信息')
    Title = fields.Char(u'标题')
    Description = fields.Char(u'描述')
    Cover_PicUrl = fields.Char(u'封面缩略图的url')

    @api.multi
    @api.depends('MsgType', 'MsgId')
    def name_get(self):
        result = []
        for receive in self:
            name = receive.MsgType + '_' + receive.MsgId
            result.append((receive.id, name))
        return result


    def add_message(self, data):
        '''
        增加一条待处理的上传消息
        :param AgentID:
        :param Content:
        :return:
        '''

        app = request.env['wechat.enterprise.app'].sudo().search([("agentid","=",data["AgentID"])])
        receive_message_data = {}
        receive_message_data["AgentID"] = app.id
        receive_message_data["MsgType"] = data["MsgType"]
        receive_message_data["FromUserName"] = data["FromUserName"]
        receive_message_data["ToUserName"] = data["ToUserName"]
        current_time = datetime.datetime.now()
        real_time = current_time + datetime.timedelta(hours=8)
        receive_message_data["CreateTime"] =  real_time
        receive_message_data["name"] = data["MsgType"] + data["MsgId"]

        if data["MsgType"] == "text":
            receive_message_data["MsgId"] = data["MsgId"]
            receive_message_data["Content"] = data["Content"]
        if data["MsgType"] == "image":
            receive_message_data["MsgId"] = data["MsgId"]
            receive_message_data["PicUrl"] = data["PicUrl"]
            receive_message_data["MediaId"] = data["MediaId"]
        if data["MsgType"] == "voice":
            receive_message_data["MsgId"] = data["MsgId"]
            receive_message_data["MediaId"] = data["MediaId"]
            receive_message_data["Format"] = data["Format"]
        if data["MsgType"] == "video" or data["MsgType"] == "shortvideo":
            receive_message_data["MsgId"] = data["MsgId"]
            receive_message_data["MediaId"] = data["MediaId"]
            receive_message_data["ThumbMediaId"] = data["ThumbMediaId"]
            # wechat = WeChatEnterprise(agentid = 1)
            # file = wechat.get_media(data["MediaId"])
            # verification_code = random.randint(10000, 99999)  # 5位随机码
            # vals = {}
            # vals["db_datas"] = file
            # vals["name"] = str(verification_code) + ".avi"
            # vals["type"] = "binary"
            # vals["res_model"] = "wechat.enterprise.receive.message"
            # request.env["ir.attachment"].sudo().sudo().create(vals)
        if data["MsgType"] == "location":
            receive_message_data["MsgId"] = data["MsgId"]
            receive_message_data["Location_X"] = data["Location_X"]
            receive_message_data["Location_Y"] = data["Location_Y"]
            receive_message_data["Scale"] = data["Scale"]
            receive_message_data["Label"] = data["Label"]
        if data["MsgType"] == "link":
            receive_message_data["MsgId"] = data["MsgId"]
            receive_message_data["Title"] = data["Title"]
            receive_message_data["Description"] = data["Description"]
            receive_message_data["Cover_PicUrl"] = data["PicUrl"]
        if data["MsgType"] == "event":
            if data["Event"] == "subscribe":
                receive_message_data["MsgType"] = "subscribe"
            if data["Event"] == "unsubscribe":
                receive_message_data["MsgType"] = "unsubscribe"

        return super(WechatEnterpriseReceiveMessage, self).create(receive_message_data)

    def process_message(self,data):
        '''
        处理未处理和失败的消息
        :return:
        '''
        messages = self.sudo().add_message(data)
        for message in messages:
            # 处理具体的业务
            if message:
                # 检查已处理的消息不进行处理
                if message.state == '2':
                    break
                if data["MsgType"] == "text":
                    process = self.env['wechat.enterprise.receive.message.process'].get_message_process(data["MsgType"],
                                                                                         data["Content"],
                                                                                         data["AgentID"])
                else:
                    process = self.env['wechat.enterprise.receive.message.process'].get_message_process(data["MsgType"],
                                                                                         " ",
                                                                                         data["AgentID"])
                try:
                    if process:
                        if data["MsgType"] == "voice" or data["MsgType"] == "image" or data["MsgType"] == "video" or data["MsgType"] == "shortvideo":
                            process.sudo().exec_class_mothed(data["FromUserName"], data["AgentID"],data["MediaId"])
                        else:
                            process.sudo().exec_class_mothed(data["FromUserName"], data["AgentID"])
                    else:
                        return self.env['wechat.enterprise.send.message'].send_text_message(data["FromUserName"],data["AgentID"],content=u'感谢您的关注！')

                    message.sudo().write({'state': '1'})
                except Exception, e:
                    message.sudo().write({'state': u'处理失败'})
