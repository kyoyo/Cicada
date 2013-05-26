#encoding:utf-8
from django.db import models
from contrib.auth.models import User

class Topic_category(models.Model):
	category_name = models.CharField(max_length=45)
	category_logo = models.CharField(max_length=145)

class TopicManager(models.Manager):

	def getTopic(self,name):
		try:
			topic = self.filter(topic_name=name)[0]
		except Exception:
			topic = None
		return topic

class Topic(models.Model):
	topic_name = models.CharField(max_length=45)
	topic_desc = models.CharField(max_length=250,default='')
	logo = models.CharField(max_length=145)
	topic_category_id = models.IntegerField()
	
	objects = TopicManager()

class QuestionManager(models.Manager):

	def getQuestionById(self,qid):
		return self.filter(id = qid)

class Question(models.Model):
	user_id = models.IntegerField()
	title = models.CharField(max_length=145)
	desc = models.CharField(max_length=500)
	created = models.DateTimeField(auto_now_add=True)
	_has_topic = models.ManyToManyField(Topic)

	objects = QuestionManager()

class Answer(models.Model):
	content = models.TextField()
	user = models.ForeignKey(User, on_delete = models.DO_NOTHING)
	question = models.ForeignKey(Question)
	created = models.DateTimeField(auto_now_add=True)
	vote_yes = models.PositiveSmallIntegerField(default=0)
	vote_no = models.PositiveSmallIntegerField(default=0)
