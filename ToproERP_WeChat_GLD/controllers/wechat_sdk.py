import time
import random
import string
import hashlib


class Sign:
    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        # print string
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret


if __name__ == '__main__':
    # sign = Sign('jsapi_ticket', 'http://example.com')
    # sign = Sign('jsapi_ticket', 'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token=HYltRN0byXlngFKPR_jbWetJ2t6KQuItG2V3FfjJGZEg6jtX4TJq_AQqMCueizr0')
    sign = Sign('jsapi_ticket', 'https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token=HYltRN0byXlngFKPR_jbWetJ2t6KQuItG2V3FfjJGZEg6jtX4TJq_AQqMCueizr0')
    # print sign.sign()
