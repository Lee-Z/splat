function show_pic(idc_id) {
    // let msg_html = `<button src="${icon_url}" width="400px" />`
    // // $alert接收3个参数，data，title，options
    // // options使用案例可以参考https://element.eleme.cn/#/zh-CN/component/message-box#options
    // self.parent.app.$alert(msg_html, '这里是title', {
    //     dangerouslyUseHTMLString: true
    // })
    // var x = $('#a').val();
// var y = $('#b').val();
    alert(idc_id);
    $.post('/index')
    xmlHttp.send('{"name":idc_ip,"age":22}')
}
// show_pic = function (){
//     alert("点击了js");
// }