$(pageInit);
function submitForm(){
	alert(1)
}
function pageInit()
{
	$.extend(xheditor.settings,{shortcuts:{'ctrl+enter':submitForm}});
	$('div.emit-editor textarea.html-editor').xheditor({tools:'Bold,Italic,Underline,|,Blockquote,Code,OrderedList,UnorderedList,|,Img,Media,Record,|,Removeformat,Fullscreen',
		"width":"608px",
		"height":"143px"
		});
}
$('div.answer-total div.drop-menu').hover(function(){
	$(this).addClass('active')
},function(){
	$(this).removeClass('active')
})
$('div.answer-list a.agree').click(function(){
	var aid = $(this).parents('div.item').attr('aid'),
		_this = $(this);
	$.post('/answer_vote/',
		{"answer_id":aid,"type":"agree"},function(data){
			if(data.success){
				_this.attr({'class':'cancel-agree','title':'取消赞同'})
			}
		},"json")
	return false;
})