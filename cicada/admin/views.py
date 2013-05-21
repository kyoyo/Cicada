# Create your views here.
from django.http import HttpRequest,HttpResponse

def index(request):
	# print request.path
	# print request.get_host()
	# print request.get_full_path()
	# print request.is_secure()
	# print request.GET
	# for n in request.META:
		# print n
	# print request.META['REQUEST_METHOD']
	# print request.method
	# return HttpResponse('admin-admin')
	values = request.META.items()
	values.sort()
	html = []
	for k, v in values:
		html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
	return HttpResponse('<table>%s</table>' % '\n'.join(html))

def edit(request):
	return HttpResponse('edit')