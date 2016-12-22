/**
 * Created by jiangxiang on 2016/1/21.
 */

// 加载当前时间
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
document.getElementById("reservation_time").value = current_time;
document.getElementById("reservation_time").setAttribute("min", current_time);

//加载时获取预约项目信息
function get_reservation_type() {
    $.ajax({
        type: 'POST',
        url: "/wechat/get_reservation_type",
        data: "",
        dataType: "json",
        success: function (result) {
            if (result != 0) {
                var json_length = getJsonObjLength(result);
                var label_title = document.getElementsByClassName("label_title");
                var reservation_type = document.getElementsByClassName("reservation_type");
                for (var i = 0; i < json_length; i++) {
                    reservation_type[i].value = result[i].id;
                    label_title[i].innerHTML = result[i].name;
                }
                for (var i = 0; i < 6; i++) {
                    if (label_title[i].innerHTML == "" || label_title[i].innerHTML == null) {
                        document.getElementsByClassName("reservation_type_div")[i].style.display = "none";
                    }
                }
            }
            else {
                return false;
            }
        },
        error: function () {
            return false;
        }
    });
}
setTimeout("get_reservation_type()", 100);

// 根据不同公司展示不同的公司地址和时间段
function get_company_address() {
    var company_id = document.getElementById("company").value;
    var company_name = document.getElementById("company");
    var select_company = company_name.options[company_name.selectedIndex].text;
    $.ajax({
        type: 'POST',
        url: "/wechat/get_company_address",
        data: {company: company_id},
        success: function (result) {
            if (result != 0) {
                $("#service_address").val(result);
            }
            else {
                $("#service_address").val("无法获取地址信息");
            }
        },
        error: function () {
            return false;
        }
    });
    var time_slot = document.getElementsByClassName("time_slot");
    for (var i = 0; i < time_slot.length; i++) {
        time_slot[i].innerHTML = "";
    }
    $.ajax({
        type: 'POST',
        url: "/wechat/get_time_slot",
        data: {company: select_company},
        dataType: "json",
        success: function (result) {
            if (result != 0) {
                var json_length = getJsonObjLength(result);
                var reservation_time_scale = document.getElementById("reservation_time_scale");
                $("#reservation_time_scale").children('option').remove();
                for (var i = 0; i < json_length; i++) {
                    var option = document.createElement("option");
                    var option_text = document.createTextNode(result[i].name);
                    option.appendChild(option_text);
                    option.value = result[i].id;
                    reservation_time_scale.appendChild(option);
                }
            }
            else {
                return false;
            }
        },
        error: function () {
            return false;
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

// 页面加载时获取公司列表
function get_company_name() {
    $.ajax({
        type: 'POST',
        url: "/wechat/get_company_name",
        dataType: "json",
        success: function (result) {
            var json_length = getJsonObjLength(result);
            var company = document.getElementById("company");
            for (var i = 0; i < json_length; i++) {
                var option = document.createElement("option");
                var option_text = document.createTextNode(result[i].name);
                option.appendChild(option_text);
                option.value = result[i].id;
                company.appendChild(option);
            }
        },
        error: function () {
            return false;
        }
    });
}
setTimeout("get_company_name()", 100);

// 页面加载时获取车系列表
function get_car_type() {
    $.ajax({
        type: 'POST',
        url: "/wechat/get_car_type",
        dataType: "json",
        success: function (result) {
            var json_length = getJsonObjLength(result);
            var car_brand = document.getElementById("car_brand");
            for (var i = 0; i < json_length; i++) {
                var option = document.createElement("option");
                var option_text = document.createTextNode(result[i]);
                option.appendChild(option_text);
                car_brand.appendChild(option);
            }
        },
        error: function () {
            return false;
        }
    });
}
setTimeout("get_car_type()", 100);


//客户进行预约
//*param
//客户的openID:openID
//通过openID获取客户对象
//预约时间：reservation_time
//预约时间段：reservation_time_scale
//预约类型：reservation_type
function reservation() {
    var company_id = $("#company").val();
    var openID = getUrlParam(window.location, "openID");
    //var openID = "oEYmlty4tfoo6N4hp9NLd7Ms88x4";
    var reservation_time = $("#reservation_time").val();
    var reservation_time_scale = $("select[name='reservation_time_scale']").val();
    var reservation_type = $("input[name='reservation_type']:checked").val();
    var car_number = $("#car_number").val();
    var car_brand = $("#car_brand").val();
    if (company_id == null || openID == null || reservation_time == null || reservation_time_scale == null || reservation_type == null|| car_number == null|| car_brand == null) {
        document.getElementById("prompt_comment").innerHTML = "预约信息不完整";
        document.getElementById("modal").style.display = "block";
        return false;
    }

    $.ajax({
        type: 'POST',
        url: "/wechat/reservation",
        data: {
            openID: openID,
            reservation_time: reservation_time,
            reservation_time_scale: reservation_time_scale,
            reservation_type: reservation_type,
            company_id: company_id,
            car_number: car_number,
            car_brand: car_brand,
        },
        success: function (result) {
            if (result =="1") {
                document.getElementById("prompt_comment").innerHTML = "预约成功";
                document.getElementById("modal").style.display = "block";
                setTimeout("reservation_list()",1000);
            }
            else if(result =="0"){
                document.getElementById("prompt_comment").innerHTML = "预约失败";
                document.getElementById("modal").style.display = "block";
            }
            else if(result =="2"){
                document.getElementById("prompt_comment").innerHTML = "该时间段预约人数已满";
                document.getElementById("modal").style.display = "block";
            }
        },
        error: function () {
            document.getElementById("prompt_comment").innerHTML = "提交失败";
            document.getElementById("modal").style.display = "block";
        }
    });
}
//跳转至我的个人页面
function reservation_list(){
    var url = window.location;
    var openID = getUrlParam(url, "openID");
    window.location.href = "/wechat/reservation_list?openID="+openID;
}

//加载页面时获取客户车辆

function get_customer_car() {
    var url = window.location;
    var openID = getUrlParam(url, "openID");
    if (openID != null) {
        openID = openID.replace(/^\s*/, "");
    }
    $.ajax({
        type: 'POST',
        url: "/wechat/get_customer_car",
        data: {openID: openID},
        dataType: "json",
        success: function (result) {
            if (result != "0") {
                $("#car_number").val(result[0]);
                $("#car_brand").val(result[1]);
            }
            else {
                return false;
            }
        },
        error: function () {
            return false;
        }
    });
}
setTimeout("get_customer_car()", 100);




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

// 检查是否选取当前日期之前

function check_date(){
    var reservation_time = $("#reservation_time").val();
    if(current_time>reservation_time){
        $("#reservation_time").val(current_time);
        document.getElementById("prompt_comment").innerHTML = "预约时间小于当前时间";
        document.getElementById("modal").style.display = "block";
    }
    else{
        return false;
    }
}