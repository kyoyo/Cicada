#encoding:utf-8
from HTMLParser import HTMLParser

class XssClean(HTMLParser):
	"""过滤html代码中的标签和标签属性"""

	def __init__(self,valid_tags = {"a":["href","onclick"],"img":["src"]},strip = False):
		"""
			valid_tags dict 允许使用的标签,key为标签名，value为标签允许的属性
			strip bool 若标签被禁止，True会删除标签，False会实体化标签
		"""
		HTMLParser.__init__(self)
		self.valid_tags = valid_tags
		# 最终的结果
		self.clean_data = ''
		self.single_tags = ['img','br','hr','input','meta','link']

	def handle_starttag(self,tag,attrs):
		if self.valid_tags.has_key(tag):
			self.clean_data += '<'+tag+' '
			for key,value in attrs:
				if key in self.valid_tags[tag]:
					if key == 'href' and value.strip()[:10] =='javascript:':
						value = ''
					self.clean_data += key+'="'+value+'" '
			if tag in self.single_tags:
				self.clean_data += '/>'
			else:
				self.clean_data += '>'
		else:
			self.clean_data += '&lt;'+tag+'&gt;'

	def handle_data(self,data):
		self.clean_data += data

	def handle_endtag(self,tag):
		if self.valid_tags.has_key(tag):
			if tag not in self.single_tags:
				self.clean_data += '</'+tag+'>'
		else:
			if tag not in self.single_tags:
				self.clean_data += '&lt;/' + tag + '&gt;'

	# def getresult(self):
	# 	return self.data

#Useage

# if __name__=="__main__":
# 	string = '<a href="http://www.baidu.com" onclick="javascript:alert(1)"><i>baidu</i></a><img src="http://www.baidu.comm" onerror="alert(you error)" /><h2>This is a title!</h2>This is just a simple text'
# 	print string
# 	xss = XssClean()
# 	xss.feed(string)
# 	print xss.clean_data
#	# print xss.getresult()
# 	xss.close()