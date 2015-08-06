from jinja2 import Template, Environment, FileSystemLoader
from cgi import parse_qs, escape
import re

def application(environ, start_response):
	#env = Environment(loader=FileSystemLoader('/home/user/myapp/templates/'))
	#template = env.get_template('index.html')
	main_page = Template(open('/home/user/myapp/templates/base.html').read())
	p1 = open('/home/user/myapp/templates/test/p1.html').read()
	article_id = int(open('/home/user/myapp/templates/test/test.html').read()) #temp for testing (id=2)
	contacts_page = open('/home/user/myapp/templates/contacts.html').read()
	
	#parsing uri like from http://127.0.0.1/?age=10&hobbies=software&hobbies=tunning
	#d = parse_qs(environ['QUERY_STRING'])
	#print (d)
	
	uri = environ['REQUEST_URI']
	print(uri)

	#Match (re.match()) objects are always True, and None if there's no match.
	
	if re.match(r'/article/%s/.*'%article_id, uri):
		output = "Article page (ID important)"
	elif re.match(r'/reg/.*', uri):
		output = "Registration page"
	elif re.match(r'/partner/.*', uri):
		output = "Became a partner page"
	elif re.match(r'/contacts/.*', uri):
		output = main_page.render(block1=contacts_page)
	elif uri == "/":
		output = main_page.render(block1=p1)
	else:
		output = "404 page.html page"

	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
	return [ output.encode("utf-8") ]
