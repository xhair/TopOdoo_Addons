/**
 * Created by jiangxiang on 2016/3/14.
 */

//��ȡ���Ӵ�������openID����
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

var url = document.getElementById("url").innerText;
window.location.href = url;