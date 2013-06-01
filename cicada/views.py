# encoding:utf-8
# sys lib
import json
import hashlib
import random
import time
import re

# django lib
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.utils.html import strip_tags, escape
from django.conf import settings

# third lib
import markdown
import redis

# project lib
from cicada.models import *
from contrib.auth.models import User

redis_cache = redis.Redis(host='localhost', port=6379, db=0)


def random_name(username=None):
    sauce = '!@#$%^&*()_+~Z'
    username = 'django_cicada' + str(random.randint(
        0, 1000)) if username == None else username
    stri = '%f %s %d)' % (time.time(), username, random.randint(0, 1000))
    sauce_s = sauce[random.randint(0, len(sauce) - 1)]
    filename = hashlib.md5(stri).hexdigest()[:10] + sauce_s
    return filename


def error(msg=[], time=3, url=''):
    return render_to_response('error.html', {"msg": msg, "time": time, "url": url})

# 用户id
# print request.session['_auth_user_id']
# request.session['username'] = request.user.username

# @login_required(login_url='/auth/login')


def index(request):
    return render_to_response('index.html', {"test": "test"}, context_instance=RequestContext(request))

# 用户注册


def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    from django.contrib.auth.forms import *
    form = UserCreationForm()
    if request.method == 'GET':
        return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
    if form.is_valid():
        new_user = form.save()
        return HttpResponseRedirect("/")
    return HttpResponse("请输入正确的信息！")


def topic_suggest(request):
    result = []
    data = Topic.objects.filter(
        topic_name__icontains=request.GET.get('term', '')).all()
    for n in data:
        result.append({"label": n.topic_name, "value": n.topic_name})

    return HttpResponse(json.dumps(result), content_type="application/json")
# 话题页面


def topic_page(request, tid):
    return HttpResponse(tid)

# 取得某个问题 回答的支持者(html)、支持者id


def get_answer_agree_list(answer_id):

    rkey = 'cacida.answer-%d-agree-uid' % answer_id
    html = ''
    ruid = redis_cache.zrevrange(rkey, 0, -1)

    uid = map(int, ruid)
    answers = User.objects.filter(id__in=uid).extra(
        select={'manual': 'FIELD(id,%s)' % ','.join(ruid)},
        order_by=['manual']).all()

    if answers:
        html += ('%d 票，来自<span class="voters">' % len(answers))
        for n in answers:
            html += '<a href="/profile/%d/">%s</a>、' % (
                n.id, n.nickname.encode('utf-8'))
        html = html.rstrip('、')
        html += '</span>'
    return html, uid


@login_required(login_url='/auth/login')
def answer_vote(request):
    """ 赞成/反对 回答 """
    result = {"success": False}
    if request.method == 'POST':
        from django.db.models import F
        answer_id = int(request.POST['answer_id'])
        rkey = 'cacida.answer-%d-agree-uid' % answer_id
        r_oppose_key = 'cacida.answer-%d-oppose-uid' % answer_id
        uid = request.user.id
        score = time.time()
        affect_nums = 0
        # 取消赞成

        def cancel_agree():
            global affect_nums
            r = redis_cache.zrem(rkey, uid)
            if r:
                affect_nums = Answer.objects.filter(
                    id=answer_id).update(vote_yes=F('vote_yes') - 1)
        # 取消反对

        def cancel_oppose():
            global affect_nums
            r = redis_cache.zrem(r_oppose_key, uid)
            if r:
                affect_nums = Answer.objects.filter(
                    id=answer_id).update(vote_no=F('vote_no') - 1)

        # 赞成 -- 记录用户ID、更新数据库
        if request.POST['type'] == 'agree':
            # 如果有反对，先取消反对
            cancel_oppose()
            r = redis_cache.zadd(rkey, uid, score)
            if r:
                affect_nums = Answer.objects.filter(
                    id=answer_id).update(vote_yes=F('vote_yes') + 1)
        # 取消赞成
        elif request.POST['type'] == 'cancel-agree':
            cancel_agree()
        # 反对 --- 如果已经赞同了，取消赞同
        elif request.POST['type'] == 'oppose':
            cancel_agree()
            r = redis_cache.zadd(r_oppose_key, uid, score)
            if r:
                affect_nums = Answer.objects.filter(
                    id=answer_id).update(vote_no=F('vote_no') + 1)
        # 取消反对
        elif request.POST['type'] == 'cancel-oppose':
            cancel_oppose()

        if affect_nums >= 0:
            result['voters'] = get_answer_agree_list(answer_id)[0]
            result['success'] = True

    return HttpResponse(json.dumps(result))


@login_required(login_url='/auth/login')
@csrf_exempt
def recorder_save(request):
    import os
    result = {"path": ''}
    record = request.body
    filename = random_name(request.user.username)
    wav = 'uploads/recorder/' + filename + '.wav'
    f = open(wav, 'w+')
    f.write(record)
    f.close()
    mp3 = 'uploads/recorder/' + filename + '.mp3'
    os.system("lame %s %s" % (wav, mp3))
    result['path'] = '/' + mp3
    return HttpResponse(json.dumps(result))
def at_user(content):
    regular = re.compile('(@.+?)(?=\s|？|、|！|，|。|：|\?|!|,|\.|$)')
    # (@.+?)(?=\s|？|、|！|，|。|：|\?|!|,|\.|$)
    r = regular.findall(content)
    uid = []
    def call_replace(m):
        name = m.group()
        try:
            u = User.objects.get(nickname = name[1:])
            url = '/profile/%d/' % u.id
            uid.append(u.id)
        except User.DoesNotExist:
            url = '#'
        return '<a href="%s">%s</a>' % (url,name)
    content = regular.sub(call_replace,content)
    # 返回替换后的内容和@到的用户ID
    return content,set(uid)

@login_required(login_url='/auth/login')
def answer_save(request, qid):
    if request.method == 'POST':
        answer = Answer()
        user = User()
        user.id = request.user.id
        answer.user = user
        ques = Question()
        ques.id = qid
        answer.question = ques

        # 去除xss，留下受信任的标签和属性
        content = request.POST['content'].strip()
        if len(strip_tags(content)) < 10:
            errmsg = {'content': {'msg': '回答内容至少需要10个字符!', 'value': content}}
            return question(request, qid, errmsg)
        from cicada.tool.XssClean import XssClean
        ser_tag = settings.VALID_TAGS
        xss = XssClean(valid_tags=ser_tag)
        xss.feed(content)
        answer.content = xss.clean_data
        # 为@到的用户替换超链接和写入到redis中，提醒谁@到了
        answer.content, at_uid = at_user(answer.content.encode('utf-8'))
        xss.close()
        answer.save()
        for uid in at_uid :
            at_user_key = 'cacida.answer-at-user-%d' % uid
            redis_cache.lpush(at_user_key,answer.id)
        if answer.id:
            return HttpResponseRedirect('/question/' + qid)
    return HttpResponseRedirect('/question/' + qid)

# 问题信息页


def question(request, qid, errmsg=[]):
    qinfo = Question.objects.getQuestionById(qid)
    if not qinfo:
        return HttpResponseRedirect('/')
    qtopic = qinfo[0]._has_topic.all()
    answer = Answer.objects.filter(question=qid).order_by('-vote_yes').all()
    user_id = request.user.id
    # 查找 answer 的支持者
    for n in answer:
        r_oppose_key = 'cacida.answer-%d-oppose-uid' % n.id
        oppose_uid = redis_cache.zrank(r_oppose_key, user_id)
        n.answers, agree_uid = get_answer_agree_list(n.id)
        if user_id in agree_uid:
            n.agree = True
        if oppose_uid != None:
            n.oppose = True
    return render_to_response('question.html', {"qinfo": qinfo[0], "qtopic": qtopic, "errmsg": errmsg, "answer": answer}, context_instance=RequestContext(request))


@login_required(login_url='/auth/login')
def question_save(request):
    result = {"islogin": True, "success": True, "errmsg": "", "valid": []}
    if request.method == 'POST':
        # 1.数据验证（去除Html标签）
        # 2.判断topic是否存在
        # 3.如果topic不存在则添加topic
        # 4.记录添加的topic的id
        # 5.添加问题到question
        ques = Question()
        ques.user_id = request.user.id
        ques.title = strip_tags(request.POST['title']).strip(u'？?') + u'？'
        ques.desc = markdown.markdown(strip_tags(request.POST['desc']))
        topic_l = strip_tags(request.POST['topic']).split(',')

        if len(ques.title) < 5:
            result['valid'].append(['title', '标题至少为5个字符！'])

        if topic_l == ['']:
            result['valid'].append(['topic', '请选择对应的话题再发表!'])

        # 如果验证信息有错误，则不添加topic
        if len(result['valid']):
            result['success'] = False
            return HttpResponse(json.dumps(result))

        # 添加topic，并且记录topic，id
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
        # 添加question的topic到中间表(多对多插入)
        for n in tobject:
            ques._has_topic.add(n)

        if ques.id:
            result['success'] = True
        return HttpResponse(json.dumps(result))
    return HttpResponseRedirect('/')


def handle_uploaded_file(f, user=''):
    filename = hashlib.md5('' + user + str(
        random.randint(0, 1000))).hexdigest()[:9]
    filename += '.jpg'
    with open('uploads/avatar/' + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

# -------个人中心


@login_required(login_url='/auth/login')
def profile(request, user):
    if user.strip() == '':
        user = request.user.username

    if request.method == 'POST':
        # handle_uploaded_file(request.FILES['avatar'],user)
        handle_uploaded_file(request.FILES['Filedata'], user)
    item = {"image": "/uploads/test.jpg"}
    return render_to_response('profile.html', {"request": request, "item": item})

def notify(request):
    result = {'at':False}
    uid = request.user.id
    at_rkey = 'cacida.answer-at-user-%d' % uid
    at_nums = redis_cache.llen(at_rkey)
    result['at'] = '%d 条新@，<a href="">查看@</a>' % at_nums
    return HttpResponse(json.dumps(result))