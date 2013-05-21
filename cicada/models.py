#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User

class Topic_category(models.Model):
	category_name = models.CharField(max_length=45)
	category_logo = models.CharField(max_length=145)

class TopicManager(models.Manager):

	def addTopic(self):
		self.save()
		return self.id

	def checkExist(self,name):
		return bool(self.filter(topic_name=name).count())

class Topic(models.Model):
	topic_name = models.CharField(max_length=45)
	logo = models.CharField(max_length=145)
	topic_category_id = models.IntegerField()
	
	objects = TopicManager()


class Question(models.Model):
	user_id = models.IntegerField()
	title = models.CharField(max_length=145)
	desc = models.CharField(max_length=500)
	created = models.DateTimeField(auto_now_add=True)
	_has_topic = models.ManyToManyField(Topic)