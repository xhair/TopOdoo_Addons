/**
 * Created by suntao on 2016/1/10.
 */

//获取链接传过来的openID参数
function getUrlParam(url, name) {
    var pattern = new RegExp("[?&]" + name + "\=([^&]+)", "g");
    var matcher = pattern.exec(url);
    var items = null;
    if (matcher != null) {
        try {
            items = decodeURIComponent(decodeURIComponent(matcher[1]));
        } catch (e) {
            try {
                items = decodeURIComponent(matcher[1]);
            } catch (e) {
                items = matcher[1];
            }
        }
    }
    items = items.replace(/^\s*/, "");
    return items;
}

//加载当前日期
//var my_date = new Date();
//var years = my_date.getFullYear();
//var months = my_date.getMonth() + 1;
//if (months < 10) {
//    months = "0" + months;
//}
//var days = my_date.getDate();
//document.getElementById("reservation_time").value = years + "/" + months + "/" + days;

//document.getElementById("verify").style.display = "none";
//document.getElementById("verify_change_button").style.display = "none";

function change_info() {
    document.getElementById("phone_no").removeAttribute("readonly", "readonly");
    document.getElementById("change_button").style.display = "none";
    document.getElementById("verify").style.display = "block";
    document.getElementById("verify_change_button").style.display = "block";
}

// 关闭提示
function close_modal() {
    document.getElementById("modal").style.display = "none";
}


// 新客户进行会员注册
function sure() {
    var verify = $("#verify_value").val();
    var customer_name = $("#customer_name").val();
    var IDcard = $("#IDcard").val();
    var phone_no = $("#phone_no").val();
    if (customer_name.length < 1) {
        document.getElementById("prompt_comment").innerHTML = "无效的姓名";
        document.getElementById("modal").style.display = "block";
        return false;
    }
    if (IDcard.length != 18) {
        document.getElementById("prompt_comment").innerHTML = "无效的身份证号";
        document.getElementById("modal").style.display = "block";
        return false;
    }
    if (phone_no.length != 11) {
        document.getElementById("prompt_comment").innerHTML = "无效的手机号";
        document.getElementById("modal").style.display = "block";
        return false;
    }
    if (verify.length != 4) {
        document.getElementById("prompt_comment").innerHTML = "无效的验证码";
        document.getElementById("modal").style.display = "block";
        return false;
    }
    //验证验证码是否正确
    $.ajax({
        type: 'POST',
        url: "/wechat/check_verify",
        data: {phone: phone_no, verification_code: verify},
        success: function (result) {
            if (result == verify) {
                $.ajax({
                    type: 'POST',
                    url: "/wechat/register",
                    data: {name: customer_name, phone: phone_no, card: IDcard},
                    success: function (result) {
                        if (result == customer_name) {
                            document.getElementById("prompt_comment").innerHTML = "注册成功";
                            register_success();
                        }
                        else if (result == "1") {
                            document.getElementById("prompt_comment").innerHTML = "注册失败";
                            document.getElementById("modal").style.display = "block";
                            return false;
                        }
                        else if (result == "2") {
                            document.getElementById("prompt_comment").innerHTML = "更新资料成功";
                            register_success();
                        }
                        else if (result == "3") {
                            document.getElementById("prompt_comment").innerHTML = "该手机号已经注册";
                            register_success();
                        }
                    },
                    error: function () {
                        document.getElementById("prompt_comment").innerHTML = "发生错误";
                        document.getElementById("modal").style.display = "block";
                        return false;
                    },
                });
            }
            else {
                document.getElementById("prompt_comment").innerHTML = "验证码错误";
                document.getElementById("modal").style.display = "block";
            }
        },
        error: function () {
            alert("无法验证");
        }
    });

}
//注册成功后的样式变化
function register_success() {
    document.getElementById("modal").style.display = "block";
    document.getElementById("phone_no").setAttribute("readonly", "readonly");
    document.getElementById("customer_name").setAttribute("readonly", "readonly");
    document.getElementById("IDcard").setAttribute("readonly", "readonly");
    document.getElementById("verify_value").value = "";
    document.getElementById("send_verify_button").innerHTML = "发送验证码";
    document.getElementById("verify").style.display = "none";
    document.getElementById("change_button").style.display = "block";
    document.getElementById("change_button").innerHTML = "修改信息";
    document.getElementById("verify_change_button").style.display = "none";
}

// 选择预约项目时背景变色
function choose_reservation_type(links) {
    var reservation_type = document.getElementsByClassName("reservation_type");
    var label = document.getElementsByClassName("label");
    for (var i = 0; i < reservation_type.length; i++) {
        label[i].style.backgroundColor = "#d9d9d9";
        label[i].style.color = "#000000";
        if (reservation_type[i].checked) {
            label[i].style.backgroundColor = "#337ab7";
            label[i].style.color = "#ffffff";
        }
    }
}


//发送短信
function get_phone_verify() {
    var phone_no = $("#phone_no").val();
    if (phone_no.length != 11) {
        document.getElementById("prompt_comment").innerHTML = "电话号码错误";
        document.getElementById("modal").style.display = "block";
        return false;
    }
    $.ajax({
        type: 'POST',
        url: "/wechat/get_phone_verify",
        data: {phone: phone_no, expires_Minute: 10},
        success: function (result) {
            if (result == phone_no) {
                $("#send_verify_button").text("已发送(60s)");
                document.getElementById("send_verify_button").setAttribute("disabled", "disabled");
                inital_time = 60;
                timer();
            }
            else {
                $("#send_verify_button").text("发送失败");
            }
        },
        error: function () {
            document.getElementById("prompt_comment").innerHTML = "发送失败";
            document.getElementById("modal").style.display = "block";
        }
    });
}

//计时器

function timer() {
    a_timer = setInterval("times()", 1000);
}
function times() {
    inital_time--;
    $("#send_verify_button").text("已发送(" + inital_time + "s)");
    if (inital_time == 0) {
        clearInterval(a_timer);
        $("#send_verify_button").text("发送验证码");
        document.getElementById("send_verify_button").removeAttribute("disabled");
    }
}

//获取当前openID
var url = window.location;
var openID = getUrlParam(url, "openID");
// 跳转至注册页面
function customer_bind_start() {
    window.location.href = "/wechat/customer_bind_start?openID=" + openID;
}
// 跳转至预约页面
function customer_bind() {
    window.location.href = "/wechat/customer_bind?openID=" + openID;
}
// 跳转至预约管理页面
function reservation_list() {
    window.location.href = "/wechat/reservation_list?openID=" + openID;
}

