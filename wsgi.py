from jinja2 import Template, Environment, FileSystemLoader
from cgi import parse_qs, escape
from wsgiref.util import request_uri

def application(environ, start_response):
	#env = Environment(loader=FileSystemLoader('/home/user/myapp/templates/'))
	#template = env.get_template('index.html')
	html = open('/home/user/myapp/templates/base.html').read()
	template = Template(html)
	p1 = open('/home/user/myapp/templates/index/p1.html').read()
	output = template.render(block1=p1, block2=u'BLOCK2', block3=u'BLOCK3')
	
	#parsing like from http://127.0.0.1/?age=10&hobbies=software&hobbies=tunning
	#d = parse_qs(environ['QUERY_STRING'])
	#print (d)
	
	full_uri = request_uri(environ, include_query=1)
	print(full_uri)
	if full_uri == "http://localhost/" or full_uri == "http://127.0.0.1/":
		output = "Main Page"
	elif full_uri == "http://localhost/article/(?P<article_id>\d+)/$" or full_uri == "http://127.0.0.1/article/(?P<article_id>\d+)/$":
		output = "Article page (ID important)"
	elif full_uri == "http://localhost/reg/$" or full_uri == "http://127.0.0.1/reg/$":
		output = "Registration page"
	elif full_uri == "http://localhost/partner/$" or full_uri == "http://127.0.0.1/partner/$":
		output = "Became a partner page"
	elif full_uri == "http://localhost/contacts/$" or full_uri == "http://127.0.0.1/contacts/$":
		output = "Contacts page"
	else:
		output = "404 page.html page"

	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
	return [ output.encode("utf-8") ]
