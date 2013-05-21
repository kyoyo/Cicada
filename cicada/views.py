# Create your views here.
from django.http import HttpRequest,HttpResponse
from django.shortcuts import render_to_response
import json
from cicada.models import *

def index(request):
	return render_to_response('index.html',{"test":"test"})

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
		print request.POST
		return HttpResponse(json.dumps(result))