function show_pic(idc_id) {
 $.ajax({
    url: "/jsindex",
    data: JSON.stringify({    // JSON格式封装数据
        idc_id: idc_id,
        age: 77
    }),
    contentType: 'application/json',
    type: "POST",
    traditional: true,    // 需要传递列表、字典时加上这句
    success: function(result) {
    },
    fail: function(result) {
    }
});
    // alert(idc_id);
    // // $.post('/index')
    // return idc_id
}
function outgongw(outgong_id) {
    alert(outgong_id);
    // // $.post('/index')
    // return idc_id
}
function btn1(project_id) {
 $.ajax({
    url: "/system/aserviceIp/obtain/",
    data: JSON.stringify({    // JSON格式封装数据
        project_id: project_id,
    }),
    contentType: 'application/json',
    type: "POST",
    traditional: true,    // 需要传递列表、字典时加上这句
    success: function(result) {
    },
    fail: function(result) {
    }
});
}
function btn2(project_id) {
 $.ajax({
    url: "/system/aserviceIp/contrast/",
    data: JSON.stringify({    // JSON格式封装数据
        project_id: project_id,
    }),
    contentType: 'application/json',
    type: "POST",
    traditional: true,    // 需要传递列表、字典时加上这句
    success: function(result) {
    },
    fail: function(result) {
    }
});
}
