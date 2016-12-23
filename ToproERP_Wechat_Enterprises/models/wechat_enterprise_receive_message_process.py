# -*- coding: utf-8 -*-
__author__ = 'suntao'
from openerp import api,models,fields,_
from wechat_sdk import WechatBasic
import logging

_logger = logging.getLogger(__name__)

class WechatEnterpriseReceiveMessageProcess(models.Model):
    _name = 'wechat.enterprise.receive.message.process'
    _description = 'Wechat Enterprise Process Receive Process Message'

    name = fields.Char(u'名称',help=u'取个好名称方便管理，比如优惠信息索取',required=True)
    message_type = fields.Selection([('text',u'文本'),
                                     ('voice',u'语音'),
                                     ('image',u'图片'),
                                     ('video',u'视频'),
                                     ('shortvideo',u'短视频'),
                                     ('location',u'位置'),
                                     ('link',u'链接'),
                                     ('subscribe',u'关注'),
                                     ('unsubscribe',u'取消关注'),
                                     ('view',u'自定义菜单链接跳转'),
                                     ('click',u'自定义菜单点击'),
                                     ('scan',u'扫描二维码'),
                                     ('scancode_waitmsg',u'扫描二维码并等待'),
                                     ('unsubscribe',u'取消关注')],
                                    string=u'消息类型',required=True)
    message_key = fields.Char(u'关键字',required=True)
    class_name = fields.Char(u'负责处理的类',help='此处填写进行处理的类的名称），例如:topro_service_base.test',required=True,default="类的名称")
    method_name = fields.Char(u'负责处理的方法',help='此处填写进入处理的方法名,方法必须包括参数是message和account_id(微信公众号的id),这是一个dict',required=True,default="方法名")
    agentID = fields.Many2one('wechat.enterprise.app',u'企业应用',required=True)
    note = fields.Text(u'备注')

    def get_message_process(self, message_type, key_word=False, agentID=False):
        '''
        取得消息处理的设置
        :param message_type:
        :param key_word:
        :param agentID:
        :return:
        '''
        if message_type:
            process = self.sudo().search([('message_type', '=', message_type),('message_key', '=', key_word),('agentID', '=', agentID)], limit=1)
        if not process and message_type and key_word != None:
            process = self.sudo().search([('message_type', '=', message_type),('message_key', '=', key_word)],limit=1)
        if not process and message_type:
            process = self.sudo().search([('message_type', '=', message_type)],limit=1)
        return process

    def exec_by_message_type(self,type,message_key,agentID):
        '''
        根据消息的类型动态调用类进行执行
        :param type:
        :param message:
        :param account_id:
        :return:
        '''

        #取得对象，
        if type and message_key:
            process = self.get_message_process(type, message_key, agentID)
            process.sudo().exec_class_mothed(message_key, agentID)

    def exec_class_mothed(self,FromUserName,agentID,media_id=None):
        '''
        执行类的方法
        :param class_name:
        :param method_name:
        :param message:
        :return:
        '''

        _logger.debug('exec_class_mothed')
        objFunc = getattr(self.env[self.class_name],self.method_name )
        ret = objFunc(FromUserName,agentID,media_id=None)

        return ret


    def hello(self,FromUserName,agentID,media_id=None):
        '''
        demo方法，模拟动态处理客户的需求
        :param message:
        :return:
        '''

        try:
            self.env['wechat.enterprise.send.message'].send_news_message(FromUserName,agentID,u'测试图文信息',u'测试图文信息的描述',
                                                          'http://www.baidu.com','http://www.kia-hnsyt.com.cn/uploads/allimg/141204/1-1412041624240-L.jpg')
        except Exception,e:
            _logger.warning(u'发送微信文本失败原因:%s',e.message)
            raise Warning(e.message)


    def send_img(self,FromUserName,agentID,media_id=None):
        '''
        demo方法，模拟动态处理客户的需求
        :param message:
        :return:
        '''

        try:
            self.env['wechat.enterprise.send.message'].send_text_message(FromUserName,agentID,u'即将为您发送一条消息')
        except Exception,e:
            _logger.warning(u'发送微信文本失败原因:%s',e.message)
            raise Warning(e.message)

