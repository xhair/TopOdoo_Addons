# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, exceptions
import re


class ToproerpPartner(models.Model):
    _inherit = "res.partner"
    _description = u'客户'

    @api.constrains('card')
    def _card_info(self, card=None):
        '''
        当身份证改变时，获取生日、年龄、性别
        Errors=['验证通过!','身份证号码位数不对!','身份证号码出生日期超出范围或含有非法字符!','身份证号码校验错误!','身份证地区非法!']
        :return:
        '''
        if (self.card) or (card):
            Errors = [u'验证通过!', u'身份证号码位数不对!', u'身份证号码出生日期超出范围或含有非法字符!', u'身份证号码校验错误!', u'身份证地区非法!']
            area = {"11": u"北京", "12": u"天津", "13": u"河北", "14": u"山西", "15": u"内蒙古", "21": u"辽宁", "22": u"吉林",
                    "23": u"黑龙江",
                    "31": u"上海", "32": u"江苏", "33": u"浙江", "34": u"安徽", "35": u"福建", "36": u"江西", "37": u"山东",
                    "41": u"河南",
                    "42": u"湖北", "43": u"湖南", "44": u"广东", "45": u"广西", "46": u"海南", "50": u"重庆", "51": u"四川",
                    "52": u"贵州",
                    "53": u"云南", "54": u"西藏", "61": u"陕西", "62": u"甘肃", "63": u"青海", "64": u"宁夏", "65": u"新疆",
                    "71": u"台湾",
                    "81": u"香港", "82": u"澳门", "91": u"国外"}

            if self.card:
                idcard = str(self.card)
            if card:
                idcard = str(card)
            idcard = idcard.strip()
            idcard_list = list(idcard)
            if (idcard[0:1].isdigit() == False or idcard[1:2].isdigit() == False or idcard[2:3].isdigit() == False
                or idcard[3:4].isdigit() == False or idcard[4:5].isdigit() == False or idcard[5:6].isdigit() == False
                or idcard[6:7].isdigit() == False or idcard[7:8].isdigit() == False or idcard[8:9].isdigit() == False
                or idcard[9:10].isdigit() == False or idcard[10:11].isdigit() == False or idcard[
                                                                                          11:12].isdigit() == False
                or idcard[12:13].isdigit() == False or idcard[13:14].isdigit() == False or idcard[
                                                                                           14:15].isdigit() == False
                or idcard[15:16].isdigit() == False or idcard[16:17].isdigit() == False):
                if self.card:
                    raise exceptions.Warning(u'身份证地区非法')
                if card:
                    return u'身份证地区非法'
            # 地区校验
            if (not area[(idcard)[0:2]]):
                # print Errors[4]
                if self.card:
                    raise exceptions.Warning(u'身份证地区非法')
                if card:
                    return u'身份证地区非法'
            # 15位身份号码检测
            # if (len(idcard) == 15):
            #     if ((int(idcard[6:8]) + 1900) % 4 == 0 or (
            #                         (int(idcard[6:8]) + 1900) % 100 == 0 and (int(idcard[6:8]) + 1900) % 4 == 0)):
            #         erg = re.compile(
            #             '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')  # //测试出生日期的合法性
            #     else:
            #         ereg = re.compile(
            #             '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # //测试出生日期的合法性
            #     if (re.match(ereg, idcard)):
            #         self._birthday(idcard)
            #     else:
            #         # print Errors[2]
            #         raise exceptions.Warning(u'身份证号码出生日期超出范围或含有非法字符')
            # 18位身份号码检测
            if (len(idcard) == 18):
                # 出生日期的合法性检查
                # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
                # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
                if (int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10]) % 4 == 0)):
                    ereg = re.compile(
                        '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')  # //闰年出生日期的合法性正则表达式
                else:
                    ereg = re.compile(
                        '[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')  # //平年出生日期的合法性正则表达式
                # //测试出生日期的合法性
                if (re.match(ereg, idcard)):
                    # //计算校验位
                    S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(
                        idcard_list[11])) * 9 + (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(
                        idcard_list[3]) + int(idcard_list[13])) * 5 + (int(idcard_list[4]) + int(
                        idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 + (int(
                        idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(
                        idcard_list[8]) * 6 + int(idcard_list[9]) * 3
                    Y = S % 11
                    M = "F"
                    JYM = "10X98765432"
                    M = JYM[Y]  # 判断校验位
                    if (M == idcard_list[17]):  # 检测ID的校验位
                        if self.card:
                            self._birthday(idcard)
                    else:
                        if self.card:
                            raise exceptions.Warning(u'身份证号码校验错误')
                        if card:
                            return u'身份证号码校验错误'
                else:
                    if self.card:
                        raise exceptions.Warning(u'身份证号码出生日期超出范围或含有非法字符')
                    if card:
                        return u'身份证号码出生日期超出范围或含有非法字符'
            else:
                # print Errors[1]
                if self.card:
                    raise exceptions.Warning(u'身份证号码位数不对')
                if card:
                    return u'身份证号码位数不对'

    def _birthday(self, card):
        '''
        计算生日年月日、年龄、性别的方法
        :param card:
        :return:
        '''
        # 生日
        year = card[6:14]
        self.birthday = year
        # 性别
        sex = card[14:17]
        if int(sex) % 2 == 0:
            self.sex = u'女'
        else:
            self.sex = u'男'
        # 年龄
        # %y 两位数的年份表示（00-99）%Y 四位数的年份表示（000-9999）%m 月份（01-12）%d 月内中的一天（0-31）
        now_time = fields.Date.today()[0:4]
        self.age = (int(now_time) - int(card[6:10]))

    @api.constrains('mobile')
    def phonecheck(self):
        # 号码前缀，如果运营商启用新的号段，只需要在此列表将新的号段加上即可。
        phoneprefix = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                       '147',
                       '150', '151', '152', '153', '154', '155', '156', '157', '158', '159',
                       '170', '175', '176', '177', '178',
                       '180', '181', '182', '183', '185', '186', '187', '188', '189']
        # print len(s)
        # 检测号码是否长度是否合法。
        # print self.phone
        if self.mobile:
            if len(self.mobile.strip()) > 4:
                if len(self.mobile.strip()) <> 11:
                    print u'客户失败的手机号是 %s' % self.mobile
                    raise Warning(u'客户手机号必须是11位数字')
                else:
                    # 检测输入的号码是否全部是数字。
                    if self.mobile.isdigit():
                        # 检测前缀是否是正确。
                        if self.mobile[:3] in phoneprefix:
                            # print "电话号码是有效的."
                            pass
                        else:
                            # print "无效的手机号码."
                            raise Warning(u'无效的手机号码')
                    else:
                        # print "手机号必须是数字"
                        raise Warning(u'手机号必须是数字')

    @api.multi
    @api.depends('if_group_cusotmer_contact_views', 'name')
    def _get_if_group_cusotmer_contact_views(self):
        for par in self:
            jurisdiction_obj = self.env["res.groups"].search([('name', '=', u'客户联络信息查看')])
            par._cr.execute(
                "select uid from res_groups_users_rel where gid =%s and uid=%s ",
                (int(jurisdiction_obj.id), par.env.user.id))
            groups_users_obj = [r[0] for r in par._cr.fetchall()]
            print groups_users_obj
            if groups_users_obj:
                print 11
                par.if_group_cusotmer_contact_views = True
                return True
            else:
                print 22
                par.if_group_cusotmer_contact_views = False
                return False

    card_type = fields.Selection([('passport', u'护照'), ('card', u'身份证')], string=u'证件类型', default='card')
    card = fields.Char(string=u'身份证号', default=_card_info, size=18)
    business_license = fields.Char(string=u'营业执照', size=20)
    passport = fields.Char(string=u'护照', size=9)
    birthday = fields.Char(string=u'生日')
    age = fields.Char(string=u'年龄(岁)')
    sex = fields.Char(string=u'性别')
    isinscomp = fields.Boolean(string=u'是否保险公司', default=False)

    if_group_cusotmer_contact_views = fields.Boolean(string=u'是否有“客户联络信息查看”的权限',
                                                     compute="_get_if_group_cusotmer_contact_views")

    # _sql_constraints = [
    #     ('partner_card_unique', 'unique (card)', u'客户证件号不能重复!'), ]
    #
    # ALTER TABLE "res_partner" ADD CONSTRAINT "res_partner_partner_card_unique" unique (card)

    def get_customer(self, phone=None, card=None):
        '''
        根据身份证或手机号获取客户对象
        :param card: 身份证号
        :param phone: 电话号码
        :return:
        '''
        if card:
            partner = self.search([('card', '=', card)])
        else:
            partner = self.search(['|', ('mobile', '=', phone), ('phone', '=', phone)])
        if partner:
            return partner
        else:
            return False

    # @api.multi
    def create_customer(self, name, phone=None, card=None):
        # def create_customer(self):
        '''
        创建一个客户: 根据客户姓名、电话、身份证创建新客户
        :param name:客户姓名
        :param phone: 客户电话
        :param card: 客户身份证
        :return:
        '''
        check_card = self._card_info(card)
        if check_card == None:
            if card:
                partner = self.search([('card', '=', card)])
            else:
                partner = self.search(['|', ('mobile', '=', phone), ('phone', '=', phone)])
            if not partner:
                customer_info = {}
                customer_info['name'] = name
                customer_info['phone'] = phone
                customer_info['card'] = card
                return self.sudo().create(customer_info)
            else:
                return False
        else:
            return False

    def update_customer(self, phone=None, card=None):
        '''
        根据身份证修改客户电话
        :param phone: 客户电话
        :param card: 客户身份证
        :return:
        '''
        if card:
            partner = self.search([('card', '=', card)])
        else:
            partner = self.search(['|', ('mobile', '=', phone), ('phone', '=', phone)])
        if partner:
            return partner.write({'phone': phone})
        else:
            return False

    def write_customer(self, obj, vals):
        '''
        根据客户对象修改客户属性
        :param obj:
        :return:
        '''
        if obj:
            vals["customer"] = True
            return obj.sudo().write(vals)

    def send_mess_partner(self, obj, old_phone, new_phone):
        '''
        手机号发生变更的日志SNS
        :param obj:
        :param old_phone:老电话
        :param new_phone:新电话
        :return:
        '''
        body = ""
        if old_phone:
            body = old_phone[:3] + '****' + old_phone[7:11]
        else:
            body = ""
        print obj.mobile
        print new_phone
        if obj.mobile != new_phone:
            obj.message_post(
                u'手机号已发生变更,由' + body + u' 变为：' + new_phone[:3] + '****' + new_phone[
                                                                          7:11] + u',(操作人：' +
                self.env['toproerp.common'].get_login_user()["name"] + u')')

    def check_phone(self, phone):
        phoneprefix = ['1']
        # 检测号码是否长度是否合法。
        if phone:
            phone = str(phone)
            if len(phone.strip()) > 4:
                if len(phone.strip()) <> 11:
                    print u'客户失败的手机号是 %s' % self.mobile
                    raise Warning(u'客户手机号必须是11位数字')
                else:
                    # 检测输入的号码是否全部是数字。
                    if phone.isdigit():
                        # 检测前缀是否是正确。
                        if phone[:1] in phoneprefix:
                            # print "电话号码是有效的."
                            pass
                        else:
                            # print "无效的手机号码."
                            raise Warning(u'无效的手机号码')
                    else:
                        # print "手机号必须是数字"
                        raise Warning(u'手机号必须是数字')