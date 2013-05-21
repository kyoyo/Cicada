#coding:utf-8
from django import forms

class ContactForm(forms.Form):
	subject = forms.CharField(error_messages={'required': '错误啦'})
	email = forms.EmailField(required=False, label='Your e-mail address')
	message = forms.CharField()

	def clean_email(self):
		email = self.cleaned_data['email']
		if email != 'user01@user01.com':
			raise forms.ValidationError("Email不是user01@user01.com")
		return email