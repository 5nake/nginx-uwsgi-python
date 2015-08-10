from jinja2 import Template, Environment, FileSystemLoader
from cgi import parse_qs, escape
import cgi
import re
import random
import string
import md5
import psycopg2

def application(environ, start_response):
	#env = Environment(loader=FileSystemLoader('/home/user/myapp/templates/'))
	#template = env.get_template('index.html')
	#TEMPLATES LOAD BLOCK
	main_page = Template(open('/home/user/myapp/templates/base.html').read())
	p1 = open('/home/user/myapp/templates/test/p1.html').read()
	article_id = int(open('/home/user/myapp/templates/test/test.html').read()) #temp for testing (id=2)
	contacts_page = open('/home/user/myapp/templates/contacts.html').read()
	page_404 = open('/home/user/myapp/templates/404.html').read()
	reg_page = open('/home/user/myapp/templates/reg.html').read()
	
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
		output = main_page.render(myblock=reg_page)
	elif re.match(r'/success/.*', uri):
		output = reg(environ, start_response)
	elif re.match(r'/auth/.*', uri):
		output = auth(environ, start_response)
	elif re.match(r'/partner/.*', uri):
		output = "Became a partner page"
	elif re.match(r'/test/.*', uri):
		output = test(environ, start_response)
	elif re.match(r'/contacts/.*', uri):
		output = main_page.render(myblock=contacts_page)
	elif uri == "/":
		output = main_page.render(myblock=p1)
	else:
		output = main_page.render(myblock=page_404)

	start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
	print(environ)
	return [ output.encode("utf-8") ]

def auth(environ, start_response):
	#DEF Block
	key = "Blast"
	session_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(32))
	client_agent = environ['HTTP_USER_AGENT'] + key
	ident_id = md5.new(client_agent).digest()
	#Parsing Block
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0
	request_body = environ['wsgi.input'].read(request_body_size)
	d = parse_qs(request_body)

	email = d.get('email', [''])[0]
	password = d.get('password', [''])[0]
	email = escape(email)
	password = escape(password)
	
	return "The input is: email:%s password:%s "%(email, password)


def reg(environ, start_response):
	#Psycopg open connect (PostgreSQL)	
	try:
		conn = psycopg2.connect("dbname=mydb user=postgres password=G898Q8QArma")
		conn.autocommit = True
	except:
		print "Cannot connect to db" 
	
	#Parsing Block
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0
	request_body = environ['wsgi.input'].read(request_body_size)
	d = parse_qs(request_body)
	
	name = d.get('name', [''])[0]
	email = d.get('email', [''])[0]
	password = d.get('password', [''])[0]
	name = escape(name)	
	email = escape(email)
	password = escape(password)
	
	#Psycopg block2 (PostgreSQL)
	cur = conn.cursor()
	cur.execute("SELECT name from users")
	users_db = cur.fetchall()
	for elem in users_db:
		if elem[0] == name:
			if conn:
				conn.close()
			return "name already exist"
	else:
		cur.execute("SELECT login from users")
		logins_db = cur.fetchall()
		for elem2 in logins_db:
			if elem2[0] == email:
				if conn:
					conn.close()
				return "email already exist"
		else:
			SQL = "INSERT INTO users (name, login, password) VALUES (%s, %s, %s);"
			data = (str(name), str(email), str(password), )
			cur.execute(SQL, data)
			if conn:
				conn.close()
				return "The input is: name:%s email:%s password:%s "%(name, email, password)
	
def test(environ, start_response):
	try:
		conn = psycopg2.connect("dbname=mydb user=postgres password=G898Q8QArma")
		conn.autocommit = True
	except:
		print "Cannot connect to db"
	cur = conn.cursor()
	cur.execute("SELECT name from users")
	a = cur.fetchall()
	for elem in a:
		print(elem[0])
	return "Hello"
	
