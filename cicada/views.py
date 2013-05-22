#encoding:utf-8
import json
import hashlib
import random

from django.http import HttpRequest,HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from contrib.auth.decorators import login_required

from django.utils.html import strip_tags,escape

import markdown

from cicada.models import *

# 用户id
# print request.session['_auth_user_id']
# request.session['username'] = request.user.username

@login_required(login_url='/auth/login')
def index(request):
	return render_to_response('index.html',{"test":"test","request":request})

#用户注册
def register(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/")

	from django.contrib.auth.forms import *
	form = UserCreationForm()
	if request.method == 'GET':
		return render_to_response('register.html',{'form':form},context_instance=RequestContext(request))
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
    	if form.is_valid():
        		new_user = form.save()
        		return HttpResponseRedirect("/")
        return HttpResponse("请输入正确的信息！")

def topic_suggest(request):
	result = []
	data = Topic.objects.filter(topic_name__icontains=request.GET.get('term','')).all()
	for n in data:
		result.append({"label":n.topic_name,"value":n.topic_name})

	return HttpResponse(json.dumps(result),content_type="application/json")

# 问题信息页
def question(request,qid):
	qinfo = Question.objects.getQuestionById(qid)
	if not qinfo:
		return HttpResponseRedirect('/')
	return render_to_response('question.html',{"qinfo":qinfo[0]})


@login_required(login_url='/auth/login')
def question_save(request):
	result = {"islogin":True,"success":True,"errmsg":"","valid":[]}
	if request.method == 'POST':
		# 1.数据验证（去除Html标签）
		# 2.判断topic是否存在
		# 3.如果topic不存在则添加topic
		# 4.记录添加的topic的id
		# 5.添加问题到question
		
		ques = Question()
		ques.user_id = request.user.id
		ques.title = strip_tags(request.POST['title']).strip('？?')+'？'
		ques.desc = markdown.markdown(strip_tags(request.POST['desc']))
		topic_l = strip_tags(request.POST['topic']).split(',')

		if len(ques.title) < 5:
			result['valid'].append(['title','标题至少为5个字符！'])

		if topic_l == ['']:
			result['valid'].append(['topic','请选择对应的话题再发表!'])

		#如果验证信息有错误，则不添加topic
		if len(result['valid']):
			result['success'] = False
			return HttpResponse(json.dumps(result))

		#添加topic，并且记录topic，id
		tobject = []
		tp = Topic()
		for t in topic_l:
			tinfo = Topic.objects.getTopic(t)
			if tinfo != None:
				tobject.append(tinfo)
			else:
				tp.topic_name = t
				tp.topic_category_id = 0
				tp.save()
				tobject.append(tp)
		ques.save()

		#添加question的topic到中间表(多对多插入)
		for n in tobject:
			ques._has_topic.add(n)

		if ques.id:
			result['success'] = True
		return HttpResponse(json.dumps(result))

def handle_uploaded_file(f,user=''):
	filename = hashlib.md5(''+user+str(random.randint(0,1000))).hexdigest()[:9]
	filename+='.jpg'
	with open('uploads/avatar/'+filename, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

# -------个人中心
@login_required(login_url='/auth/login')
def profile(request,user):
	if user.strip() == '':
		user = request.user.username

	if request.method == 'POST':
		print request.POST
		# print request.FILES.items()
		handle_uploaded_file(request.FILES['avatar'],user)

	return render_to_response('profile.html',{"request":request})