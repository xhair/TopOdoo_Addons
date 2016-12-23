/**
 * Created by jiangxiang on 2016/1/25.
 */
//获取链接传过来的预约订单号参数
var url = window.location;
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
    return items;
}


//预约时间的限制,并加载当前时间
var my_date = new Date();
var years = my_date.getFullYear();
var months = my_date.getMonth() + 1;
if (months < 10) {
    months = "0" + months;
}
var days = my_date.getDate();
if (days < 10) {
    days = "0" + days;
}
var current_time = years + "-" + months + "-" + days;
document.getElementById("delay_date").value = current_time;

//进入页面时获取时间段，并判断是否已经延期
function get_delay_time_scale() {
    var reservation_no = getUrlParam(url, "reservation_no");
    $.ajax({
        type: 'POST',
        url: "/wechat/get_delay_time_scale",
        dataType: "json",
        data: {reservation_no: reservation_no},
        success: function (result) {
            var delay_time_scale = document.getElementById("delay_time_scale");
            length = getJsonObjLength(result);
            for (var i = 0; i < length; i++) {
                var option = document.createElement("option");
                var option_text = document.createTextNode(result[i].name);
                option.appendChild(option_text);
                option.value = result[i].id;
                delay_time_scale.appendChild(option);
            }
        },
        error: function () {
            return false;
        }
    });
    $.ajax({
        type: 'POST',
        url: "/wechat/judge_if_delay",
        dataType: "json",
        data: {reservation_no: reservation_no},
        success: function (result) {
            if(result.state == "已变更"){
                document.getElementById("delay_button").value = "已变更";
                document.getElementById("delay_button").style.backgroundColor = "#EA2127";
                document.getElementById("delay_button").setAttribute("disabled", "disabled");
                document.getElementById("delay_date").setAttribute("readonly", "readonly");
                var delay_time_scale = document.getElementById("delay_time_scale");
                delay_time_scale.setAttribute("disabled", "disabled");
            }
        },
        error: function () {
            return false;
        }
    });
}
setTimeout("get_delay_time_scale()", 100);

// 提交延期
function reservation_delay() {
    var delay_date = $("#delay_date").val();
    var delay_time_scale = $("#delay_time_scale").val();
    var reservation_no = getUrlParam(url, "reservation_no");
    $.ajax({
        type: 'POST',
        url: "/wechat/reservation_delay",
        dataType: "json",
        data: {reservation_no: reservation_no, delay_time: delay_date, delay_time_scale: delay_time_scale},
        success: function (result) {
            if (result == "1") {
                document.getElementById("prompt_comment").innerHTML = "变更成功";
                document.getElementById("modal").style.display = "block";
                document.getElementById("delay_button").value = "已变更";
                document.getElementById("delay_button").style.backgroundColor = "#EA2127";
                document.getElementById("delay_button").setAttribute("disabled", "disabled");
            }
            else if (result == "0") {
                document.getElementById("prompt_comment").innerHTML = "该订单无法变更";
                document.getElementById("modal").style.display = "block";
            }
        },
        error: function () {
            document.getElementById("prompt_comment").innerHTML = "变更失败";
            document.getElementById("modal").style.display = "block";
        }
    });
}

//获取json数据的长度
function getJsonObjLength(jsonObj) {
    var Length = 0;
    for (var item in jsonObj) {
        Length++;
    }
    return Length;
}


// 检查是否选取当前日期之前

function check_date(){
    var delay_date = $("#delay_date").val();
    if(current_time > delay_date){
        $("#delay_date").val(current_time);
        document.getElementById("prompt_comment").innerHTML = "预约时间小于当前时间";
        document.getElementById("modal").style.display = "block";
    }
    else{
        return false;
    }
}