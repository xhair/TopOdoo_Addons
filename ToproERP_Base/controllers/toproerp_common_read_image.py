# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import time
import json
import hashlib
import functools
import requests
from json import *
from openerp import api, http, fields, models
import openerp
from openerp.http import request
from cStringIO import StringIO

from wechat_sdk import WechatBasic
from wechat_sdk.messages import (
    TextMessage, VoiceMessage, ImageMessage, VideoMessage, ShortVideoMessage, LinkMessage, LocationMessage, EventMessage
)

from werkzeug.exceptions import abort

import logging
from openerp.modules import get_module_resource

_logger = logging.getLogger(__name__)


class ToproerpCommonReadImage(http.Controller):
    '''
    用于接收微信发过来的任何消息，并转发给相应的业务类进行处理
    '''

    __check_str = 'NDOEHNDSY#$_@$JFDK:Q{!'

    # 从数据库读取图片
    @http.route('/wechat/ToproerpCommonReadImage/base_image', type='http', auth="none", cors="*")
    def base_image(self, model_name, file_name, column_name, id):
        '''
        :param model_name: 业务对象(_name)
        :param file_name: 文件路径（模块名/static/src/img）
        :param column_name: 属性为图片的值
        :param id: 图片存在的对象记录Id
        :return:
        '''
        customer_card = http.request.env[model_name].sudo().search(
            [('id', '=', id)])
        column = column_name
        imgname = 'toproerp.png'
        # str=file_name.split('/')
        # placeholder = functools.partial(get_module_resource,str[0],str[1],str[2],str[3])
        placeholder = functools.partial(get_module_resource, file_name)
        if id:
            image_data = StringIO(str(column).decode('base64'))
            response = http.send_file(image_data, filename=imgname, mtime=fields.Date.today())
        else:
            response = http.send_file(placeholder('base.png'))
        return response
