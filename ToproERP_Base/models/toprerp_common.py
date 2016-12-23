# coding=utf-8
import re

import pytz, datetime
import logging
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

__author__ = 'Administrator'

from odoo import fields, models, exceptions

_logger = logging.getLogger(__name__)


class ToproerpCommon(models.Model):
    _name = 'toproerp.common'
    _description = u'公用基础类'

    def get_login_user(self):
        '''
        根据用户id获取员工id
        :return:
        '''
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
        if employee:
            if len(employee) > 0:
                if not employee.department_id:
                    raise exceptions.Warning(u'您当前使用的用户没有所属部门')
                return employee
            else:
                return False
        else:
            raise exceptions.Warning(u'您当前使用的用户没有关联员工')

    def get_user_by_employee(self, employee_id):
        '''
        根据员工id获取用户
        :param employee_id:
        :return:
        '''
        users = self.env['res.users'].search([('id', '=', employee_id)])
        if users:
            return users[0]['id']
        else:
            return False

    def get_user_by_partner_id(self, partner_id):
        '''
        根据客户id获取员工
        :return:
        '''
        users = self.env['res.users'].sudo().search([('partner_id', '=', int(partner_id))])
        if users:
            return users
        else:
            return False

    def get_zero_time(self):
        '''
        获取当前0时区时间
        :return:
        '''
        now_time = datetime.datetime.today()
        tz = self.env.user.tz or 'Asia/Shanghai'
        tz_timedelta = now_time.replace(tzinfo=pytz.timezone('UTC')) - now_time.replace(tzinfo=pytz.timezone(tz))
        zero_time = now_time - tz_timedelta
        zero_time = zero_time.replace(tzinfo=pytz.timezone('UTC'))
        return zero_time

    def get_location_time(self):
        '''
        获取当前时区时间(带时区)
        :return:
        '''
        now_time = datetime.datetime.utcnow()
        tz = self.env.user.tz or 'Asia/Shanghai'
        return now_time.replace(tzinfo=pytz.timezone(tz))

    def strToDate(self, dt):
        '''
        将字符串转成日期
        :param dt:
        :return:
        '''
        return datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))


        return now.strftime(tformat)


    def render_tag_usertime(self,create_date,time_format):
        '''
        用来在qweb中显示自定义的时间，并做好时区的处理
        :param time_str:
        :param time_format:
        :return:
        '''
        tformat = time_format
        if not tformat:
            # No format, use default time and date formats from qwebcontext
            lang = (
                self.env.lang or
                self.env.context['lang'] or
                self.env.user.lang
            )
            if lang:
                lang = self.env['res.lang'].search(
                    [('code', '=', lang)]
                )
                tformat = "{0.date_format} {0.time_format}".format(lang)
            else:
                tformat = DEFAULT_SERVER_DATETIME_FORMAT

        now = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")

        tz_name = self.env.user.tz
        if tz_name:
            try:
                utc = pytz.timezone('UTC')
                context_tz = pytz.timezone(tz_name)
                utc_timestamp = utc.localize(now, is_dst=False)  # UTC = no DST
                now = utc_timestamp.astimezone(context_tz)
            except Exception:
                _logger.debug(
                    "failed to compute context/client-specific timestamp, "
                    "using the UTC value",
                    exc_info=True)
        return now.strftime(tformat)

    def strToDateTime(self, dt):
        '''
        将字符串转成日期时间
        :param dt:
        :return:
        '''
        return datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]), int(dt[11:13]), int(dt[14:16]), int(dt[17:19]))

    def get_base_url(self):
        '''
        取得当前系统的url
        使用这个方法前，去系统的系统参数里增加一个system.base.url的参数，放入要访问的地址
        :return:
        '''
        conf = self.env['ir.config_parameter']
        return conf.get_param('system.base.url') or conf.get_param('web.base.url') or None

    import re

    def encode_utf8_to_iso88591(self, utf8_text):
        """
        将字符串从utf8转换为iso88591
        Encode and return the given UTF-8 text as ISO-8859-1 (latin1) with
        unsupported characters replaced by '?', except for common special
        characters like smart quotes and symbols that we handle as well as we
        can.
        For example, the copyright symbol => '(c)' etc.

        If the given value is not a string it is returned unchanged.

        References:

        en.wikipedia.org/wiki/Quotation_mark_glyphs#Quotation_marks_in_Unicode
        en.wikipedia.org/wiki/Copyright_symbol
        en.wikipedia.org/wiki/Registered_trademark_symbol
        en.wikipedia.org/wiki/Sound_recording_copyright_symbol
        en.wikipedia.org/wiki/Service_mark_symbol
        en.wikipedia.org/wiki/Trademark_symbol
        """
        if not isinstance(utf8_text, basestring):
            return utf8_text
        # Replace "smart" and other single-quote like things
        utf8_text = re.sub(
            u'[\u02bc\u2018\u2019\u201a\u201b\u2039\u203a\u300c\u300d]',
            "'", utf8_text)
        # Replace "smart" and other double-quote like things
        utf8_text = re.sub(
            u'[\u00ab\u00bb\u201c\u201d\u201e\u201f\u300e\u300f]',
            '"', utf8_text)
        # Replace copyright symbol
        utf8_text = re.sub(u'[\u00a9\u24b8\u24d2]', '(c)', utf8_text)
        # Replace registered trademark symbol
        utf8_text = re.sub(u'[\u00ae\u24c7]', '(r)', utf8_text)
        # Replace sound recording copyright symbol
        utf8_text = re.sub(u'[\u2117\u24c5\u24df]', '(p)', utf8_text)
        # Replace service mark symbol
        utf8_text = re.sub(u'[\u2120]', '(sm)', utf8_text)
        # Replace trademark symbol
        utf8_text = re.sub(u'[\u2122]', '(tm)', utf8_text)
        # Replace/clobber any remaining UTF-8 characters that aren't in ISO-8859-1
        return utf8_text.encode('ISO-8859-1', 'replace')
