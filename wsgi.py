from jinja2 import Template, Environment, FileSystemLoader
from cgi import parse_qs, escape
from Cookie import SimpleCookie
import Cookie
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
	
	uri = environ['REQUEST_URI']
	print(uri)

	#Match (re.match()) objects are always True, and None if there's no match.
	#URI BLOCK
	if re.match(r'/article/%s/.*'%article_id, uri):
		output = "Article page (ID important)"
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	elif re.match(r'/reg/', uri):
		if environ['REQUEST_URI'] == "/reg/reg/":
			output = reg(environ, start_response)
			start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
			print(environ)			
			return [ output.encode("utf-8") ]
		else:
			output = main_page.render(myblock=reg_page)
			start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
			print(environ)
			return [ output.encode("utf-8") ]
	elif re.match(r'/auth/.*', uri):
		out = auth(environ, start_response) #output + cookies in tuple!
		output = out[0]
		session_cookie = out[1]
		set_cookies = ('Set-Cookie', session_cookie)
		start_response('200 OK', [set_cookies, ('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	elif re.match(r'/partner/.*', uri):
		output = "Became a partner page"
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	elif re.match(r'/test/', uri):
		output = "TEST PAGE"
		set_cookies = ('Set-Cookie', "Cookieees")
		start_response('200 OK', [set_cookies, ('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		test(environ, start_response)
		print(environ)
		return [ output.encode("utf-8") ]
	elif re.match(r'/contacts/.*', uri):
		output = main_page.render(myblock=contacts_page)
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	elif uri == "/":
		output = main_page.render(myblock=p1)
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	else:
		output = main_page.render(myblock=page_404)
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]

def auth(environ, start_response):
	#Psycopg open connect (PostgreSQL)	
	try:
		conn = psycopg2.connect("dbname=mydb user=postgres password=G898Q8QArma")
		conn.autocommit = True
	except:
		print "Cannot connect to db"
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

	#Psycopg block2 (PostgreSQL)
	cur = conn.cursor()
	cur.execute("SELECT login from users")#emails
	users_emails = cur.fetchall()
	cur.execute("SELECT password from users")#emails
	users_passwords = cur.fetchall()
	for elem1 in users_emails:
		if elem1[0] == email:
			SQL_pass = "SELECT password from users WHERE login = %s;"
			data_pass = (str(email), )
			cur.execute(SQL_pass, data_pass)
			user_password = cur.fetchall() #Getting password which email input
			user_password = str(user_password[0][0])
			if user_password == password: #Checking right password
				SQL_email = "SELECT id from users WHERE login = %s;"
				data_email = (str(email), )
				cur.execute(SQL_email, data_email)
				user_id = cur.fetchall() #Getting user_id which email input. For string format use str(user_id[0][0])
				#INSERT SESSION DATA
				SQL_insert = "INSERT INTO sessions (user_id, session_id, ident_id) VALUES (%s, %s, %s);"
				ident = psycopg2.Binary(ident_id)
				data_insert = (str(user_id[0][0]), str(session_id), ident)
				cur.execute(SQL_insert, data_insert)

				session_cookie = "session_id=%s"%session_id
				return ("INSERT SESSION DATA", session_cookie)
			else:
				return "Wrong password!"
		else:
			return "Email doesn't exists!"
	conn.close() #Close Postgre Connection



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
	
	if name == "" or email == "" or password == "":
		return "Please fill all fields!"
	else:
		#Psycopg block2 (PostgreSQL)
		cur = conn.cursor()
		cur.execute("SELECT name from users")
		users_db = cur.fetchall()
		for elem in users_db:
			if elem[0] == name:
				if conn:
					conn.close()
				return "Name already exists!"
		else:
			cur.execute("SELECT login from users")
			logins_db = cur.fetchall()
			for elem2 in logins_db:
				if elem2[0] == email:
					if conn:
						conn.close()
					return "Email already exists!"
			else:
				SQL = "INSERT INTO users (name, login, password) VALUES (%s, %s, %s);"
				data = (str(name), str(email), str(password))
				cur.execute(SQL, data)
				if conn:
					conn.close()
					return "Registration successfull!"

def test(environ, start_response):
	cookie = SimpleCookie()
	cookie['likes'] = "cheese"
	# output the HTTP header
	print(cookie.output())
	
