// $(pageInit);
function submitForm(){
	$('#commit-answer').submit()
}

// function pageInit()
// {
	$.extend(xheditor.settings,{shortcuts:{'ctrl+enter':submitForm}});
	var editor = $('div.emit-editor textarea.html-editor').xheditor({tools:'Bold,Italic,Underline,|,Blockquote,Code,OrderedList,UnorderedList,|,Img,Media,Record,|,Removeformat,Fullscreen,Markdown',
		"width":"608px",
		"height":"143px",
		"sourceMode":false,
		"focus": checklogin,
		// "blur":function(){
		// 	alert(2)
		// }
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
		{"answer_id":aid,"type":_type},function(data){
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