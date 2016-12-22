/**
 * Created by suntao on 2016/1/25.
 */

// 取消预约提示
function cancel_reservation_prompt() {
    document.getElementById("prompt_text").innerHTML = "确定取消预约吗？";
    document.getElementById("prompt").style.display = "none";
    document.getElementById("modal").style.display = "block";

}

// 取消预约
function cancel_reservation() {
    document.getElementById("modal").style.display = "none";
    var cancel_reservation = document.getElementById("cancel_reservation");
    var reservation_no = $("#reservation_no").text();
    var reservation_delay = document.getElementsByClassName("reservation_delay")[0];
    $.ajax({
        type: 'POST',
        url: "/wechat/cancel_reservation",
        data: {reservation_no: reservation_no},
        dataType: "json",
        success: function (result) {
            if (result == "0") {
                document.getElementById("prompt_comment").innerHTML = "该预约不存在";
                document.getElementById("modal").style.display = "block";
            }
            else if (result == "1") {
                document.getElementById("prompt_comment").innerHTML = "取消预约成功";
                document.getElementById("prompt").style.display = "block";
                document.getElementById("cancel_prompt").style.display = "none";
                document.getElementById("modal").style.display = "block";
                cancel_reservation.value = "已取消";
                cancel_reservation.style.backgroundColor = "lightgray";
                cancel_reservation.setAttribute("disabled", "disabled");
                reservation_delay.style.backgroundColor = "lightgray";
                reservation_delay.setAttribute("disabled", "disabled");
            }
        },
        error: function () {
            document.getElementById("prompt_comment").innerHTML = "取消预约失败";
            document.getElementById("modal").style.display = "block";
        }
    });
}

// 跳转至延期页面
function reservation_delay() {
    var reservation_no = $("#reservation_no").text();
    var openID = getUrlParam(window.location, "openID");
    window.location.href = "/wechat/customer_delay?reservation_no=" + reservation_no + "&openID=" + openID;
}

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
    //items=Replace(items," ","");
    return items;
}

// 获取订单的详细信息
function get_reservation_info() {
    var url = window.location.href;
    var reservation_no = getUrlParam(url, "reservation_no");
    $.ajax({
        type: 'POST',
        url: "/wechat/get_reservation_info",
        data: {reservation_no: reservation_no},
        dataType: "json",
        success: function (result) {
            if (result != "0") {
                $("#reservation_no").text(result.reservation_no);
                $("#reservation_company").text(result.company);
                $("#reservation_type").text(result.reservation_type);
                $("#reservation_datetime").text(result.reservation_datetime);
                $("#reservation_address").text(result.reservation_address);
                $("#reservation_car").text(result.reservation_car);
                var cancel_reservation = document.getElementById("cancel_reservation");
                var reservation_delay = document.getElementsByClassName("reservation_delay")[0];
                if (result.reservation_status == "已取消") {
                    cancel_reservation.value = "已取消";
                    cancel_reservation.style.backgroundColor = "lightgray";
                    cancel_reservation.setAttribute("disabled", "disabled");
                    reservation_delay.style.backgroundColor = "lightgray";
                    reservation_delay.setAttribute("disabled", "disabled");
                }
                if (result.reservation_status == "已变更") {
                    reservation_delay.value = "已变更";
                    reservation_delay.style.backgroundColor = "lightgray";
                    reservation_delay.setAttribute("disabled", "disabled");
                }
                if (result.reservation_status == "未确认") {
                    cancel_reservation.style.backgroundColor = "lightgray";
                    cancel_reservation.setAttribute("disabled", "disabled");
                    reservation_delay.style.backgroundColor = "lightgray";
                    reservation_delay.setAttribute("disabled", "disabled");
                }
            }
            else {
                document.getElementById("prompt_comment").innerHTML = "无该订单信息";
                document.getElementById("modal").style.display = "block";
            }
        },
        error: function () {
            document.getElementById("prompt_comment").innerHTML = "获取订单信息失败";
            document.getElementById("modal").style.display = "block";
        }
    })
}
setTimeout("get_reservation_info()", 100);