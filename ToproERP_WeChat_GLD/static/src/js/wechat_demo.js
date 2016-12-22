/**
 * Created by Administrator on 2016/3/11.
 */


wx.ready(function () {
    var images = {
        localId: [],
        serverId: []
    };

    //添加附件按钮
    document.querySelector('#add_fujian_id').onclick = function () {

        //alert(123456);
        //打开照片
        wx.chooseImage({
            count: 1, // 默认9
            sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
            sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
            success: function (res) {
                var localIds = res.localIds; // 返回选定照片的本地ID列表，localId可以作为img标签的src属性显示图片
                images.localId = res.localIds;
                var i = 0, length = images.localId.length;
                if (length > 0) {
                    images.serverId = [];
                    //上传图片到微信服务器
                    wx.uploadImage({
                        localId: images.localId[i], // 需要上传的图片的本地ID，由chooseImage接口获得
                        isShowProgressTips: 1,// 默认为1，显示进度提示
                        success: function (res) {
                            i++;
                            images.serverId.push(res.serverId); // 返回图片的服务器端ID
                            //下载图片到本地保存
                            if (images.serverId.length == 0) {
                                return;
                            }
                            var i = 0, length = images.serverId.length;
                            images.localId = [];
                            wx.downloadImage({
                                serverId: images.serverId[i], // 需要下载的图片的服务器端ID，由uploadImage接口获得
                                isShowProgressTips: 1,// 默认为1，显示进度提示
                                success: function (res) {
                                    var localId = res.localId; // 返回图片下载后的本地ID
                                    $.ajax({
                                            type: 'POST',
                                            url: "/WechatGLD/downloadImage",
                                            data: {media_id: images.serverId[i]},
                                            dataType: "json",
                                            success: function (result) {
                                                $("#attachment_id").text($("#attachment_id").text() + ',' + $(result).attr("attachment_id"))
                                                $("#image_name").text($(result).attr("image_name"))
                                            },
                                            error: function () {
                                                return false;
                                            }
                                        }
                                    );
                                }
                            });

                        },
                        fail: function (res) {
                            //alert(JSON.stringify(res));
                        }
                    });
                }
            }
        });
    }
});

wx.error(function (res) {
    //alert(res.errMsg);
});

