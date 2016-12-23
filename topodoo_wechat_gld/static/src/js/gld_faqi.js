/**
 * Created by jiangxiang on 2016/6/1.
 */
//向下滑动时加载更多
document.addEventListener("touchend",function(){
    var height = document.body.scrollHeight; //总的高度
    var top = document.body.scrollTop;  //距离顶部的高度
    var screen_height = screen.height; // 屏幕的高度
    if(top+screen_height > height || top+screen_height == height){
        add_data();
    }
},false);
var number = 5;
var data_hint = 0;
function add_data(){
    if(data_hint==1){
        return false;
    }
    var userid = $("#user_id").val();
    var list_faqi_body_div = $("#list_faqi_body_div");
    list_faqi_body_div.append("<p style='text-align: center;margin-top: 5px;font-style: italic;font-size: 14px;color: #0079BF' id='hint'>正在加载...</p>");
    add_list("/WechatGLD/add_faqi_list", "#list_faqi_body_div", 1, userid);
}
function add_list(url, adrs, shuzi, userid) {
    $.ajax({
        type: 'POST',
        url: url,
        data: {userid: userid,number: number},
        dataType: "json",
        success: function (result) {
            var json_length = getJsonObjLength(result);
            if(json_length == 0){
                if(data_hint==1){
                    return false;
                }
                else if(data_hint==0){
                    var hint = document.getElementById("hint");
                    hint.innerHTML = "已经没有更多数据了";
                    data_hint++;
                    return false;
                }
            }
            number = number + 5;
            var list_faqi_body_div = document.getElementById("list_faqi_body_div");
            var hint = document.getElementById("hint");
            list_faqi_body_div.removeChild(hint);
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