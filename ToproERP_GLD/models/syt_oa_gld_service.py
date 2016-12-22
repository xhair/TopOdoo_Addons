# -*- coding: utf-8 -*-
# © <2016> <ToproERP liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, exceptions
from types import ListType
import time
import logging
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
import os
from openerp import tools
from PIL import Image, ImageDraw, ImageFont

_logger = logging.getLogger(__name__)


class syt_oa_gld_service(models.Model):
    _name = "syt.oa.gld.service"
    _description = u'工联单服务'

    # 发送消息
    def gld_post_message(self, rece_uid, msg, gld_id):
        gld_bean = self.env['syt.oa.gld'].search([('id', '=', gld_id)])
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url = "%s/web#id=%s&view_type=form&model=syt.oa.gld" % (base_url, gld_id)
        body = msg % ("<a href='%s'>%s</a>" % (url, gld_bean['subject']))
        body2 = msg % ("%s" % (gld_bean['subject']))
        # self.env('res.users').message_post(rece_uid, body2=body2, gld_id_d="gld_id")

    def delete_approver_by_uid(self, gld_id, open_id=None):
        '''
        从工联单中删除一个审批人
        :param gld_id: 工联单ID
        :return:
        '''
        # 获取当前用户对应的员工ID
        if open_id != None:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', int(open_id))])
            if employee:
                empid = employee.id
            else:
                empid = 0
        else:
            empid = self.env['toproerp.common'].get_login_user()['id']
        if empid:
            gld_bean = self.env['syt.oa.gld'].sudo().search([('id', '=', gld_id), ('approver', 'in', empid)])
            if gld_bean:
                vals = {'approver': [(3, empid)]}
                op_ids = self.env['syt.oa.gld.opinion'].sudo().search(
                    [('approver', '=', empid), ('gld_id', '=', gld_id)])
                if op_ids:
                    # 删除工联单下对应的审批意见
                    op_ids.unlink()
                gld_bean.write(vals)
                if open_id == None:
                    gld_bean.message_post(
                        self.env['toproerp.common'].get_login_user()["name"] + u"确认,本工联单的审批,不在本人审批范围")

    def get_approver(self, uid=None):
        if uid == False:
            uid = self.env.uid

        # self._cr.execute(
        #     "select approver from syt_oa_gld_opinion where create_uid =%s and opinion!='' group by approver LIMIT 5",
        #     (uid,))

        self._cr.execute(
            "select a.approver from syt_oa_gld_opinion as a ,hr_employee as b, resource_resource as c where a.approver =b.id and c.id = b.resource_id and c.active = true and a.create_uid = %s and a.opinion!='' group by a.approver limit 5;" % uid)
        configured_cmp = [r[0] for r in self._cr.fetchall()]
        return configured_cmp

    @api.model
    def create_opinion(self, gld):
        '''
        将审批意见写到意见表中去
        :param gld:
        :return:
        '''
        if gld:
            opinionsid_ids = []
            for approver in gld["approver"]:
                employee = self.env['hr.employee'].sudo().search([('id', '=', approver.id)])
                vals = {}
                vals['approver'] = approver.id
                vals['approver_dept'] = employee['department_id'].name
                vals['gld_id'] = gld.id
                vals['company_id'] = approver.company_id.name
                class_name = 'syt.oa.gld.opinion'  # 获得对象类名
                method_name = 'add_opinion'  # 获得对象的方法
                objFunc = getattr(self.env[class_name], method_name)
                opinionsid = objFunc(vals)
                opinionsid_ids.append((4, opinionsid))
            return opinionsid_ids

    @api.model
    def create_opinion_gld(self, gld_id, approver):
        '''
        将审批意见写到意见表中去
        :param gld:
        :return:
        '''
        if approver:
            opinionsid_ids = []
            for approver in approver:
                employee = self.env['hr.employee'].sudo().search([('id', '=', int(approver.id))])
                vals = {}
                vals['approver'] = approver.id
                vals['approver_dept'] = employee['department_id'].name
                vals['gld_id'] = gld_id
                vals['company_id'] = approver.company_id.name
                class_name = 'syt.oa.gld.opinion'  # 获得对象类名
                method_name = 'add_opinion'  # 获得对象的方法
                objFunc = getattr(self.env[class_name], method_name)
                opinionsid = objFunc(vals)
                opinionsid_ids.append((4, opinionsid))
            return opinionsid_ids

    @tools.ormcache()
    def _filestore(self):
        return tools.config.filestore(self._cr.dbname)

    def create_service(self, gld, pc_wechat=None):
        '''
        创建的业务单据方法
        :param gld: 工联单
        :return:
        '''
        # 将审批意见写到意见表中去
        opinionsid_ids = self.create_opinion(gld)
        # 生成编号
        random_num = self.serial_number_product(gld['id'])
        number = 'GLD' + time.strftime('%Y%m%d') + random_num

        # SNS信息
        gld.message_post(self.env['toproerp.common'].get_login_user()["name"] + u"创建工联单")
        # 更新审批人列表,返回待审，已审人uid拼接的字符串
        app_ids_string_ds, app_ids_string_ys = self.write_app_string(gld['id'])
        vals = {}
        vals['name'] = number
        vals['number'] = number
        vals['is_init'] = False
        # vals['user_id_gld'] = self.get_user_by_employee(gld['sponsor'].id).id
        vals['user_id_gld'] = self.env["toproerp.common"].get_user_by_employee(gld['sponsor'].id)
        if pc_wechat != "wechat":
            # 给附件打水印
            # att_names = self.make_water_photo(gld, number)
            att_names = self.env['play.watermark'].make_watermark(obj=gld, number=number)
            vals['att_names'] = att_names
        vals['message_follower_ids'] = "message_follower_ids"
        vals['approver_opinions'] = opinionsid_ids
        vals['approvals_user_ids'] = app_ids_string_ds
        vals['yi_approver_user_ids'] = app_ids_string_ys
        return vals

    def delete_will_copy_users(self, gld_id):
        '''
        完成状态下继续审批工联单 删除预设抄送人
        :param gld_id:
        :return:
        '''
        if (type(gld_id) is ListType):
            gld_id = gld_id[0]
        gld_bean = self.env["syt.oa.gld"].browse(gld_id)
        # 如果状态为审批中
        # if (gld_bean.state == 'through'):
        #     for will_copy in gld_bean.will_copy_users:
        #         sql = 'delete from  syt_oa_gld_copyuser_rel  where copy_id =' + str(
        #             will_copy.id) + ' and gld_id= ' + str(gld_id)
        #         cr.execute(sql)

    def serial_number_product(self, gld_id):
        '''
        生成编码
        :param gld_id:
        :return:
        '''
        b = ''
        a = str(gld_id)
        if len(a) > 0:
            if len(a) >= 4:
                b = a[-4:]
            elif len(a) == 3:
                b = '0' + a
            elif len(a) == 2:
                b = '00' + a
            elif len(a) == 1:
                b = '000' + a
        return b

    def employee_vali(self, gld):
        '''
        工联单create的业务方法
        :param gld: 工联单对象
        :return:
        '''
        now_date = time.strftime('%Y-%m-%d')
        if int(gld['expiration'].replace("-", "")) <= int(now_date.replace("-", "")):
            raise exceptions.Warning(u"截止时间必须大于发起时间！")
            # hr = self.env('hr.employee')

            for approver in gld["approver"][0][2]:
                employee = self.env['hr.employee'].sudo().search([('id', '=', approver)])
                if (not employee['department_id']):
                    raise exceptions.Warning(u"添加的审批用户【' + employee['name'] + u'】没有所属部门,请联系管理员！")
                if (not employee['resource_id']):
                    raise exceptions.Warning(u'提示：', u'添加的审批用户【' + employee['name'] + u'】没有所属用户,请联系管理员')

    @api.model
    def create_gld_from_other(self, business_bill_number, subject, content, approver, emergency, business_class,
                              attachment_ids):
        # def create_gld_from_other(self):
        '''
        提供接口：为所有业务单据提供创建工联单的接口
        :param business_bill_number: 业务单据编号
        :param subject: 标题
        :param content: 正文
        :param approval: 审批人
        :param emergency: 优先级（急、特急、一般）
        :param business_class:来自于哪个业务类（比如你当前操作的业务对象类，odoo类）
        :return:此方法返回一个工联单对象
        回写方法名：from_gld_message(工联单业务对象，业务单据编号)
        '''

        # business_bill_number = 'QJ001'  # 业务单据编号
        # subject = u'关于刘晶请假的申请'  # 标题
        # content = u'尊敬的领导，您好，本人于2016年2月28日请年假一天，望批准。'  # 正文
        # approver = 1  # 审批人
        # emergency = u'general'  # 优先级（急、特急、一般）
        # business_class = 'yewulei'  # 来自于哪个业务类（比如你当前操作的业务对象类，odoo类）
        #
        # approver = [2, 4, 3]
        apprs = []
        appas = []
        approver_id = ''  # 审批人id
        attachment_id = ''
        for appr in approver:
            approver_id += str(appr) + ','
            apprs.append((4, appr))
        for appa in attachment_ids:
            attachment_id += str(appa) + ','
            appas.append((4, appa.id))
        vals = {}
        vals['subject'] = subject
        vals['content'] = content
        vals['approver'] = apprs  # 审批人
        vals['emergency'] = emergency
        vals['expiration'] = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400 * 3))  # 截止时间
        vals['attachment_ids'] = appas
        vals['relevant_documents'] = business_bill_number
        vals['approvals_user_ids'] = approver_id
        vals['business_object'] = business_class

        # 保存数据
        gld_id = self.env['syt.oa.gld'].create(vals)
        if gld_id:
            # 创建业务单据  返回单号
            write_val = self.create_service(gld_id)
        # 更新业务单号
        gld_id.write({'name': write_val['name'], 'state': 'pending'})
        # 发送消息给审批人
        agentid = self.env['wechat.enterprise.app'].sudo().search([('name', '=', u'工联单')])
        icp = self.env['ir.config_parameter']
        insur_str = icp.get_param('web.base.url')
        for item in approver:
            employee = self.env['hr.employee'].search([('id', '=', int(item))], limit=1)
            if employee:
                descrpition = u"你收到了一张标题为“%s”的工联单，需要您进行审批，请点击查看全文，马上处理！" % (gld_id.subject)
                url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                    gld_id.name, '2', employee.user_id.id)  # 跳转地址，需要和微信保持一致
                employee.send_news_message(agentid.agentid, subject, descrpition, url)
        return gld_id

    def find_is_appo_finish(self, gld_id, gld, opinion, shuzi, employee=None):
        '''
        处理判断此工联单是否已经审批完成
        :param gld_id: 工联单ID
        :param gld: 工联单对象
        :return:
        '''
        if gld:
            # 如果没有审批人
            if len(gld.approver) == 0 and len(gld.approver_opinions) == 0:
                # 状态置为草稿
                state_str = u'作废'
                if gld.business_object and gld.relevant_documents:
                    gld.sudo().write({"state": "cancel"})

                else:
                    gld.sudo().write({"state": "draft"})
                    state_str = u'草稿'

                gld.message_post(u"无审批人,系统自动置为[%s]状态." % state_str)
                icp = self.env['ir.config_parameter']
                insur_str = icp.get_param('web.base.url')
                url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                    gld.name, '2', gld.sponsor.user_id.id)
                # url = insur_str + '/WechatGLD/xiangqing?name=%s' % (gld.name)
                title = u'单号：' + gld.name
                description = u'该工联单状态发生改变，已置为[%s]，点击查看全文！' % state_str
                self.env['syt.oa.gld'].get_gld_agentid(gld.sponsor,
                                                       title, description, url)
                # gld.get_gld_agentid(gld.sponsor,
                #                     title,description, url)
                self.return_to_other_document(gld)
                return {}

        # 是否全审批
        a = True
        # 是否全同意
        b = True
        # 判断是否所有人都完成审批
        strs = u'不同意'
        for opin in gld.approver_opinions:
            if opin.opinion == False:
                a = False
            if opin.opinion and str(opin.opinion.encode('utf-8')).find(strs.encode('utf-8')) > -1:
                b = False
        state = 'pass'
        if a:
            # 同意
            if b:
                state = 'through'
            # 不同意
            else:
                state = 'n_through'

        gld.sudo().write({'state': state})
        # SNS信息
        gld_state = gld.state
        employee_name = ''
        if shuzi == 2:
            if employee:
                employee_name = employee.name
        else:
            employee_name = self.env['toproerp.common'].get_login_user()["name"]
        if gld_state == "through":
            gld.message_post(employee_name + u'审批工联单,审批意见为：' + opinion + u',所有审批人审批完毕')
        else:
            if opinion:
                gld.message_post(employee_name + u'审批工联单,审批意见为：' + opinion)
            else:
                gld.message_post(employee_name + u'审批工联单,审批意见为：不在审批范围')

        dq_state = ''
        icp = self.env['ir.config_parameter']
        insur_str = icp.get_param('web.base.url')
        title = u'单号：' + gld.name
        if gld.state == "pass":
            dq_state = u"审批中"
        elif gld.state == "through":
            dq_state = u"通过"
            for appr in gld.approver:
                url = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (gld.name, '2', appr.user_id.id)
                description = u'标题为“%s”的工联单已审核通过，点击查看全文！' % gld.subject
                self.env['syt.oa.gld'].get_gld_agentid(appr,
                                                       title, description, url)
            description = u'标题为“%s”的工联单已审核通过，点击查看全文！' % gld.subject
            urls = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                gld.name, '2', gld.sponsor.user_id.id)
            self.env['syt.oa.gld'].get_gld_agentid(gld.sponsor,
                                                   title, description, urls)
        elif gld.state == "n_through":
            dq_state = u"不通过"
            for appr in gld.approver:
                url_ = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (gld.name, '2', appr.user_id.id)
                description = u'标题为“%s”的工联单审核不通过，点击查看全文' % gld.subject
                self.env['syt.oa.gld'].get_gld_agentid(appr, title, description, url_)
            description = u'标题为“%s”的工联单审核不通过，点击查看全文' % gld.subject
            urls = insur_str + '/WechatGLD/xiangqing?name=%s&qubie=%s&userid=%s' % (
                gld.name, '2', gld.sponsor.user_id.id)
            self.env['syt.oa.gld'].get_gld_agentid(gld.sponsor,
                                                   title, description, urls)
        self.return_to_other_document(gld)

    def return_to_other_document(self, gld):
        """

        :param gld:
        :return:
        """
        if gld and gld.relevant_documents:
            try:
                application = self.env[gld.business_object].sudo()
                application.from_gld_message(gld, gld.relevant_documents)
            except Exception as ex:
                _logger.error(u'%s %s' % (gld, ex))

    def back_process_recode(self, other_name):
        '''
        当请假单据追回时，把当前单据对应的工联单置为作废
        :param gld_name:
        :return:
        '''
        if other_name:
            gld_obj = self.env['syt.oa.gld'].search([('processe_name', '=', other_name)])
            for record in gld_obj:
                if record:
                    if record.state != 'pending':
                        raise exceptions.Warning(u"您提交的工联单只有待审状态下才能追回！")
                    else:
                        record.write({'state': 'cancel', 'approvals_user_ids': False, 'copy_users_dy_ids': False})

    def cencal_process_recode(self, other_name):
        '''
        当请假单据作废时，把当前单据对应的工联单置为作废
        :param gld_name:
        :return:
        '''
        if other_name:
            gld_obj = self.env['syt.oa.gld'].search([('processe_name', '=', other_name)])
            for item in gld_obj:
                if item:
                    item.write({'state': 'cancel', 'approvals_user_ids': False, 'copy_users_dy_ids': False})

    def write_app_string(self, gld_id):
        '''
        更新权限字段字符串 id是单个，不要用数组，如果是整形，请自行循环调用
        :param gld_id: 工联单ID
        :return:
        '''
        gld_bean = self.env['syt.oa.gld'].search([('id', '=', gld_id)])
        app_ids_string_ys = ','  # 已审批人id
        app_ids_string_ds = ','  # 审批人id
        for opin in gld_bean.approver_opinions:
            if opin.opinion and opin.opinion != '':
                app_ids_string_ys += str(self.env.uid) + ","  # 已审批人Id
        if gld_id:
            employee_id = self.env['toproerp.common'].get_login_user()["id"]  # 获取员工的 id
            app_ids_string_ds = [(3, employee_id)]  # 审批人Id
        # 返回待审已审拼装的好的数据
        return app_ids_string_ds, app_ids_string_ys

    # 给工联单附件Pdf打水印
    def product_weate_photo(self, number, attachment):
        b = self._filestore()
        a = b + '/' + attachment[0]['store_fname'].split('/')[0] + "/"
        old_file_name = attachment[0]['store_fname'].split('/')[1]
        c = canvas.Canvas(a + u"shuiyin.pdf")
        c.setFont("Courier", 35)
        # 设置水印文字的灰度
        c.setFillGray(0.4, 0.4)
        # 设置水印文件，并将文字倾斜45度角
        c.saveState()
        c.rotate(45)  # 旋转角度

        c.translate(500, 100)  # 重设中心点
        c.drawCentredString(100, 270, number)

        # c.translate(200, 350)  # 重设中心点
        c.drawCentredString(0, 0, number)  # 绘制一个以坐标为中心的字符串
        #
        # c.translate(400, 50)  # 重设中心点
        c.drawCentredString(-100, -300, number)
        c.restoreState()
        c.save()
        output = PdfFileWriter()
        aa = file(b + '/' + attachment[0]['store_fname'], 'rb')
        input1 = PdfFileReader(aa)
        bb = file(a + u'shuiyin.pdf', 'rb')
        water = PdfFileReader(bb)
        # 获取pdf文件的页数
        pageNum = input1.getNumPages()
        # 给每一页打水印
        for i in range(pageNum):
            page = input1.getPage(i)
            page.mergePage(water.getPage(0))
            output.addPage(page)
        # 最后输出文件
        outStream = file(a + u'shuchuwenjian.pdf', 'wb')
        output.write(outStream)
        aa.close()
        bb.close()
        outStream.close()
        os.chdir(a)
        os.remove("shuiyin.pdf")  # 删除水印文件
        os.remove(old_file_name)  # 删除上次源文件
        os.rename('shuchuwenjian.pdf', old_file_name)  # 添加水印的文件改名

    # 给工联单附件图片打水印
    def make_watermark(self, attachment, gld_id):
        '''
        :param attachment: 附件对象
        :param gld_id: 要打的工联单编号（字段name）
        :return:
        '''
        fname, full_path = self.env['ir.attachment'].sudo()._get_path(gld_id, attachment.checksum)
        img = Image.open(full_path)
        # font = ImageFont.truetype('simsun.ttc', 50)
        font = ImageFont.load_default()

        img2 = Image.new('RGB', (300, 200), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        height = img.size[0]
        width = img.size[1]

        x = 50
        y = 50
        step = 100
        while x < height and y < width:
            draw.text((x, y), gld_id, (0, 0, 0), font=font)
            x += step
            y += step

        img.save(full_path, 'JPEG')

    # 打水印、判断文件类型 是否为pdf和Image 暂时没用
    def make_water_photo(self, gld, number):
        attachment_ids = gld['attachment_ids']
        att_obj = self.env['ir.attachment']
        att_names = ''
        for at in attachment_ids:
            attachment = att_obj.search([('id', '=', at.id)])
            att_names += attachment[0]['datas_fname'] + u';'
            if len(attachment[0]['datas_fname'].split(".")) > 1 and attachment[0]['datas_fname'].split(".")[
                        len(attachment[0]['datas_fname'].split(".")) - 1].lower() == 'pdf' or \
                            attachment[0]['datas_fname'].split(".")[
                                        len(attachment[0]['datas_fname'].split(".")) - 1].lower() == 'jpg':
                try:

                    if attachment[0]['datas_fname'].split(".")[
                                len(attachment[0]['datas_fname'].split(".")) - 1].lower() == 'jpg':
                        # self.env["play.watermark"].make_watermark(attachment, number)
                        self.make_watermark(attachment, number)
                    else:
                        # self.env["play.watermark"].product_weate_photo(number, attachment)
                        self.product_weate_photo(number, attachment)
                except:
                    raise exceptions.Warning(u"文件类型错误或者文件已经被损坏！")
            else:
                raise exceptions.Warning(u"只允许传pdf或者jpg文件！")
        return att_names
