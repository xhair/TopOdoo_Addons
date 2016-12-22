# -*- coding:utf-8 -*-
__author__ = 'suntao'

import time
import json
import hashlib
import requests
import functools
from json import *
import urllib2
import base64
from openerp import api, http, fields, models, tools
from openerp.http import request
from wechat_enterprise_basic import WeChatEnterprise
import WXBizMsgCrypt
import xml.etree.cElementTree as ET

from werkzeug.exceptions import abort

import logging

_logger = logging.getLogger(__name__)


def wechat_login(func):
    '''
    用来根据userid取得合作伙伴的id
    :return:
    '''

    @functools.wraps(func)
    def wrapper(*args, **kw):
        now_time = time.time()
        if not 'session_time' in request.session:
            request.session['session_time'] = 1
        if (now_time > request.session['session_time'] + 350):
            print u"没进来之前的kw值为%s" % JSONEncoder().encode(kw)
            if not request.session['login'] or request.session['login'] == None or request.session[
                'login'] == "public":  # 检查是否存在request.uid
                enterprise = request.env['wechat.enterprise.config'].sudo().get_wechat(agentid=0)
                if enterprise:
                    if 'code' in kw and 'state' in kw:  # 检查是否取得了code
                        account = enterprise.get_enterprise_account_by_code(kw['code'])
                        if account:  # 是否取得了微信企业号通讯录的账号
                            user = request.env['res.users'].sudo().search([('login', '=', account)])
                            print user
                            if user:  # 是否取得了用户
                                if 'state' in kw:
                                    state = JSONDecoder().decode(base64.decodestring(kw['state']))
                                    kw = state
                                request.httprequest.session['login'] = account
                                request.httprequest.session['uid'] = user.id
                                request.session['session_time'] = time.time()
                                request.session.login = account
                                request.session.uid = user.id
                                kw['user_id'] = user.id
                                request.uid = user.id
                                # kw = {}
                                print u"进来之后的kw值为%s" % kw
                                return func(*args, **kw)
                            else:
                                _logger.warning('用户不存在.')
                                # return request.render('ToproERP_Wechat_Enterprises.wechat_warning',{'title':u'警告','content':u'用户不存在.'})
                                return " "
                        else:
                            _logger.warning('微信企业号验证失败.')
                            return request.render('ToproERP_Wechat_Enterprises.wechat_warning',
                                                  {'title': u'警告', 'content': u'微信企业号验证失败.'})
                    else:  # 开始微信企业号登录认证
                        request.session['kw'] = base64.encodestring(JSONEncoder().encode(kw))
                        url = enterprise.get_authorize_url(request.httprequest.base_url,state=base64.encodestring(JSONEncoder().encode(kw)))
                        _logger.info('url: %s' % url)
                        value = {"url": url}
                        return request.render("ToproERP_Wechat_Enterprises.Transfer", value)
                else:
                    _logger.warning('微信企业号初始化失败.')
                    return request.render('ToproERP_Wechat_Enterprises.wechat_warning',
                                          {'title': u'警告', 'content': u'微信企业号初始化失败.'})

    return wrapper


class WechatEnterprise(http.Controller):
    '''
   用于接收微信发过来的任何消息，并转发给相应的业务类进行处理
   '''
    __check_str = 'NDOEHNDSY#$_@$JFDK:Q{!'

    @http.route('/WechatEnterprise/<string:code>/api', type='http', auth="public", methods=["POST", "GET"], csrf=False)
    def process(self, request, code, msg_signature=None, timestamp=None, nonce=None, echostr=None):
        '''
        处理从微信服务器发送过来的请求
        :param request:
        :param code:
        :param signature:
        :param timestamp:
        :param nonce:
        :param echostr:
        :return:
        '''
        _logger.debug('WeChat connected: code=%s, signature=%s, timestamp=%s, nonce=%s, echostr=%s', code,
                      msg_signature, timestamp,
                      nonce, echostr)

        # 根据code获取当前的应用

        app = request.env['wechat.enterprise.app'].sudo().search([('code', '=', code)])

        if not app:
            _logger.warning('Can not find wechat app by code:%s.', code)
            abort(403)

        # 实例化 wechat
        wechat = request.env['wechat.enterprise.config'].sudo().get_wechat(agentid=app['agentid'])
        # wechat = WeChatEnterprise(agentid = app['agentid'])
        # 对签名进行校验
        res, rechostr = wechat.check_signature(sVerifyMsgSig=msg_signature, sVerifyTimeStamp=timestamp,
                                               sVerifyNonce=nonce, sVerifyEchoStr=echostr)

        if wechat.check_signature(sVerifyMsgSig=msg_signature, sVerifyTimeStamp=timestamp, sVerifyNonce=nonce,
                                  sVerifyEchoStr=echostr):
            # 处理开发验证
            _logger.debug(u'验证通过...')

            if rechostr and rechostr != None:
                return rechostr

            body_text = request.httprequest.data  # 获取微信传过来的消息体
            corp_id = request.env['wechat.enterprise.config'].sudo().search([], limit=1)
            sCorpID = corp_id.corp_id
            wxcpt = WXBizMsgCrypt.WXBizMsgCrypt(app['Token'], app['EncodingAESKey'], sCorpID)
            ret, sMsg = wxcpt.DecryptMsg(body_text, msg_signature, timestamp, nonce)
            if (ret != 0):
                print "ERR: DecryptMsg ret: " + str(ret)
            xml_tree = ET.fromstring(sMsg)  # 解析消息
            data = {}
            data["MsgType"] = xml_tree.find("MsgType").text
            data["AgentID"] = xml_tree.find("AgentID").text
            data["ToUserName"] = xml_tree.find("ToUserName").text
            data["FromUserName"] = xml_tree.find("FromUserName").text
            data["CreateTime"] = xml_tree.find("CreateTime").text
            if data["MsgType"] == "text":
                data["Content"] = xml_tree.find("Content").text
                data["MsgId"] = xml_tree.find("MsgId").text
            if data["MsgType"] == "image":
                data["PicUrl"] = xml_tree.find("PicUrl").text
                data["MediaId"] = xml_tree.find("MediaId").text
                data["MsgId"] = xml_tree.find("MsgId").text
            if data["MsgType"] == "voice":
                data["MediaId"] = xml_tree.find("MediaId").text
                data["Format"] = xml_tree.find("Format").text
                data["MsgId"] = xml_tree.find("MsgId").text
            if data["MsgType"] == "video" or data["MsgType"] == "shortvideo":
                data["MediaId"] = xml_tree.find("MediaId").text
                data["ThumbMediaId"] = xml_tree.find("ThumbMediaId").text
                data["MsgId"] = xml_tree.find("MsgId").text
            if data["MsgType"] == "location":
                data["Location_X"] = xml_tree.find("Location_X").text
                data["Location_Y"] = xml_tree.find("Location_Y").text
                data["Scale"] = xml_tree.find("Scale").text
                data["Label"] = xml_tree.find("Label").text
                data["MsgId"] = xml_tree.find("MsgId").text
            if data["MsgType"] == "link":
                data["Title"] = xml_tree.find("Title").text
                data["Description"] = xml_tree.find("Description").text
                data["PicUrl"] = xml_tree.find("PicUrl").text
                data["MsgId"] = xml_tree.find("MsgId").text
            if data["MsgType"] == "event":
                if xml_tree.find("Event") == "subscribe" or xml_tree.find("Event") == "unsubscribe":
                    data["Event"] = xml_tree.find("Event").text
                else:
                    return " "
            print data
            request.env['wechat.enterprise.receive.message'].sudo().process_message(data)
            return " "
        else:
            return "45"

    @http.route('/WechatEnterprise/transfer', type='http', auth="public", methods=["POST", "GET"], csrf=False)
    def transfer(self, url):
        value = {"url": url}
        return request.render('ToproERP_Wechat_Enterprises.Transfer', value)

    @http.route('/WechatEnterprise/haha', type='http', auth="public", methods=["POST", "GET"], csrf=False)
    def haha(self):
        return "haha"

    @http.route(['/WechatEnterprise/image/<string:model>/<string:id>/<string:field>',
                 '/WechatEnterprise/image/<string:model>/<string:id>/<string:field>/<int:width>x<int:height>'],
                type='http', auth='public', csrf=False)
    def get_image(self, id, model, field, width=0, height=0, *args, **kwargs):
        obj = request.env[model].sudo().browse(int(id))
        if obj and field in obj:
            content = obj[field]
            if width and height:
                content = tools.image_resize_image(base64_source=obj[field], size=(width, height), filetype='PNG',
                                                   avoid_if_small=True)
            return base64.decodestring(content)
        else:
            response = request.make_response()
            response.status = 404
            return response

    @wechat_login
    @http.route('/WechatEnterprise/show_attatchment/<string:id>', type='http', auth='public', csrf=False)
    def show_attatchment(self, id, *args, **kwargs):
        obj = request.env['ir.attachment'].sudo().browse(int(id))
        if obj:
            content = base64.decodestring(obj['datas'])
            response = request.make_response(content, headers=[
                ('Content-Type', obj['mimetype']), ('Content-Length', len(content))])
            #response.headers.add('Content-Disposition', 'inline;filename="%s"' % (request.env['toproerp.common'].encode_utf8_to_iso88591(obj['name'])))
            #response.headers.add('Content-Disposition', 'inline;filename="123.pdf')
        else:
            response = request.make_response()
            response.status = 404

        return response
      

