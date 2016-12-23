# -*- coding: utf-8 -*-
# © <2016> <gld liujing>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, exceptions
from types import ListType
import time
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
import os
from openerp import tools
from PIL import Image, ImageDraw, ImageFont
import logging

_logger = logging.getLogger(__name__)


class PlayWatermark(models.Model):
    _name = "play.watermark"

    def make_watermark(self, obj=None, number=None, attachment_obj=None):
        '''
        打水印、根据文件类型分别调用不同的打水印的方法
        :param obj: 对象 当前要打水印的单据对象
        :param number: 要打水印的文字
        :param attachment_obj: 附件对象 例如：ir.attachment(109,)
        :return:
        '''
        if attachment_obj:  # 如果当前附件对象直接有值 就直接给这个对象打印水印
            attachment_ids = attachment_obj
        else:
            attachment_ids = obj['attachment_ids']  # 取得附件对象 例如：ir.attachment(109,)（只适用于单据上的水印）
            number = str(number).replace(u'(副本)', '')

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
                        self.make_watermark_image(attachment, number)
                    else:
                        self.make_watermark_pdf(number, attachment)
                except Exception as ex:
                    _logger.info(u'error:%s' % ex)
                    raise exceptions.Warning(u"文件类型错误或者文件已经被损坏！")
            else:
                raise exceptions.Warning(u"只允许传pdf或者图片文件！")
        return att_names

    def make_watermark_image(self, attachment, number):
        '''
        给图片类型的文件打水印
        :param attachment: 附件对象
        :param number: 要打的数据
        :return:
        '''
        print u'准备给图片打水印----看以下输出的日志是否正确-通用模块'
        print attachment
        fname, full_path = self.env['ir.attachment'].sudo()._get_path(number, attachment.checksum)
        img = Image.open(full_path)
        print img
        # font = ImageFont.truetype('simsun.ttc', 50)
        font = ImageFont.load_default()
        print font
        img2 = Image.new('RGB', (300, 200), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        height = img.size[0]
        width = img.size[1]

        print number
        x = 50
        y = 50
        step = 100
        while x < height and y < width:
            draw.text((x, y), number, (0, 0, 0), font=font)
            x += step
            y += step
        img.save(full_path, 'JPEG')

    @tools.ormcache()
    def _filestore(self):
        return tools.config.filestore(self._cr.dbname)

    def make_watermark_pdf(self, number, attachment):
        '''
        给PDF类型的文件打水印
        :param number:
        :param attachment:
        :return:
        '''
        print u'准备给PDF打水印----看以下输出的日志是否正确-通用模块'
        print attachment
        print number

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

        # def make_watermark_image(self, attachment, number):
        #     '''
        #     给图片类型的文件打水印
        #     :param attachment: 附件对象
        #     :param number: 要打的数据
        #     :return:
        #     '''
        #     print u'准备给图片打水印----看以下输出的日志是否正确-通用模块'
        #     print attachment
        #     print number
        #
        #     icp = self.env['ir.config_parameter']
        #     font = icp.get_param('make_watermark_font')
        #
        #     # Liberation Sans  服务器字体
        #     fname, full_path = self.env['ir.attachment'].sudo()._get_path(number, attachment.checksum)
        #     img = Image.open(full_path)
        #     font = ImageFont.truetype(font, 50)
        #     img2 = Image.new('RGB', (300, 200), (255, 255, 255))
        #     draw = ImageDraw.Draw(img)
        #     draw.text((0, 50), number, (0, 0, 0), font=font)
        #     img.save(full_path, 'JPEG')
        #
        # #
        # def make_watermark_pdf(self, number, attachment):
        #     '''
        #     给PDF类型的文件打水印
        #     :param number:
        #     :param attachment:
        #     :return:
        #     '''
        #     b = self._filestore()
        #     a = b + '/' + attachment[0]['store_fname'].split('/')[0] + "/"
        #     old_file_name = attachment[0]['store_fname'].split('/')[1]
        #     c = canvas.Canvas(a + u"shuiyin.pdf")
        #     c.setFont("Courier", 35)
        #     # 设置水印文字的灰度
        #     c.setFillGray(0.4, 0.4)
        #     # 设置水印文件，并将文字倾斜45度角
        #     c.saveState()
        #     c.translate(500, 100)
        #     c.rotate(45)
        #     c.drawCentredString(200, 300, number)
        #     c.restoreState()
        #     c.save()
        #     output = PdfFileWriter()
        #     aa = file(b + '/' + attachment[0]['store_fname'], 'rb')
        #     input1 = PdfFileReader(aa)
        #     bb = file(a + u'shuiyin.pdf', 'rb')
        #     water = PdfFileReader(bb)
        #     # 获取pdf文件的页数
        #     pageNum = input1.getNumPages()
        #     # 给每一页打水印
        #     for i in range(pageNum):
        #         page = input1.getPage(i)
        #         page.mergePage(water.getPage(0))
        #         output.addPage(page)
        #     # 最后输出文件
        #     outStream = file(a + u'fwddwenjian.pdf', 'wb')
        #     output.write(outStream)
        #     aa.close()
        #     bb.close()
        #     outStream.close()
        #     os.chdir(a)
        #     os.remove("shuiyin.pdf")  # 删除水印文件
        #     os.remove(old_file_name)  # 删除上次源文件
        #     os.rename('fwddwenjian.pdf', old_file_name)  # 添加水印的文件改名
