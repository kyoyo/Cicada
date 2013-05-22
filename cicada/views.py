#encoding:utf-8
import json

from django.http import HttpRequest,HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from cicada.models import *
# 用户id
# print request.session['_auth_user_id']
# request.session['username'] = request.user.username

def index(request):
	print request.META['REMOTE_ADDR']
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

def question_save(request):
	result = {"success":True,"error":""}
	if request.method == 'POST':

		# 1.数据验证（去除Html标签）
		# 2.判断topic是否存在
		# 3.如果topic不存在则添加topic
		# 4.记录添加的topic的id
		# 5.添加问题到question
		
		tp = Topic()
		tp.topic_name = request.POST['title']
		if Topic.objects.
		print request.POST
		return HttpResponse(json.dumps(result))