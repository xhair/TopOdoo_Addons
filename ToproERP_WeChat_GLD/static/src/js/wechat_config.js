var nonceStr;
var timestamp;
var signature;

var template_type = getUrlParam(window.location, "template_type");
var template = getUrlParam(window.location, "template");
var title = getUrlParam(window.location, "title");
var text = getUrlParam(window.location, "text");
var emergency = getUrlParam(window.location, "emergency");
var url = location.href.split('#')[0]

//alert(url)
$.ajax({
    type: 'POST',
    url: "/WechatGLD/get_signature",
    data: {
        url: url
    },
    dataType: "json",
    success: function (result) {
        //alert(location.href.split('#')[0])
        //alert($(result).attr('nonceStr'))
        //alert($(result).attr('timestamp'))
        //alert($(result).attr('signature'))
        //alert($(result).attr('jsapi_ticket'))
        wx.config({
            debug: true,// 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
            appId: 'wxc1317b61e7e122aa',// 必填，企业号的唯一标识，此处填写企业号corpid
            //appId: 'wx0046935c06f7c27e',// 必填，企业号的唯一标识，此处填写企业号corpid
            timestamp: $(result).attr('timestamp'),// 必填，生成签名的时间戳
            nonceStr: '' + $(result).attr('nonceStr') + '',// 必填，生成签名的随机串
            signature: '' + $(result).attr('signature') + '',// 必填，签名，见附录1
            jsApiList: [// 必填，需要使用的JS接口列表，所有JS接口列表见附录2
                'chooseImage',
                'uploadImage',
                'downloadImage',
            ]
        });
    },
    error: function () {
        return false;
    }
});



