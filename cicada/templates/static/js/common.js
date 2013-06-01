$('input.search-input').focus(function(){
	if($(this).val()=='输入话题，问题……'){
		$(this).val('')
	}
})
$('input.search-input').blur(function(){
	if($(this).val()==''){
		$(this).val('输入话题，问题……')
	}
})
$('div.login-status').hover(function(){
	$(this).children('.account').addClass('active')
	$(this).children('.acc-func').fadeIn(120)
},function(){
	$(this).children('.account').removeClass('active')
	$(this).children('.acc-func').fadeOut(120)
})
$('a.show-cate').click(function(){
	if($('#subnav_bg').is(':visible')){
		$('#subnav_bg').slideUp(500)
	}else{
		$('#subnav_bg').slideDown(500)
	}
	return true
})
$('.post-ques').click(function(){
	$('.post-ques-dialog').modal()
	$('.post-ques-dialog').on('shown',function(){
		$('div.question-form .ques-title').focus()
	})
	return false;
});
$('#tags').tagsInput({
	"autocomplete_url":"/topic_suggest",
	"autocomplete":{"selectFirst":true,"width":"100px","autoFill":true},
	"height":"auto",
	"width":"510px",
	"defaultText":"搜索话题",
});
$('a.post-ques-cancel').click(function(){
	$('.post-ques-dialog').modal('hide')
	return false
})
$('a.post-ques-btn').click(function(){
	var title = $('div.question-form .ques-title').text(),
		desc = $('div.question-form .ques-desc').text(),
		topic = $('#tags').val();
	if(title==''){
		alert('请输入问题标题');
		return false;
	}
	if(topic==''){
		alert('请选择你要发表的话题');
		return false;
	}
	csrf = $('input[name=csrfmiddlewaretoken]').val()
	$.post('/question_save/',
		{"title":title,"desc":desc,"topic":topic,"csrfmiddlewaretoken":csrf},
		function(data){
			if(data.islogin==false){
				alert("请登录后操作!!!")
				return false
			}
			if(data.success){
				alert("发表问题成功。")
				$('.post-ques-dialog').modal("hide")
			}
		},"json"
	)
	return false
});
$('div.answer-list div.item').hover(function(){
	$(this).children('div.comment-bar').find('a.hide').fadeIn(200)
},function(){
	$(this).children('div.comment-bar').find('a.hide').fadeOut(200)
})
$(window).scroll(function(){
	if($('div.notify').is(':visible')){
		var notify_top = $(window).scrollTop();
		if(notify_top < 47){
			notify_top = 46
		}
		$('div.notify').stop()
		$('div.notify').animate({'top':notify_top+'px'},300)
	}
})
// 默认获取消息的间隔时间
var notify_timeout = 10000
$('div.notify a.close-notify').click(function(){
	$('div.notify').slideUp()
	notify_timeout = 600000
	return false;
});
var poll_notify = {
	poll: function(){
		$.ajax({
			url: "/poll", 
			type: "POST", 
			dataType: "json",
			data:{"csrfmiddlewaretoken":csrf_token},
			success: poll_notify.onSuccess,
			error: poll_notify.onError
		});
	},
	onSuccess: function(data, dataStatus){
		var show_notify = false
		try{
			if(data.at){
				show_notify = true
				$("div.notify div.notify-at").html(data.at+"<br>");
			}
			if(show_notify){
				$("div.notify").fadeIn(300,function(){
					$(window).scroll()
				})
			}else{
				$("div.notify").fadeOut(300)
			}
		}
		catch(e){
			poll_notify.onError();
			return;
		}
		interval = window.setTimeout(poll_notify.poll, notify_timeout);
	},
	onError: function(){
		console.log("Poll error;");
	}
};
setTimeout(poll_notify.poll,10000);