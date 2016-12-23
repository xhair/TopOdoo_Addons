/**
 * Created by liujing on 2016/2/25
 */

//<script type="text/javascript" src="core-min.js.js"></script>
//<script src="base64.js.js"></script>


//setTimeout("get_temp_type()", 0);

function htmlEncode(value) {
    return $('<div/>').text(value).html();
}
//Html解码获取Html实体
function htmlDecode(value) {
    return $('<div/>').html(value).text();
}

function zs_mb() {
    //alert(1212)
    var temp = document.getElementById("temp_id");
    var option_text_temp = document.createTextNode("模板");
    var option_temp = document.createElement("option");
    option_temp.appendChild(option_text_temp);
    option_temp.value = 0;
    temp.appendChild(option_temp);
}

//展示模板类型
function get_temp_type() {
    //$("#temp_type_id").empty();
    var temp_type = document.getElementById("temp_type_id");
    var option_text_ = document.createTextNode("模板类型");
    var option_ = document.createElement("option");
    option_.appendChild(option_text_);
    option_.value = 0;
    temp_type.appendChild(option_);

    var temp = document.getElementById("temp_id");
    var option_text_temp = document.createTextNode("模板");
    var option_temp = document.createElement("option");
    option_temp.appendChild(option_text_temp);
    option_temp.value = 0;
    temp.appendChild(option_temp);

    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_temp_type",
        dataType: "json",
        success: function (result) {
            alert(12)
            var json_length = getJsonObjLength(result);
            for (var i = 0; i < json_length; i++) {
                var option_text = document.createTextNode(result[i].name);
                var option = document.createElement("option");
                option.appendChild(option_text);
                option.value = result[i].id;
                temp_type.appendChild(option);
            }
        },
        error: function () {
            alert('加载模板失败');
        }
    });
}

// 获得当前登录人的个人信息：图片 公司 部门 姓名
function get_user_image() {
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_user_image",
        data: {userid: $("#user_id").val()},
        dataType: "json",
        success: function (result) {
            $("#div_user").append("<div class='weui_panel_bd'>\
                <a href='javascript:void(0);' class='weui_media_box weui_media_appmsg'>\
                    <div class='weui_media_hd'>\
                     <img class='weui_media_appmsg_thumb' src='" + $(result).attr('image') + "'>\
                    </div>\
                    <div class='weui_media_bd'>\
                        <h4 class='weui_media_title'>" + $(result).attr('company_name') + "—" + $(result).attr('dept') + "</h4>\
                        <p class='weui_media_desc'>" + $(result).attr('name') + "</p>\
                    </div>\
                </a>\
            </div>");
        },
        error: function () {
            alert('操作失败');
        }
    });

    $('#text').wysiwyg();

}

//紧急程度
function get_Urgency() {
    var url = window.location;
    var emergency = getUrlParam(window.location, "emergency");//是否有紧急程度
    var content = getUrlParam(window.location, "text");//内容
    var select = document.getElementById("urgency_id");
    if (emergency == null) {
        var option_text_ = document.createTextNode("紧急程度");
        var option_ = document.createElement("option");
        option_.appendChild(option_text_);
        option_.value = 0;
        select.appendChild(option_);
        for (var i = 1; i <= 3; i++) {
            var option = document.createElement("option");
            var option_text;
            var option_value;
            if (i == 1) {
                option_text = document.createTextNode("一般");
                option_value = 'general'
                option.appendChild(option_text);
                option.value = option_value;
                select.appendChild(option);
            }
            if (i == 2) {
                option_text = document.createTextNode("急");
                option_value = 'anxious'
                option.appendChild(option_text);
                option.value = option_value;
                select.appendChild(option);
            }
            if (i == 3) {
                option_text = document.createTextNode("特急");
                option_value = 'urgent'
                option.appendChild(option_text);
                option.value = option_value;
                select.appendChild(option);
            }
        }
    }
    else {
        var jjcd_text;
        if (emergency == "general") {
            jjcd_text = "一般"
        }
        if (emergency == "anxious") {
            jjcd_text = "急"
        }
        if (emergency == "urgent") {
            jjcd_text = "特急"
        }
        var option_text_ = document.createTextNode(jjcd_text);
        var option_ = document.createElement("option");
        option_.appendChild(option_text_);
        option_.value = emergency;
        select.appendChild(option_);
        $("#urgency_id").val(emergency);
    }
    //if (emergency == null) {
    //    $("#urgency_id").val(emergency);
    //} else {
    //    $("#urgency_id").val(0);
    //}
    //get_approver();//先屏蔽
}


div_rows = 0;
//获取该员工的前五位审批人
function get_approver() {
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_approver",
        data: {user_id: $("#user_id").val()},
        dataType: "json",
        success: function (result) {
            $(result).each(function (i) {
                div_rows = i;
                var mobile_phone;
                ($(this).attr('mobile_phone') == '') ? mobile_phone = '暂无' : mobile_phone = $(this).attr('mobile_phone');
                $('#add_approver').append('<div class="add_approver_div_content" id="div_' + i + '">\
                                <div class="add_approver_span_duan left_">\
                                    <span style="display: none" id="id_' + i + '">' + $(this).attr('id') + '</span><span id="name_' + i + '">' + $(this).attr('name') + '</span>\
                                </div>\
                                <div class="personal_info ">\
                                    <p id="phone_' + i + '">' + mobile_phone + '</p>\
                                    <p>' + $(this).attr('company_name') + ' ' + $(this).attr('approver_dept') + '</p>\
                                </div>\
                                <div class="add_approver_span_tubiao " onclick="delete_row(this)">\
                                    <i class="weui_icon_clear"></i>\
                                </div>\
                            </div>');
            });
        },
        error: function () {
            alert('操作失败');
        }
    });
}

//删除一行
function delete_row(obj) {
    var tr = obj.parentNode;
    var tbody = tr.parentNode;
    tbody.removeChild(tr);
}

function qingchu() {
    var shuzi = $("#hangshu").text()
    $("#id_" + shuzi + "").text("")
    $("#name_" + shuzi + "").val("")
    $("#phone_" + shuzi + "").text("")
    $("#company_name_" + shuzi + "").text("")
    $("#dept_" + shuzi + "").text("")
}

// 根据输入的名称查询员工
function get_user_by_name(value) {
    $.ajax({
            type: 'POST',
            url: "/WechatGLD/get_user_by_name",
            data: {name: value.value},
            dataType: "json",
            success: function (result) {
                var mobile_phone;
                ($(result).attr('phone') == '') ? mobile_phone = '暂无' : mobile_phone = $(result).attr('phone');
                var shuzi = $("#hangshu").text()
                $("#id_" + shuzi + "").text($(result).attr("id") + ',')
                $("#name_" + shuzi + "").val($(result).attr("name"))
                $("#phone_" + shuzi + "").text(mobile_phone)
                $("#company_name_" + shuzi + "").text($(result).attr("company_name"))
                $("#dept_" + shuzi + "").text($(result).attr("dept"))
            },
            error: function () {
                alert('操作失败');
            }
        }
    );
}

//添加新行
function add_newrow() {
    var bool_state = true;
    $('.add_approver_div_content').each(function (i) {
        var id_text = $(this).find("div span:first-child").text();
        if (id_text != 'undefined') {
            bool_state = true;
        } else {
            bool_state = false;
        }
    });
    if (bool_state == true) {
        div_rows = div_rows + 1;
        $('#add_approver').append('<div class="add_approver_div_content" id="div_' + div_rows + '">\
                                <div class="add_approver_span_duan left_">\
                                   <span style="display: none;width:2px;" id="id_' + div_rows + '">' + $(this).attr('id') + '</span><input onblur="get_user_by_name(this)" type="text" id="name_' + div_rows + '" style="width: 60px;height:40px;text-align:center;margin-top:-10px" maxlength="3" >\
                                </div>\
                                <div class="personal_info">\
                                   <p id="phone_' + div_rows + '"></p> \
                                   <p><span id="company_name_' + div_rows + '"></span> <span id="dept_' + div_rows + '"></span></p> \
                                </div>\
                                <div class="add_approver_span_tubiao" onclick="delete_row(this)">\
                                    <i class="weui_icon_clear"></i>\
                                </div>\
                            </div>');
        $('#company_name_').append('<span id="dept_' + div_rows + '"></span>');
        $("#hangshu").text(div_rows)
    }
    else {
        $("#weui_toast_span").text("请填写空行")
        document.getElementById("weui_toast").style.display = "block";
        setTimeout("hiddenweui_toast()", 2000);
    }
}

//保存工联单
function save() {
    save_public('save')
}

//保存并提交审批
function save_and_submit() {
    save_public('save_and_submit')
}

// 保存/保存并提交审批公共方法
function save_public(function_name) {
    var attachment_id;
    if ($("#attachment_id").text() == "")
        attachment_id = 0
    else attachment_id = $("#attachment_id").text()

    if ($('.add_approver_div_content').length <= 0) {
        $("#weui_toast_span").text("请添加审批人")
        document.getElementById("weui_toast").style.display = "block";
        setTimeout("hiddenweui_toast()", 2000);
    } else if ($("#urgency_id").val() == 0) {
        $("#weui_toast_span").text("请选择紧急程度")
        document.getElementById("weui_toast").style.display = "block";
        setTimeout("hiddenweui_toast()", 2000);
    } else {
        var url = window.location;
        var template_type = $("#template_type_id").val();//模板类型
        var template = $("#template_id").val();//模板
        var title = $("#title_id").val();//标题
        var text = $("#text_id").val();//正文
        var urgency = $("#emergency_id").val();//紧急程度
        var userid = $("#user_id").val();//user_id
        var array = [];
        var j = 0;
        if (urgency == undefined) {
            urgency = $("#urgency_id").val();//获取当前输入的紧急程度
        }
        var bool_state = true;
        $('.add_approver_div_content').each(function (i) {
            var id_text = $(this).find("div span:first-child").text();
            if (id_text != 'undefined') {
                var index = id_text.indexOf(",");
                var id = id_text.substr(0, index)
                array[j] = id;
                j++;
            } else {
                bool_state = false;
            }
        });
        var approver_list = '' + array + '';
        $.ajax({
            type: 'POST',
            url: "/WechatGLD/" + function_name + "",
            data: {
                template_type: template_type,
                template: template,
                title: title,
                text: text,
                urgency: urgency,
                approver: approver_list,
                attachment_ids: attachment_id,
                userid: userid
            },
            dataType: "json",
            success: function (result) {
                if (result == "3") {
                    $("#weui_toast_span").text("审批人不允许是自己")
                    document.getElementById("weui_toast").style.display = "block";
                    setTimeout("hiddenweui_toast()", 2000);
                } else {
                    $("#weui_toast_span").text("保存提交成功")
                    document.getElementById("weui_toast").style.display = "block";
                    setTimeout("hiddenweui_toast()", 2000);
                    window.location.href = "/WechatGLD/list_faqi";
                }
            },
            error: function () {
                alert('操作失败');
            }
        });
    }
}

//根据模板类型编号获取模板
function get_temp(obj) {
    $("#temp_id").empty();
    if (obj.value && obj.value != 0) {
        $.ajax({
            type: 'POST',
            url: "/WechatGLD/get_temp",
            data: {temp_type_id: obj.value},
            dataType: "json",
            success: function (result) {
                var json_length = getJsonObjLength(result);
                var temp = document.getElementById("temp_id");
                for (var i = 0; i < json_length; i++) {
                    var option = document.createElement("option");
                    var option_text = document.createTextNode(result[i].name);
                    option.appendChild(option_text);
                    option.value = result[i].id;
                    temp.appendChild(option);
                }
                //根据模板展示标题和正文和紧急程度
                var template = $('#temp_id option:selected').val();//模板ID
                get_title(template, 1);//根据模板获取标题和正文和紧急程度
            },
            error: function () {
                alert('操作失败');
            }
        });
    } else {
        zs_mb()
    }
}

//根据模板获取标题和正文和紧急程度
function get_title(obj, id) {
    var canshu;
    if (id == 1) {
        canshu = obj;
    } else {
        canshu = obj.value;
    }
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_title",
        data: {temp_id: canshu},
        dataType: "json",
        success: function (result) {
            $("#title").val($(result).attr("subject"));
            var content = $(result).attr("content");
            content = htmlDecode(content);
            $("#text").html(content);

            $("#hide_emergency").val($(result).attr("emergency"));
        },
        error: function () {
            alert('操作失败');
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

//返回上一页
function goback() {
    history.go(-1);
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

var url = window.location.href;
// 跳转至工联单第二个页面（第一个页面的下一步按钮响应事件）
function next_gld() {
    var url = window.location;
    var template_type = $("#temp_type_id option:selected").val();//模板类型ID
    var template = $('#temp_id option:selected').val();//模板ID
    var title = $('#title').val();//标题
    var text = htmlEncode($('#text').val());//正文
    text = text.replace(/&nbsp;/g, '$$');
    var emergency = $('#hide_emergency').val();//紧急程度
    var userid = $('#user_id').val();//userid
    if (template_type && template && title && text && template_type != '模板类型' && template != '模板') {
        document.getElementById("loadingToast").style.display = "block";
        window.location.href = "/WechatGLD/get_add_gld_second_page?template_type="
            + template_type + '&template=' + template + '&title=' + title + '&text=' + text + '&emergency=' + emergency + '&userid=' + userid;
    }
    else {
        $("#weui_toast_span").text("请填写完整");
        document.getElementById("weui_toast").style.display = "block";
        setTimeout("hiddenweui_toast()", 2000);
    }
}

// 加载列表公用方法
function onload_list(url, adrs, shuzi, userid) {
    $.ajax({
        type: 'POST',
        url: url,
        data: {userid: userid},
        dataType: "json",
        success: function (result) {
            $(result).each(function (i) {
                div_rows = i;
                var state_view;
                var state;
                if ($(this).attr('state') == "draft") { //草稿
                    state_view = "caogao_anniu";
                    state = "草稿";
                }
                if ($(this).attr('state') == "cancel") {//作废
                    state_view = "zuofei_anniu";
                    state = "作废";
                }
                if ($(this).attr('state') == "pending") {//待审
                    state_view = "daishen_anniu";
                    state = "待审";
                }
                if ($(this).attr('state') == "pass") {//审批中
                    state_view = "shenpizhong_anniu";
                    state = "审批中";
                }
                if ($(this).attr('state') == "through") {//通过
                    state_view = "tongguo_anniu";
                    state = "通过";
                }
                if ($(this).attr('state') == "n_through") {//不通过
                    state_view = "butongguo_anniu";
                    state = "不通过";
                }
                var no = $(this).attr('name');
                var userid = $(this).attr('user_id');
                //($(this).attr('copy_users') == 'yes') ? shuzi = '1' : shuzi = shuzi
                $(adrs).append("<div>\
                    <div class='list_content' onclick='select_gld_info(\"" + no + "\"," + shuzi + "," + userid + ")'><div class='list_zuo_div'>\
                    <img class='aligncenter list_img_tuxiang' src='/web/binary/image?model=hr.employee&field=image&id=" + $(this).attr('id') + "&resize='/>\
                    </div>\
                    <div class='list_zhong_div'>\
                    <p class='list_p_shang'>\
                    " + $(this).attr('name') + "\
                    </p>\
                    <p class='list_p_zhong'>\
                    " + $(this).attr('dept') + "\
                    </p>\
                    <p class='list_p_xia'>\
                    " + $(this).attr('user_name') + "\
                    </p>\
                    </div>\
                    <div class='list_you_div_'>\
                    <button class=" + state_view + ">\
                    " + state + "\
                    </button>\
                    <p class='p_time'>\
                    " + $(this).attr('write_date') + "\
                    </p>\
                    </div>\
                    </div>\
                    <div class='div_daiban_shixian'></div>\
                    </div>");
            });
        },
        error: function () {
            alert('操作失败');
        }
    });
}

//我发起的工联单
function get_faqi_list() {
    var userid = $("#user_id").val()
    onload_list("/WechatGLD/get_faqi_list", "#list_faqi_body_div", 1, userid)
}

//待办工联单
function get_daiban_list() {
    var userid = $("#user_id").val();
    onload_list("/WechatGLD/get_daiban_list", "#list_daiban_body_div", 2, userid)
}

//已办工联单
function get_yiban_list() {
    var userid = $("#user_id").val()
    onload_list("/WechatGLD/get_yiban_list", "#list_yiban_body_div", 3, userid)
}

// 展开详情页面 进行所有审批操作
function select_gld_info(obj, qubie, userid) {
    window.location.href = "/WechatGLD/xiangqing?name=" + obj + '&qubie=' + qubie + '&userid=' + userid;
}

// 根据我的/待办/已办展开相对应的页面 我的1 展开 展开详情二级页面（审批意见的页面）
function view_opinion() {
    var qubie = $("#qubie").text();//1：我发起的/抄送人 2：待办  3：已办
    window.location.href = "/WechatGLD/select_opinion?name=" + $("#gldNO").text() + '&qubie=' + qubie;
}

// 展示附件页面
function view_enclosure() {
    var name = getUrlParam(window.location, "name");//工联单号
    window.location.href = "/WechatGLD/view_enclosure?name=" + $("#gldNO").text();
}

// 查看附件图片
function get_enclosure() {
    var name = getUrlParam(window.location, "name");//工联单号
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_enclosure",
        data: {name: name},
        dataType: "json",
        success: function (result) {
            $(result).each(function (i) {
                $("#select_enclosure_body_div").append("<div >\
                                <img src='file:///C:/Users/Administrator/AppData/Local/OpenERP S.A/Odoo/filestore/erp/b2/b2f436838b4663df11f394418c8f59563d081f68.jpg'>\
                            </div>")
            });

        },
        error: function () {
            alert('操作失败');
        }
    });
}

//获得当前工联单的所有审批意见的title (仅仅只获取title)
function get_opinion() {
    var name = getUrlParam(window.location, "name");//工联单号
    var shuzi = getUrlParam(window.location, "shuzi");//shuzi

    //$('#list_body_div_info_name').append("<img src='/topodoo_wechat_gld/static/src/img/fanhui.png'\
    //            class='aligncenter fanhui'  onclick='goback()'/><span class='gldNO' id='gldNO'>" + name + "</span>")
    //$('#list_body_div_info_name').append("<span class='aligncenter fanhui' ></span><span class='gldNO' id='gldNO'>" + name + "</span>")
    get_opinion_list(name, shuzi)
}
// 获得当前工联单的所有审批意见
function get_opinion_list(name, shuzi) {
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_opinion",
        data: {name: name, shuzi: shuzi},
        dataType: "json",
        success: function (result) {
            if (result != "2") {
                $(result).each(function (i) {
                    var opinion;
                    ($(this).attr('opinion') == '') ? opinion = '' : opinion = $(this).attr('opinion')
                    $("#select_opinion_div").append("<div class='weui_panel_bd'>\
                        <a href='javascript:void(0);' class='weui_media_box weui_media_appmsg'>\
                            <div class='weui_media_hd'>\
                                <img class='weui_media_appmsg_thumb' src='/web/binary/image?model=hr.employee&field=image&id=" + $(this).attr('id') + "&resize='>\
                            </div>\
                            <div class='weui_media_bd'>\
                                <h4 class='weui_media_title'>" + $(this).attr('name') + '(' + $(this).attr('dept') + ')' + '—' + $(this).attr('company') + "</h4>\
                                <p class='weui_media_desc' >审批意见：" + opinion + "</p>\
                                <p class='weui_media_desc' >" + $(this).attr('time') + "</p>\
                            </div>\
                        </a>\
                    </div>\
                    <div class='div_xiangqing_shixian'></div>\
                    <div class='xiangqing_content'>\
                    </div>");
                });
            }
        },
        error: function () {
            alert('操作失败');
        }
    });
}


function quxiao() {
    document.getElementById("dialog1").style.display = "none";
    yc = 0;
}

// 保存审批意见 同意
var tongyi_;
function tongyi() {
    //$("#huaru_div").css({
    //        backgroundColor: "#F6F6F6",
    //        width: "70%",
    //        height: "100%",
    //        //marginLeft: "-30%",
    //    }
    //)
    //$("#huaru_div").animate({right: "100px"})
    //document.getElementById("huaru_div").style.display = "none";
    tongyi_ = 1;
    document.getElementById("dialog1").style.display = "block";
    $("#rukou").text("同意)")
    $("#huaru_div").css({
            backgroundColor: "#F6F6F6",
            width: "70%",
            height: "100%",
        }
    )
    $("#huaru_div").animate({left: '-70%'}, "slow");
    yc = 0
}

// 保存审批意见 不同意
function butongyi() {
    //$("#huaru_div").css({
    //        backgroundColor: "#F6F6F6",
    //        width: "70%",
    //        height: "100%",
    //        //marginLeft: "-30%",
    //    }
    //)
    //$("#huaru_div").animate({right: "100px"})
    //document.getElementById("huaru_div").style.display = "none";
    tongyi_ = 2;
    document.getElementById("dialog1").style.display = "block";
    $("#rukou").text("不同意)")
    $("#huaru_div").css({
            backgroundColor: "#F6F6F6",
            width: "70%",
            height: "100%",
        }
    )
    $("#huaru_div").animate({left: '-70%'}, "slow");
    yc = 0
}


var yc = 0
function huaru() {
    //$("#huaru_div").animate({left: "30%"})
    document.getElementById("operation").innerHTML = "取消处理";
    document.getElementById("operation").style.backgroundColor = "red";
    if (yc == 0) {
        $("#huaru_div").animate({left: '70%'}, "slow");
        yc = 1
    }
    else {
        $("#huaru_div").css({
                backgroundColor: "#F6F6F6",
                width: "70%",
                height: "100%",
            }
        )
        document.getElementById("operation").style.backgroundColor = " #0079BF";
        document.getElementById("operation").innerHTML = "马上处理";
        $("#huaru_div").animate({left: '-70%'}, "slow");
        yc = 0
    }
}

function ychrc() {
    //if (yc != 0) {
    //    $("#huaru_div").css({
    //            backgroundColor: "#F6F6F6",
    //            width: "70%",
    //            height: "100%",
    //        }
    //    )
    //    $("#huaru_div").animate({left: '-70%'}, "slow");
    //    yc = 0
    //}

}

//获得详情的数据
function get_gld_info() {
    var canshu = ''
    var name = getUrlParam(window.location, "name");//模板类型
    var qubie = getUrlParam(window.location, "qubie");//区别 1：我发起的  2：待办 3：已办
    $("#qubie").text(qubie)
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_gld_info",
        data: {name: name},
        dataType: "json",
        success: function (result) {
            canshu = "<button style='text-align:right;font-size: 16px;color: #0061c2;padding: 4px 6px;border: 0px;background-color: #0079BF;color: #ffffff;border-radius: 5px' onclick='huaru()' id='operation'>马上处理</button>";

            //if (qubie == "1") {//如果是我的/抄送人 那么审批意见按钮隐藏
            //    document.getElementById("daiban_appr").style.display = "none";  //待办按钮
            //    document.getElementById("chaosong_appr").style.display = "none";//抄送按钮
            //}
            //if (qubie == "2")//如果是我的/抄送人 那么编制人权限按钮隐藏
            //{
            //    document.getElementById("daiban_sponar").style.display = "none";//我发起的页面按钮
            //    document.getElementById("chaosong_appr").style.display = "none";//抄送按钮
            //}
            //if (qubie == "3")//如果是我的/抄送人 那么编制人权限按钮隐藏
            //{
            //    document.getElementById("daiban_sponar").style.display = "none";//我发起的页面按钮
            //    document.getElementById("daiban_appr").style.display = "none";//待办按钮
            //}
            canshu = "<button style='text-align:right;font-size: 16px;color: #0061c2;padding: 4px 6px;border: 0px;background-color: #0079BF;color: #ffffff;border-radius: 5px' onclick='huaru()' id='operation'>马上处理</button>";

            $("#list_body_div_info").append("<div class='weui_panel_bd' onclick='ychrc()'>\
                <a href='javascript:void(0);' class='weui_media_box weui_media_appmsg'>\
                    <div class='weui_media_hd'>\
                        <img class='weui_media_appmsg_thumb' src='/web/binary/image?model=hr.employee&field=image&id=" + $(result).attr('id') + "&resize='>\
                    </div>\
                    <div class='weui_media_bd'>\
                        <h4 class='weui_media_title'>" + $(result).attr('company_name') + "—" + $(result).attr('dept') + "</h4>\
                        <p>" + $(result).attr('user_name') + "</span></p>\
                        <p>" + $(result).attr('write_date') + "</p>\
                        <div style='top:50px;position:fixed;right: 5%;font-size: 18px;color: #0061c2'>" + canshu + "</div>\
                    </div>\
                </a>\
            </div>\
            <div class='div_xiangqing_shixian'></div>\
            <div class='xiangqing_content'  onclick='ychrc()'>\
            <p style='padding-bottom:7px;padding-top:7px;border-bottom: 1px solid lightgrey;margin-right: 3%'>" + $(result).attr("subject") + "</p>\
            <pre style='padding-bottom: 10px' class='pre'>" + $(result).attr("content") + "</pre>\
            <span class='gldNO' style='margin-left: 10%;display:none' id='gldNO'>" + $(result).attr('name') + "</span>\
            </div>");
            //<pre style='' class='pre'>" + $(result).attr("content").replace(/<p>/g, '\t').replace(/<\/p>/g, '').replace(/<br>/g, '\n') + "</pre>\
        },
        error: function () {
            alert('操作失败');
        }
    });
}


// 获得按钮进行操作流程
function caozuo_anniu() {
    var qubie = getUrlParam(window.location, "qubie");//区别 1：我发起的  2：待办 3：已办
    if (qubie == 3) {
        document.getElementById("daiban_appr").style.display = "none";
        document.getElementById("zf_div").style.display = "none";
    }
    if (qubie == 2) {
        document.getElementById("zf_div").style.display = "none";
    }
    if (qubie == 1) {
        document.getElementById("zf_div").style.display = "block";
    }
}

// 保存工联单意见
function save_opinion() {
    document.getElementById("dialog1").style.display = "none";
    document.getElementById("loadingToast").style.display = "block";
    var userid = getUrlParam(window.location, "userid");//userid
    var tongyi_context;
    if (tongyi_ == 1)tongyi_context = "同意";
    if (tongyi_ == 2)tongyi_context = "不同意";
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/save_opinion",
        data: {
            wechat_gldid: $("#gldNO").text(),
            opinion: $("#opinion_text").val(),
            check_state: tongyi_context,
            userid: userid,
        },
        dataType: "json",
        success: function (result) {
            if (result == "2") {
                document.getElementById("loadingToast").style.display = "none";
                $("#weui_toast_span").text("该工联单是草稿");
                document.getElementById("weui_toast").style.display = "block";
                //$("#weui_toast_span").text("该工联单是草稿");
                //document.getElementById("weui_toast").style.display = "block";
                setTimeout("hiddenweui_toast()", 2000);
            }
            if (result == "3") {
                document.getElementById("loadingToast").style.display = "none";
                $("#weui_toast_span").text("该工联单已经已完成");
                document.getElementById("weui_toast").style.display = "block";
                //$("#weui_toast_span").text("该工联单已经已完成");
                //document.getElementById("weui_toast").style.display = "block";
                setTimeout("hiddenweui_toast()", 2000);
            } else {
                document.getElementById("loadingToast").style.display = "none";
                document.getElementById("weui_toast").style.display = "block";
                $("#weui_toast_span").text("审批成功");
                //goback();
                window.location.href = "/WechatGLD/list_daiban";
            }
        },
        error: function () {
            alert('操作失败');
        }
    });
}

function hiddenweui_toast() {
    $("#weui_toast_span").text("")
    document.getElementById("weui_toast").style.display = "none";
}

//添加审批人 根据名称先查询出来
function get_user() {
    document.getElementById("loadingToast").style.display = "block";
    var value = $("#user_name").val();
    $.ajax({
            type: 'POST',
            url: "/WechatGLD/get_user_by_name",
            data: {name: value},
            dataType: "json",
            success: function (result) {
                if (result != "2") {
                    document.getElementById("loadingToast").style.display = "none";
                    $("#weui_panel_bd").html("");
                    $("#weui_panel_bd").append("<div class='weui_panel_bd'>\
                    <a href='javascript:void(0);' class='weui_media_box weui_media_appmsg'>\
                        <div class='weui_media_hd'>\
                            <img class='weui_media_appmsg_thumb' src='" + $(result).attr('image') + "'>\
                        </div>\
                        <div class='weui_media_bd'>\
                            <h4 class='weui_media_title'>" + $(result).attr('company_name') + "—" + $(result).attr('dept') + "</h4>\
                            <p class='weui_media_desc' style='width:75%;float: left;margin-top: 4px;'><span >" + $(result).attr('name') + "</span></p>\
                            <span class='weui_btn weui_btn_mini weui_btn_primary' style=';float: left;' onclick='save_appr(" + $(result).attr('id') + ")'>添加</span>\
                        </div>\
                    </a>\
                    </div>");
                }
                else {
                    document.getElementById("loadingToast").style.display = "none";
                    document.getElementById("dialog2").style.display = "block";
                }
            },
            error: function () {
                alert('操作失败');
            }
        }
    );
}
function close_dialog() {
    document.getElementById("dialog2").style.display = "none";
}
function add_approver() {

}
//查看抄送人页面
function select_appr_copy_user() {
    var no = $("#gldNO").text()
    window.location.href = "/WechatGLD/select_appr_copy_user?no=" + no;
}

//加载当前单据的所有抄送人
function get_copy_user() {
    var no = getUrlParam(window.location, "no");
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_copy_user",
        data: {wechat_gldid: no},
        dataType: "json",
        success: function (result) {
            $(result).each(function (i) {
                $('#add_appr_div').append("<div class='list_content_'>\
                        <div class='list_zuo_div_'>\
                                <img src=" + $(this).attr('image') + "\
                                 class='aligncenter list_img_tuxiang'/>\
                        </div>\
                        <div class='xiangqing_zhong_div'>\
                            <p class='xiangqing_p_shang'>\
                                " + $(this).attr('company_name') + "—" + $(this).attr('dept') + "\
                            </p>\
                            <p class='copu_user'>\
                                " + $(this).attr('name') + "—" + $(this).attr('job_name') + "\
                            </p>\
                        </div>\
                    </div>\
                    <div class='div_xiangqing_shixian'></div>\
                    ");
            })
        },
        error: function () {
            alert('操作失败');
        }
    });
}

//展示添加审批人和抄送人的页面
function view_appr(obj) {
    var no = $("#gldNO").text()
    var title_user;
    if (obj == 1) {
        title_user = "添加审批人"
    }
    else {
        title_user = "添加抄送人"
    }
    var userid = getUrlParam(window.location, "userid");
    window.location.href = "/WechatGLD/view_appr?no=" + no + '&name=' + title_user + '&userid=' + userid;
}


function get_title_user() {
    var name = getUrlParam(window.location, "name");
    $("#title_user").text(name)
}

//提交审批
function gld_state_sent() {
    document.getElementById("loadingToast").style.display = "block";
    var userid = getUrlParam(window.location, "userid");//userid
    $.ajax({
            type: 'POST',
            url: "/WechatGLD/gld_state_sent",
            data: {wechat_gldid: $("#gldNO").text(), userid: userid},
            dataType: "json",
            success: function (result) {
                if (result == "1") {
                    document.getElementById("loadingToast").style.display = "none";
                    $("#weui_toast_span").text("操作成功");
                    document.getElementById("weui_toast").style.display = "block";
                    window.location.href = "/WechatGLD/list_faqi";
                }
                else {
                    $("#huaru_div").css({
                            backgroundColor: "#F6F6F6",
                            width: "70%",
                            height: "100%",
                        }
                    )
                    $("#huaru_div").animate({left: '-70%'}, "slow");
                    yc = 0
                    $("#weui_toast_span").text("当前没有审批人")
                    document.getElementById("weui_toast").style.display = "block";
                }
            },
            error: function () {
                alert('操作失败');
            }
        }
    )
    ;
}

//通过按钮添加审批人
function save_appr(value) {
    var gldNO = getUrlParam(window.location, "no");//区别 1：我发起的  2：待办 3：已办
    var name = getUrlParam(window.location, "name");//区别 1：我发起的  2：待办 3：已办
    var userid = getUrlParam(window.location, "userid");//userid
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/add_approver_service",
        data: {wechat_gldid: gldNO, employee_id: value, name: name, userid: userid},
        dataType: "json",
        success: function (result) {
            if (result == 2) {
                document.getElementById("weui_toast").style.display = "block";
                $("#weui_toast_span").text("不能重复添加")
            }
            else if (result == 3) {
                document.getElementById("weui_toast").style.display = "block";
                $("#weui_toast_span").text("当前员工没有关联用户")
            }
            else {
                document.getElementById("weui_toast").style.display = "block";
                $("#weui_toast_span").text("添加成功")
            }
            setTimeout("hiddenweui_toast()", 2000);
        },
        error: function () {
            alert('操作失败');
        }
    });
}


//作废
function gld_state_cancel() {
    var userid = getUrlParam(window.location, "userid");//userid
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/gld_state_cancel",
        data: {wechat_gldid: $("#gldNO").text(), userid: userid},
        dataType: "json",
        success: function (result) {
            $("#weui_toast_span").text("操作成功！")
            document.getElementById("weui_toast").style.display = "block";
            setTimeout("hiddenweui_toast()", 2000);
            window.location.href = "/WechatGLD/list_faqi";
        },
        error: function () {
            alert('操作失败');
        }
    });
}


//已阅
function read_gld_service() {
    var userid = getUrlParam(window.location, "userid");//userid
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/read_gld_service",
        data: {wechat_gldid: $("#gldNO").text(), userid: userid},
        dataType: "json",
        success: function (result) {
            $("#weui_toast_span").text("已阅完成")
            document.getElementById("weui_toast").style.display = "block";
            setTimeout("hiddenweui_toast()", 2000);
            goback()
        },
        error: function () {
            alert('操作失败');
        }
    });
}

//置为草稿
function gld_state_draft() {
    //var userid = getUrlParam(window.location, "userid");//userid
    var userid = getUrlParam(window.location, "userid");//userid
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/gld_state_draft",
        data: {wechat_gldid: $("#gldNO").text(), userid: userid},
        dataType: "json",
        success: function (result) {
            if (result == "1") {
                $("#weui_toast_span").text("操作成功");
                document.getElementById("weui_toast").style.display = "block";
                setTimeout("hiddenweui_toast()", 2000);
                window.location.href = "/WechatGLD/list_faqi";
            } else {
                $("#weui_toast_span").text("待审状态才能追回。")
                document.getElementById("weui_toast").style.display = "block";
                setTimeout("hiddenweui_toast()", 2000);
            }
        },
        error: function () {
            alert('操作失败');
        }
    });
}

//继续审批
function gld_finish_to_pass() {
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/gld_finish_to_pass",
        data: {wechat_gldid: $("#gldNO").text()},
        dataType: "json",
        success: function (result) {
            if (result == "1") {
                $("#weui_toast_span").text("操作成功！")
                document.getElementById("weui_toast").style.display = "block";
                setTimeout("hiddenweui_toast()", 2000);
                window.location.href = "/WechatGLD/list_faqi";

            }
        },
        error: function () {
            alert('操作失败');
        }
    });
}

// 不在本人审批范围之内
function waiver() {
    document.getElementById("loadingToast").style.display = "block";
    var userid = getUrlParam(window.location, "userid");//userid
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/waiver",
        data: {wechat_gldid: $("#gldNO").text(), userid: userid},
        dataType: "json",
        success: function (result) {
            document.getElementById("loadingToast").style.display = "none";
            $("#weui_toast_span").text("操作成功!");
            document.getElementById("weui_toast").style.display = "block";
            setTimeout("hiddenweui_toast()", 2000);
            window.location.href = "/WechatGLD/list_daiban";
        },
        error: function () {
            //$("#weui_toast_span").text("操作失败，请重试!");
            //document.getElementById("weui_toast").style.display = "block";
            alert('操作失败');
        }
    });
}

//// 添加附件
//function add_enclosure() {
//    wx.chooseImage({
//        count: 1, // 默认9
//        sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
//        sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
//        success: function (res) {
//            var localIds = res.localIds; // 返回选定照片的本地ID列表，localId可以作为img标签的src属性显示图片
//        }
//    });
//}

//跳转到sns页面
function tiaozhuan_sns() {
    window.location.href = "/WechatGLD/get_sns_html?name=" + $("#gldNO").text();
}

//获得日志SNS数据
function get_sns() {
    var gld_name = getUrlParam(window.location, "name");//工联单号
    $.ajax({
        type: 'POST',
        url: "/WechatGLD/get_sns",
        data: {gld_name: gld_name},
        dataType: "json",
        success: function (result) {
            $(result).each(function (i) {

                //$('#div_sns').append("\
                //<div style='float: left;height: 35px;margin-left: 8px;margin-top: 5px;color: #0079BF'>\
                //" + $(this).attr('body') + "(" + $(this).attr('operator_time') + ")" + "</div>");

                $("#div_sns").append("<div style='margin-left: 3px;margin-right: 3px;margin-top: 6px;background-color: #EEEEEE;color: black;' class='weui_panel_bd'>\
                        <a href='javascript:void(0);' class='weui_media_box weui_media_appmsg'>\
                            <div class='weui_media_hd'>\
                                <img class='weui_media_appmsg_thumb' src='/web/binary/image?model=hr.employee&field=image&id=" + $(this).attr('id') + "&resize='>\
                            </div>\
                            <div class='weui_media_bd'>\
                                <h4 class='weui_media_title'>" + $(this).attr('name') + '<' + $(this).attr('email') + '>' + "</h4>\
                                <p class='weui_media_desc' >" + $(this).attr('body') + "</p>\
                                <p class='weui_media_desc' >" + $(this).attr('time') + " 已更新新的文档</p>\
                            </div>\
                        </a>\
                    </div>\
                    </div>");
            })

        },
        error: function () {
            alert('操作失败');

        }
    });
}