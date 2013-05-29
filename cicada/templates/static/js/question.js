$.extend(xheditor.settings,{shortcuts:{'ctrl+enter':function(){$('#commit-answer').submit()}}});
var editor = $('div.emit-editor textarea.html-editor').xheditor({tools:'Bold,Italic,Underline,|,Blockquote,Code,OrderedList,UnorderedList,|,Img,Media,Record,|,Removeformat,Fullscreen,Markdown',
	"width":"608px",
	"height":"143px",
	"sourceMode":false,
	"focus": checklogin,
	});
// }
function checklogin(){
	if(login==false){
		$('.login-dialog').modal()
	}
}

$('div.answer-total div.drop-menu').hover(function(){
	$(this).addClass('active')
},function(){
	$(this).removeClass('active')
})
$('div.item-vote a').click(function(){
	var aid = $(this).parents('div.item').attr('aid'),
		_this = $(this),
		_type = _this.attr('class'),
		v = _this.parent().siblings('div.item-vote-info');
	$.post('/answer_vote/',
		{"answer_id":aid,"type":_type,"csrfmiddlewaretoken":csrf_token},function(data){
			if(data.success){
				if(_type == 'agree'){
					_this.next().attr('class','oppose')
					_this.attr({'class':'cancel-agree','title':'取消赞同'})
				}else if(_type == 'cancel-agree'){
					v.children('.voters').remove(data.user+'、')
					_this.attr({'class':'agree','title':'赞同'})
					v.html(data.voters)
				}else if(_type == 'oppose'){
					_this.prev().attr('class','agree')
					_this.attr({'class':'cancel-oppose','title':'取消反对'})
				}else if(_type == 'cancel-oppose'){
					_this.attr({'class':'oppose','title':'反对,不会显示你的姓名'})
				}
				v.html(data.voters)
			}
		},"json")
	return false;
})
$.jRecorder({
		host : '/recorder_save/',
		'rec_top': '0px',
		'rec_left': '0px',
		callback_started_recording:function(){callback_started(); },
		callback_stopped_recording:function(){callback_stopped(); },
		callback_activityLevel:function(level){callback_activityLevel(level); },
		callback_activityTime:function(time){callback_activityTime(time); },

		callback_finished_sending:function(data){ callback_finished_sending(data) },
		swf_path : '/static/plugins/jRecorder/jRecorder2.swf',
});
$('div.record-btn a.start-recording').live('click',function(e){
	x =e.pageX-150+'px'
	y = e.pageY-220+'px'
	$('#flashrecarea').css({'top':y,'left':x})
	start_recorder()
	return false
})
function start_recorder(){
	$.jRecorder.record(130)
	return false;
}
function stop_recorder(){
	// $('#start').click(function(){
	// 	$.jRecorder.record(130)
	// 	return false;
	// })
	$.jRecorder.stop();
	$.jRecorder.sendData();
	return false;
}
function callback_activityLevel(level){
 	$('#level').html(level);
	if(level == -1){
	  $('#level').css("width",  "2px");
	}else{
	  $('#level').css("width", (level * 2)+ "px");
	}
}
function callback_started(){
	$('#status').html('Recording is started');
}
function callback_finished(){
	$('#status').html('Recording is finished');
}
function callback_activityTime(time){
	$('#time').html(time)
}
function callback_finished_sending(data){
	eval('data = '+data)
	editor.pasteHTML('<audio controls><source src="'+data.path+'" type="audio/mpeg">不支持</audio>')
	$('#status').html('File has been sent to server mentioned as host parameter');
}