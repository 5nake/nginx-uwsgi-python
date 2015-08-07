from jinja2 import Template, Environment, FileSystemLoader
import cgi
import re
import random
import string
import md5

def application(environ, start_response):
	#env = Environment(loader=FileSystemLoader('/home/user/myapp/templates/'))
	#template = env.get_template('index.html')
	#TEMPLATES BLOCK
	main_page = Template(open('/home/user/myapp/templates/base.html').read())
	p1 = open('/home/user/myapp/templates/test/p1.html').read()
	article_id = int(open('/home/user/myapp/templates/test/test.html').read()) #temp for testing (id=2)
	contacts_page = open('/home/user/myapp/templates/contacts.html').read()
	page_404 = open('/home/user/myapp/templates/404.html').read()
	
	#parsing uri like from http://127.0.0.1/?age=10&hobbies=software&hobbies=tunning
	#d = parse_qs(environ['QUERY_STRING'])
	#print (d)
	
	uri = environ['REQUEST_URI']
	print(uri)

	#Match (re.match()) objects are always True, and None if there's no match.
	#URI BLOCK
	if re.match(r'/article/%s/.*'%article_id, uri):
		output = "Article page (ID important)"
	elif re.match(r'/reg/.*', uri):
		output = "Registration page"
	elif re.match(r'/auth/.*', uri):
		output = auth(environ, start_response)
	elif re.match(r'/partner/.*', uri):
		output = "Became a partner page"
	elif re.match(r'/contacts/.*', uri):
		output = main_page.render(myblock=contacts_page)
	elif uri == "/":
		output = main_page.render(myblock=p1)
	else:
		output = main_page.render(myblock=page_404)

	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
	return [ output.encode("utf-8") ]

def auth(environ, start_response):
	key = "Blast"
	session_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(32))
	client_agent = environ['HTTP_USER_AGENT'] + key
	ident_id = md5.new(client_agent).digest()
	print(ident_id)
	return "Session_id is " + session_id
