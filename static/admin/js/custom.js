function show_pic(idc_id) {
 $.ajax({
    url: "/index",
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

