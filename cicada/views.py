#encoding:utf-8
# sys lib
import json
import hashlib
import random

# django lib
from django.http import HttpRequest,HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from contrib.auth.decorators import login_required

from django.utils.html import strip_tags,escape
from django.conf import settings

# third lib
import markdown
import redis

# project lib
from cicada.models import *
from contrib.auth.models import User


redis_cache = redis.Redis(host='localhost', port=6379, db=0)

def error(msg = [],time = 3, url = ''):
	return render_to_response('error.html',{"msg":msg,"time":time,"url":url})

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
# 话题页面
def topic_page(request,tid):
	return HttpResponse(tid)

@login_required(login_url='/auth/login')
def answer_vote(request):
	""" 赞成/反对 回答 """

	result = {"success":False}
	if request.method == 'POST':
		from django.db.models import F
		answer_id = int(request.POST['answer_id'])
		rkey = 'cacida.answer-%d-agree-uid' % answer_id
		uid = request.user.id

		def cancel_agree():
			r = redis_cache.srem(rkey,uid)
			if r :
				affect_nums = Answer.objects.filter(id=answer_id).update(vote_yes = F('vote_yes')-1)

		# 赞成 -- 记录用户ID、更新数据库
		if request.POST['type'] == 'agree':
			r = redis_cache.sadd(rkey,uid)
			if r :
				affect_nums = Answer.objects.filter(id=answer_id).update(vote_yes = F('vote_yes')+1)
		# 取消赞成
		elif request.POST['type'] == 'cancel-agree':
			cancel_agree()
		# 反对 --- 如果已经赞同了，取消赞同
		elif request.POST['type'] == 'oppose':
			cancel_agree()
			affect_nums = Answer.objects.filter(id=answer_id).update(vote_no = F('vote_no')+1)

		# 取消反对
		elif request.POST['type'] == 'cancel-oppose':
			affect_nums = Answer.objects.filter(id=answer_id).update(vote_no = F('vote_no')-1)
		if affect_nums :
			result['success'] = True
	return HttpResponse(json.dumps(result))


@login_required(login_url='/auth/login')
def answer_save(request,qid):
	if request.method=='POST':
		answer = Answer()
		user = User()
		user.id =  request.user.id
		answer.user = user
		ques = Question()
		ques.id = qid
		answer.question = ques

		#去除xss，留下受信任的标签和属性
		content = request.POST['content'].strip()
		if len(content) < 10 :
			# return error(['回答内容至少需要10个字符!'])
			errmsg = {'content':{'msg':'回答内容至少需要10个字符!','value':content}}
			return question(request,qid,errmsg)
		import XssClean
		ser_tag = settings.VALID_TAGS
		xss = XssClean.XssClean(valid_tags = ser_tag)
		xss.feed(content)
		answer.content = xss.clean_data
		xss.close()
		answer.save()
		if answer.id:
			return HttpResponseRedirect('/question/'+qid)
	return HttpResponseRedirect('/question/'+qid)

# 问题信息页
def question(request,qid,errmsg = []):
	qinfo = Question.objects.getQuestionById(qid)
	qtopic = qinfo[0]._has_topic.all()
	answer = Answer.objects.filter(question = qid).all()
	# 查找 answer 的支持者
	for n in answer:
		rkey = 'cacida.answer-%d-agree-uid' % n.id
		uid = map(int,redis_cache.smembers(rkey))
		n.answers = User.objects.filter(id__in = uid).all()

	if not qinfo:
		return HttpResponseRedirect('/')
	return render_to_response('question.html',{"qinfo":qinfo[0],"qtopic":qtopic,"errmsg":errmsg,"answer":answer},context_instance=RequestContext(request))


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
	return HttpResponseRedirect('/')

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
		# handle_uploaded_file(request.FILES['avatar'],user)
		handle_uploaded_file(request.FILES['Filedata'],user)
		

	return render_to_response('profile.html',{"request":request})