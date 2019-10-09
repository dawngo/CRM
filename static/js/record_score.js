// 修改成绩事件
$('.score').change(function(){
    var sid=$(this).attr('sid') ;
    var val=$(this).val();
    $.ajax({
        url:'',
        type:'post',
        data:{
            sid:sid,
            val:val,
            action:'score',
            "csrfmiddlewaretoken":$("[name='csrfmiddlewaretoken']").val(),
        },
        success:function (data) {
            console.log(data)
        }
    })
});

// 修改评语事件
$('.note').blur(function(){
    var sid=$(this).attr('sid') ;
    var val=$(this).val();
    $.ajax({
        url:'',
        type:'post',
        data:{
            sid:sid,
            val:val,
            action:'homework_note',
            "csrfmiddlewaretoken":$("[name='csrfmiddlewaretoken']").val(),
        },
        success:function (data) {
            console.log(data)
        }
    })
});