# -*- coding:utf-8 -*-
import json
import requests
import urllib
import hashlib
from json import *
from xml.dom import minidom, Node
import WXBizMsgCrypt
from openerp.http import request
from wechat_sdk.messages import MESSAGE_TYPES, UnknownMessage
from wechat_sdk.exceptions import ParseError, NeedParseError, NeedParamError, OfficialAPIError
import time
import logging
_logger = logging.getLogger(__name__)
from wechat_sdk.reply import TextReply, ImageReply, VoiceReply, VideoReply, MusicReply, Article, ArticleReply


class ErrorCode(object):
    SUCCESS = 0

class WeChatEnterprise(object):

    def __init__(self, corpid,corpsecret,agentid=1,Token=None,AESKey=None):
        """
            document address: http://qydev.weixin.qq.com/wiki/index.php?title=%E9%A6%96%E9%A1%B5
        """
        # self.corpid = self._get_corpid()
        # self.corpsecret = self._get_corpsecret()
        # self.agentid = agentid
        # self.url_prefix = "https://qyapi.weixin.qq.com/cgi-bin"
        # self.access_token = self.__get_access_token()
        # self.Token = self._get_token()
        # self.EncodingAESKey = self._get_EncodingAESKey()
        # self.__message = None

        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.url_prefix = "https://qyapi.weixin.qq.com/cgi-bin"
        self.access_token = self.__get_access_token()
        self.Token = Token
        self.EncodingAESKey = AESKey
        self.__message = None

    def __get_access_token(self):
        # access_token 有效期为 7200秒
        # todo 缓存access_token
        url = "%s/gettoken?corpid=%s&corpsecret=%s" % (self.url_prefix, self.corpid, self.corpsecret)
        res = requests.get(url)
        access_token = res.json().get("access_token")
        return access_token

    # def _get_corpid(self):
    #     result = request.env['wechat.enterprise.config'].sudo().search([],limit=1)
    #     return result.corp_id
    #
    # def _get_corpsecret(self):
    #     result = request.env['wechat.enterprise.config'].sudo().search([],limit=1)
    #     return result.corp_secret
    #
    # def _get_token(self):
    #     result = request.env['wechat.enterprise.app'].sudo().search([("agentid","=",self.agentid)],limit=1)
    #     return result.Token
    #
    # def _get_EncodingAESKey(self):
    #     result = request.env['wechat.enterprise.app'].sudo().search([("agentid","=",self.agentid)],limit=1)
    #     return result.EncodingAESKey

    @staticmethod
    def __response(res):
        errcode = res.get("errcode")
        # errmsg = res.get("errmsg")
        if errcode is ErrorCode.SUCCESS:
            return True, res
        else:
            return False, res

    def __post(self, url, data):
        _logger.debug(u"the url is：%s" % url)
        res = requests.post(url, data=json.dumps(data).decode('unicode-escape').encode("utf-8")).json()
        return self.__response(res)

    def __get(self, url):
        _logger.debug(u"the url is：%s" % url)
        res = requests.get(url).json()
        return self.__response(res)

    def __post_file(self, url, media_file):
        res = requests.post(url, file=media_file).json()
        return self.__response(res)

    # 部门管理
    def create_department(self, name, parentid=1,department_id=None):
        """
            创建部门
            name    : 部门名称。长度限制为1~64个字符
            parentid: 父亲部门id。根部门id为1
            order   : 在父部门中的次序。从1开始，数字越大排序越靠后
        """
        url = "%s/department/create?access_token=%s" % (self.url_prefix, self.access_token)
        data = {
            "name": name,
            "parentid": parentid,
        }
        if department_id is not None:
            data["id"] = int(department_id)
        status, res = self.__post(url, data)
        return status, res

    def update_department(self, department_id, name=None, parentid=None, **kwargs):
        """
            更新部门
            参数	必须	说明
            access_token	是	调用接口凭证
            id	是	部门id
            name	否	更新的部门名称。长度限制为1~64个字符。修改部门名称时指定该参数
            parentid	否	父亲部门id。根部门id为1
            order	否	在父部门中的次序。从1开始，数字越大排序越靠后
        """
        url = "%s/department/update?access_token=%s" % (self.url_prefix, self.access_token)
        data = {
            "id": department_id,
        }
        if name is not None:
            data["name"] = name
        if parentid is not None:
            data["parentid"] = parentid
        data.update(kwargs)
        status, res = self.__post(url, data)
        return status, res

    def delete_department(self, department_id):
        """
            删除部门
            参数	必须	说明
            access_token	是	调用接口凭证
            id	是	部门id。（注：不能删除根部门；不能删除含有子部门、成员的部门）
        """
        url = "%s/department/delete?access_token=%s&id=%s" % (self.url_prefix, self.access_token, department_id)
        status, res = self.__get(url)
        return status, res

    def get_department_list(self):
        """
            获取部门列表
            参数	必须	说明
            access_token	是	调用接口凭证
        """
        url = "%s/department/list?access_token=%s" % (self.url_prefix, self.access_token)
        status, res = self.__get(url)
        return status, res

    # 成员管理
    def create_user(self, data):
        """
            创建用户
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID。对应管理端的帐号，企业内必须唯一。长度为1~64个字符
            name	是	成员名称。长度为1~64个字符
            department	是	成员所属部门id列表。注意，每个部门的直属员工上限为1000个
            position	否	职位信息。长度为0~64个字符
            mobile	否	手机号码。企业内必须唯一，mobile/weixinid/email三者不能同时为空
            email	否	邮箱。长度为0~64个字符。企业内必须唯一
            weixinid	否	微信号。企业内必须唯一。（注意：是微信号，不是微信的名字）
            extattr	否	扩展属性。扩展属性需要在WEB管理端创建后才生效，否则忽略未知属性的赋值
        """
        url = "%s/user/create?access_token=%s" % (self.url_prefix, self.access_token)
        if data.get("userid") and data.get("name"):
            status, res = self.__post(url, data)
        else:
            status = False
            res = u"userid 或者 name 为空"
        return status, res

    def update_user(self, data):
        """
            更新成员
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID。对应管理端的帐号，企业内必须唯一。长度为1~64个字符
            name	否	成员名称。长度为0~64个字符
            department	否	成员所属部门id列表。注意，每个部门的直属员工上限为1000个
            position	否	职位信息。长度为0~64个字符
            mobile	否	手机号码。企业内必须唯一，mobile/weixinid/email三者不能同时为空
            email	否	邮箱。长度为0~64个字符。企业内必须唯一
            weixinid	否	微信号。企业内必须唯一。（注意：是微信号，不是微信的名字）
            enable	否	启用/禁用成员。1表示启用成员，0表示禁用成员
            extattr	否	扩展属性。扩展属性需要在WEB管理端创建后才生效，否则忽略未知属性的赋值
        """
        url = "%s/user/update?access_token=%s" % (self.url_prefix, self.access_token)
        if data.get("userid") and data.get("name"):
            status, res = self.__post(url, data)
        else:
            status = False
            res = u"userid 或者 name 为空"
        return status, res

    def delete_user(self, userid):
        """
            删除成员
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID。对应管理端的帐号
        """
        url = "%s/user/delete?access_token=%s&userid=%s" % (self.url_prefix, self.access_token, userid)
        status, res = self.__get(url)
        return status, res

    def multi_delete_user(self, useridlist):
        """
            批量删除成员
            参数	必须	说明
            access_token	是	调用接口凭证
            useridlist	是	员工UserID列表。对应管理端的帐号
        """
        url = "%s/user/batchdelete?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"useridlist": useridlist}
        status, res = self.__post(url, data=data)
        return status, res

    def get_user(self, userid):
        """
            获取成员
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID。对应管理端的帐号
        """
        url = "%s/user/get?access_token=%s&userid=%s" % (self.url_prefix, self.access_token, userid)
        status, res = self.__get(url)
        return status, res

    def get_users_in_department(self, department_id, fetch_child=0, status=0):
        """
            获取部门成员
            参数	必须	说明
            access_token	是	调用接口凭证
            department_id	是	获取的部门id
            fetch_child	否	1/0：是否递归获取子部门下面的成员
            status	否	0获取全部员工，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加
        """
        url = "%s/user/simplelist?access_token=%s&department_id=%s&fetch_child=%s&status=%s" \
              % (self.url_prefix, self.access_token, department_id, fetch_child, status)
        status, res = self.__get(url)
        return status, res

    def get_users_in_department_detail(self, department_id, fetch_child=0, status=0):
        """
            获取部门成员(详情)
            参数	必须	说明
            access_token	是	调用接口凭证
            department_id	是	获取的部门id
            fetch_child	否	1/0：是否递归获取子部门下面的成员
            status	否	0获取全部员工，1获取已关注成员列表，2获取禁用成员列表，4获取未关注成员列表。status可叠加
        """
        url = "%s/user/list?access_token=%s&department_id=%s&fetch_child=%s&status=%s" \
              % (self.url_prefix, self.access_token, department_id, fetch_child, status)
        status, res = self.__get(url)
        return status, res

    def invite_attention_to_user(self, userid, invite_tips=None):
        """
            邀请用户关注
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	用户的userid
            invite_tips	否	推送到微信上的提示语（只有认证号可以使用）。当使用微信推送时，该字段默认为“请关注XXX企业号”，邮件邀请时，该字段无效。
        """
        url = "%s/invite/send?access_token=%s" % (self.url_prefix, self.access_token)
        data = {
            "userid": userid
        }
        if invite_tips is not None:
            data["invite_tips"] = invite_tips
        status, res = self.__post(url, data)
        return status, res

    # 管理标签
    def create_tag(self, tagname,tagid=None):
        """
            创建标签
            参数	必须	说明
            access_token	是	调用接口凭证
            tagname	是	标签名称。长度为1~64个字符，标签不可与其他同组的标签重名，也不可与全局标签重名
        """
        url = "%s/tag/create?access_token=%s" % (self.url_prefix, self.access_token)
        data = {}
        data['tagname'] = tagname
        if tagid:
            data['tagid'] = tagid
        status, res = self.__post(url, data)
        return status, res

    def update_tag(self, tagid, tagname):
        """
            更新标签名字
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
            tagname	是	标签名称。长度为1~64个字符，标签不可与其他同组的标签重名，也不可与全局标签重名
        """
        url = "%s/tag/update?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"tagid": tagid, "tagname": tagname}
        status, res = self.__post(url, data)
        return status, res

    def delete_tag(self, tagid):
        """
            删除标签
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
        """
        url = "%s/tag/delete?access_token=%s&tagid=%s" % (self.url_prefix, self.access_token, tagid)
        status, res = self.__get(url)
        return status, res

    def get_user_from_tag(self, tagid):
        """
            获取标签成员
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
        """
        url = "%s/tag/get?access_token=%s&tagid=%s" % (self.url_prefix, self.access_token, tagid)
        status, res = self.__get(url)
        return status, res

    def add_users_to_tag(self, data):
        """
            增加标签成员
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
            userlist	否	企业员工ID列表，注意：userlist、partylist不能同时为空
            partylist	否	企业部门ID列表，注意：userlist、partylist不能同时为空
        """
        url = "%s/tag/addtagusers?access_token=%s" % (self.url_prefix, self.access_token)
        status, res = self.__post(url, data=data)
        return status, res

    def delete_user_in_tag(self, tagid, userlist, partylist):
        """
            删除标签成员
            参数	必须	说明
            access_token	是	调用接口凭证
            tagid	是	标签ID
            userlist	否	企业员工ID列表，注意：userlist、partylist不能同时为空
            partylist	否	企业部门ID列表，注意：userlist、partylist不能同时为空
        """
        url = "%s/tag/deltagusers?access_token=%s" % (self.url_prefix, self.access_token)
        data = {"tagid": tagid, "userlist": userlist, "partylist": partylist}
        status, res = self.__post(url, data=data)
        return status, res

    def get_tag_list(self):
        """
            获取标签列表
            参数	必须	说明
            access_token	是	调用接口凭证
        """
        url = "%s/tag/list?access_token=%s" % (self.url_prefix, self.access_token)
        status, res = self.__get(url)
        return status, res

    # 管理多媒体文件
    def upload_media(self, media_type, media_file):
        """
            上传媒体文件
            参数	必须	说明
            access_token	是	调用接口凭证
            type	是	媒体文件类型，分别有图片（image）、语音（voice）、视频（video），普通文件(file)
            media	是	form-data中媒体文件标识，有filename、filelength、content-type等信息
        """
        url = "%s/media/upload?access_token=%s&type=%s" % (self.url_prefix, self.access_token, media_type)
        data = {"media": media_file}
        status, res = self.__post_file(url, data)
        return status, res

    def get_media(self, media_id):
        """
            获取媒体文件
            参数	必须	说明
            access_token	是	调用接口凭证
            media_id	是	媒体文件id
        """
        url = "%s/media/get?access_token=%s&media_id=%s" % (self.url_prefix, self.access_token, media_id)
        media_file = requests.get(url)
        return media_file

    # 发送消息
    def send_msg_to_user(self, datas):
        """
            发送消息到用户
            text消息
                参数	必须	说明
                touser	否	员工ID列表（消息接收者，多个接收者用‘|’分隔）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送
                toparty	否	部门ID列表，多个接收者用‘|’分隔。当touser为@all时忽略本参数
                totag	否	标签ID列表，多个接收者用‘|’分隔。当touser为@all时忽略本参数
                msgtype	是	消息类型，此时固定为：text
                agentid	是	企业应用的id，整型。可在应用的设置页面查看
                content	是	消息内容
                safe	否	表示是否是保密消息，0表示否，1表示是，默认0
                其他消息参考： http://qydev.weixin.qq.com/wiki/index.php?
                    title=%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F
        """
        url = "%s/message/send?access_token=%s" % (self.url_prefix, self.access_token)

        data = {
            "msgtype": datas.get('msgtype'),
            "agentid": datas.get('agentid')
        }
        if datas.get('msgtype') != "news":
            data["safe"] = datas.get('safe')
        if datas.get('msgtype') == "text":
            data["text"] = {"content": datas.get('content')}
        if datas.get('msgtype') == "image":
            data["image"] = {"media_id": datas.get("media_id")}
        if datas.get('msgtype') == "voice":
            data["voice"] = {"media_id": datas.get("media_id")}
        if datas.get('msgtype') == "video":
            data["video"] = {
                "media_id": datas.get("media_id"),
                "title": datas.get("title"),
                "description": datas.get("description")
            }
        if datas.get('msgtype') == "file":
            data["file"] = {
                "media_id": datas.get("media_id")
            }
        if datas.get('msgtype') == "news":
              data["news"] = {
                  "articles": [
                      {
                          "title": datas.get("title"),
                          "description": datas.get("description"),
                          "url": datas.get("url"),
                          "picurl": datas.get("picurl")
                      }
                  ]
              }
        # if datas.get['msgtype'] == "mpnews":
            #{
            #   "articles":[
            #       {
            #           "title": "Title",
            #           "thumb_media_id": "id",
            #           "author": "Author",
            #           "content_source_url": "URL",
            #           "content": "Content",
            #           "digest": "Digest description",
            #           "show_cover_pic": "0"
            #       },
            #       {
            #           "title": "Title",
            #           "thumb_media_id": "id",
            #           "author": "Author",
            #          "content_source_url": "URL",
            #           "content": "Content",
            #           "digest": "Digest description",
            #           "show_cover_pic": "0"
            #       }
            #   ]
            #}
            # data["mpnews"] = kwargs

        if datas.get("touser") is None:
            to_user = "@all"
        else:
            # to_user = '|'.join(touser)
            to_user = datas.get("touser")
        data["touser"] = to_user
        if datas.get("toparty") is not None:
            data["toparty"] = datas.get("toparty")

        if datas.get("totag") is not None:
            data["totag"] = datas.get("totag")
        status, res = self.__post(url, data)
        return status, res

    # 二次验证
    def second_validation(self, userid):
        """
            二次验证
            参数	必须	说明
            access_token	是	调用接口凭证
            userid	是	员工UserID
        """
        url = "https://qyapi.weixin.qq.com/cgi-bin/user/authsucc?access_token=%s&userid=%s" \
              % (self.access_token, userid)
        status, res = self.__get(url)
        return status, res

    # 以下是自己添加的部分功能

    # 将userid转化为openid
    def convert_to_openid(self,userid):
        url ="https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_openid?access_token=%s"% self.access_token
        data = {}
        data['userid'] = userid
        content = self.__post(url, data)
        if content:
            return content[1]['openid']

    # 根据code取得用户的企业通讯录账号
    def get_enterprise_account_by_code(self, code):
        """
            根据code取得用户的企业通讯录账号
            参数	必须	说明
            code	是	调用接口凭证
        """
        url = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token=%s&code=%s" \
              % (self.access_token, code)
        # print u'根据code取得用户的企业通讯录UserId的ＵＲＬ：%s' % url
        content = self.__get(url)
        if content[1].get('errcode'):
            return "0"
        else:
            return content[1]['UserId']

    # 根据要验证的url生成微信验证的url
    def get_authorize_url(self, redircet_uri,state='toproerp'):
        """
            根据要验证的url生成微信验证的url
            参数	必须	说明
            redircet_uri	是	验证的url
        """
        parts = {'redirect_uri':redircet_uri}
        timestamp = time.time()

        url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&%s&response_type=code&scope=snsapi_base&state=%s#wechat_redirect" \
              % (self.corpid, urllib.urlencode(parts),state)
        # print u"获取code的链接:%s"%url
        return url

    # 获取微信企业号上的app列表
    def get_app_lists(self):
        """
            获取app列表
            参数	必须	说明
            access_token	是	调用接口凭证
        """
        url = "%s/agent/list?access_token=%s"%(self.url_prefix, self.access_token)
        status, res = self.__get(url)
        return status, res

    # 配置微信企业号上的app
    def create_app(self,data):
        """
            配置app
            参数	必须	说明
            access_token	是	调用接口凭证
            agentid 是  企业应用的id
            report_location_flag  是  企业应用是否打开地理位置上报 0：不上报；1：进入会话上报；2：持续上报
            logo_mediaid  否   企业应用头像的mediaid，通过多媒体接口上传图片获得mediaid，上传后会自动裁剪成方形和圆形两个头像
            name  是   企业应用名称
            description  否  企业应用详情
            redirect_domain  是  企业应用可信域名
            isreportuser  否  是否接收用户变更通知。0：不接收；1：接收。主页型应用无需该参数
            isreportenter  否  是否上报用户进入应用事件。0：不接收；1：接收。主页型应用无需该参数
            home_url  否   主页型应用url。url必须以http或者https开头。消息型应用无需该参数
        """

        url = "%s/agent/set?access_token=%s"(self.url_prefix, self.access_token)
        if data.get("agentid") and data.get("name") and data.get("redirect_domain")\
            and data.get("report_location_flag"):
            status, res = self.__post(url, data)
        else:
            status = False
            res = u"参数不完整"
        return status, res

    # 获取企业号app的详细资料
    def get_app_details(self,agentid):
        """
            获取app详细资料
            参数	必须	说明
            access_token	是	调用接口凭证
            agentid  是  授权方应用id
        """
        url = "%s/agent/get?access_token=%s&agentid=%s"%(self.url_prefix, self.access_token,agentid)
        status, res = self.__get(url)
        return status, res


    # 删除应用菜单
    def delete_app_menu(self):
        """
            删除应用菜单
            参数	必须	说明
            access_token	是	调用接口凭证
            agentid  是  授权方应用id
        """
        url = "%s/menu/delete?access_token=%s&agentid=%s"%(self.url_prefix, self.access_token, self.agentid)
        status, res = self.__get(url)
        return status, res

    #   更新菜单至应用
    def update_app_menu(self, data):
        """
            更新菜单至应用
            参数	必须	说明
            access_token	是	调用接口凭证
            agentid  是  授权方应用id
        """
        url = "%s/menu/create?access_token=%s&agentid=%s"%(self.url_prefix, self.access_token,self.agentid)
        status, res = self.__post(url, data)
        return status, res


    def check_signature(self, sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce,sVerifyEchoStr):
        """
        验证微信消息真实性
        :param signature: 微信加密签名
        :param timestamp: 时间戳
        :param nonce: 随机数
        :return: 通过验证返回 True, 未通过验证返回 False
        """
        # self._check_token()
        # print msg_signature
        # if not msg_signature or not timestamp or not nonce:
        #     return False
        #
        # tmp_list = [self.access_token, timestamp, nonce]
        # tmp_list.sort()
        # tmp_str = ''.join(tmp_list)
        # print hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
        # if msg_signature == hashlib.sha1(tmp_str.encode('utf-8')).hexdigest():
        #     print 222
        #     return True
        # else:
        #     return False
        wxcpt=WXBizMsgCrypt.WXBizMsgCrypt(self.Token,self.EncodingAESKey,self.corpid)
        return wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)

    def _check_token(self):
        """
        检查 Token 是否存在
        :raises NeedParamError: Token 参数没有在初始化的时候提供
        """
        if not self.access_token:
            raise NeedParamError('Please provide Token parameter in the construction of class.')

    def parse_data(self, data):
        """
        解析微信服务器发送过来的数据并保存类中
        :param data: HTTP Request 的 Body 数据
        :raises ParseError: 解析微信服务器数据错误, 数据不合法
        """
        result = {}
        if type(data) == unicode:
            data = data.encode('utf-8')
        elif type(data) == str:
            pass
        else:
            raise ParseError()

        try:
            xml = XMLStore(xmlstring=data)
        except Exception:
            raise ParseError()

        result = xml.xml2dict
        result['raw'] = data
        result['type'] = result.pop('MsgType').lower()

        message_type = MESSAGE_TYPES.get(result['type'], UnknownMessage)
        self.__message = message_type(result)
        self.__is_parse = True

class NeedParamError(Exception):
    """
    构造参数提供不全异常
    """
    pass

class ParseError(Exception):
    """
    解析微信服务器数据异常
    """
    pass

class XMLStore(object):
    """
    XML 存储类，可方便转换为 Dict
    """
    def __init__(self, xmlstring):
        self._raw = xmlstring
        self._doc = minidom.parseString(xmlstring)

    @property
    def xml2dict(self):
        """
        将 XML 转换为 dict
        """
        self._remove_whitespace_nodes(self._doc.childNodes[0])
        return self._element2dict(self._doc.childNodes[0])

    def _element2dict(self, parent):
        """
        将单个节点转换为 dict
        """
        d = {}
        for node in parent.childNodes:
            if not isinstance(node, minidom.Element):
                continue
            if not node.hasChildNodes():
                continue

            if node.childNodes[0].nodeType == minidom.Node.ELEMENT_NODE:
                try:
                    d[node.tagName]
                except KeyError:
                    d[node.tagName] = []
                d[node.tagName].append(self._element2dict(node))
            elif len(node.childNodes) == 1 and node.childNodes[0].nodeType in [minidom.Node.CDATA_SECTION_NODE, minidom.Node.TEXT_NODE]:
                d[node.tagName] = node.childNodes[0].data
        return d

    def _remove_whitespace_nodes(self, node, unlink=True):
        """
        删除空白无用节点
        """
        remove_list = []
        for child in node.childNodes:
            if child.nodeType == Node.TEXT_NODE and not child.data.strip():
                remove_list.append(child)
            elif child.hasChildNodes():
                self._remove_whitespace_nodes(child, unlink)
        for node in remove_list:
            node.parentNode.removeChild(node)
            if unlink:
                node.unlink()

    def get_message(self):
        """
        获取解析好的 WechatMessage 对象
        :return: 解析好的 WechatMessage 对象
        """
        self._check_parse()

        return self.__message

    def _check_parse(self):
        """
        检查是否成功解析微信服务器传来的数据
        :raises NeedParseError: 需要解析微信服务器传来的数据
        """
        if not self.__is_parse:
            raise NeedParseError()

    def get_message(self):
        """
        获取解析好的 WechatMessage 对象
        :return: 解析好的 WechatMessage 对象
        """
        self._check_parse()

        return self.__message