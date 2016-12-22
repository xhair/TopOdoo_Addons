/**
 * Created by jiangxiang on 2016/1/10.
 */
document.getElementById("verify").style.display = "none";
document.getElementById("verify_change_button").style.display = "none";
function change_info() {
    document.getElementById("exampleInputPassword1").removeAttribute("readonly");
    document.getElementById("change_button").style.display = "none";
    document.getElementById("verify").style.display = "block";
    document.getElementById("verify_change_button").style.display = "block";
}
// 确认更改信息
function sure() {
    var verify = document.getElementById("verify_value").value;
    var phone = document.getElementById("exampleInputPassword1").value;
    if (verify.length != 4) {
        alert("请输入正确的验证码");
        return false;
    }
    else if (phone.length != 11) {
        alert("请输入正确的手机号");
        return false;
    }
    else {
        document.getElementById("exampleInputPassword1").setAttribute("readonly", "readonly");
        document.getElementById("verify_value").value = "";
        document.getElementById("verify").style.display = "none";
        document.getElementById("change_button").style.display = "block";
        document.getElementById("verify_change_button").style.display = "none";
    }
}


function GetInf() {
    var code = $("#code0").val();//参数
    var xmlHttp;
    if (window.ActiveXObject) {
        xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    else if (window.XMLHttpRequest) {
        xmlHttp = new XMLHttpRequest();
    }
    xmlHttp.open("GET", "http://119.145.12.180/anta/Service/GetFlowcodeInfo?flowcode=" + code, true);
    var str = xmlHttp.responseText;//提取不出东西，为空
    var a = unescape(xmlHttp.responseText);//提取不出东西，为空
    xmlHttp.send(null);
}

//调用py文件中的方法
function change() {
    alert("h");

    //var code = $("#code0").val();//参数
    //var xmlHttp;
    //if (window.ActiveXObject) {
    //    xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
    //}
    //else if (window.XMLHttpRequest) {
    //    xmlHttp = new XMLHttpRequest();
    //}
    $.get('http://localhost:8069/wechat/hello?key1=1', function (result) {
        alert(result)
    })

    //xmlHttp.open("GET", "http://localhost:8069/wechat/hello", true);
    //var str = xmlHttp.responseText;//提取不出东西，为空
    //var a = unescape(xmlHttp.responseText);//提取不出东西，为空
    //alert(str);
    //xmlHttp.send(null);
    //var self = this;
    //var model = new instance.web.Model("wechat.partner");
    //model.call("my_method", [], {context: new instance.web.CompoundContext()}).then(function(result) {
    //        self.$el.append("<div>Hello " + result["hello"] + "</div>");
    //        // will show "Hello world" to the user
    //});
    //var myProject = new instance.web.Model("wechat.partner");
    //myProject.call("check", [element_ids, self.view.model, context]).then(function () {
    //     alert("展示");
    //})
    //instance.oepetstore.HomePage = instance.web.Widget.extend({
    //    start: function () {
    //        var self = this;
    //        var model = new instance.web.Model("wechat.partner");
    //        model.call("my_method", [], {context: new instance.web.CompoundContext()}).then(function (result) {
    //            self.$el.append("<div>Hello " + result["hello"] + "</div>");
    //            // will show "Hello world" to the user
    //        });
    //    },
    //});
}

