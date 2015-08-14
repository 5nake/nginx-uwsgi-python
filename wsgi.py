from jinja2 import Template, Environment, FileSystemLoader
from cgi import parse_qs, escape
import time
import Cookie
import cgi
import re
import random
import string
import md5
import psycopg2

def application(environ, start_response):
	name = check_auth(environ, start_response)
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
			output = main_page.render(myblock=reg_page, name=name)
			start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
			print(environ)
			return [ output.encode("utf-8") ]
	elif re.match(r'/auth/', uri):
		print(environ)
		out = auth(environ, start_response) #output + cookies in tuple!
		output = out[0]
		session_cookie = out[1]
		if session_cookie == False:
			start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
			return [ output.encode("utf-8") ]
		else:
			set_cookies = ('Set-Cookie', session_cookie)
			start_response('200 OK', [set_cookies, ('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
			return [ output.encode("utf-8") ]
	elif re.match(r'/check/auth/', uri):
		output = check_auth(environ, start_response)	
		print(environ)
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		return [ output.encode("utf-8") ]
	elif re.match(r'/logout/', uri):
		output = logout(environ, start_response)
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	elif re.match(r'/partner/.*', uri):
		output = "Became a partner page"
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	#elif re.match(r'/test/', uri):
		#output = "TEST PAGE"
		#print(environ)
		#return [ output.encode("utf-8") ]
	elif re.match(r'/contacts/.*', uri):
		output = main_page.render(myblock=contacts_page, name=name)
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	elif uri == "/":
		output = main_page.render(myblock=p1, name=name)
		start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))])
		print(environ)
		return [ output.encode("utf-8") ]
	else:
		output = main_page.render(myblock=page_404, name=name)
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
	ident_id = md5.new(client_agent).hexdigest()
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
	try:
		SQL_SELECT = "SELECT id FROM users WHERE login = %s AND password = %s;"
		data_select = (str(email), str(password))
		cur.execute(SQL_SELECT, data_select)
		user_id = cur.fetchall()
		#INSERT SESSION DATA
		SQL_insert = "INSERT INTO sessions (user_id, session_id, ident_id) VALUES (%s, %s, %s);"
		ident = psycopg2.Binary(ident_id)
		data_insert = (str(user_id[0][0]), str(session_id), ident)
		cur.execute(SQL_insert, data_insert)
		cur.close()
		conn.close() #Close Postgre Connection
		#INSERT COOKIES
		expires = time.time() + 30 * 24 * 3600
		session_expires = time.strftime("%a, %d-%b-%Y, %T GMT", time.gmtime(expires))
		session_cookie = "sessions=%s,%s; PATH=/; EXPIRES=%s"%(session_id, ident_id, session_expires)
		return ("INSERT SESSION DATA", session_cookie)
	except:
		return ("WRONG USER DATA!!", False)



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
				cur.close()
				conn.close()
				return "Name already exists!"
		else:
			cur.execute("SELECT login from users")
			logins_db = cur.fetchall()
			for elem2 in logins_db:
				if elem2[0] == email:
					cur.close()
					conn.close()
					return "Email already exists!"
			else:
				SQL = "INSERT INTO users (name, login, password) VALUES (%s, %s, %s);"
				data = (str(name), str(email), str(password))
				cur.execute(SQL, data)
				cur.close()
				conn.close()
				return "Registration successfull!"

def check_auth(environ, start_response):
	#Psycopg open connect (PostgreSQL)	
	try:
		conn = psycopg2.connect("dbname=mydb user=postgres password=G898Q8QArma")
		conn.autocommit = True
		cur = conn.cursor()
	except:
		print "Cannot connect to db"
	
	try:
		#Parsing cookie
		cookies = environ['HTTP_COOKIE']
		cookies_session = parse_qs(cookies)["sessions"]
		session_list = cookies_session[0].split(',')
		session_id_cookie = session_list[0] #Cookie session_id
		ident_id_cookie = session_list[1] #Cookie ident_id
		#Getting current Client Agent (MD5)
		key = "Blast"
		session_id_cur = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(32))
		client_agent_cur = environ['HTTP_USER_AGENT'] + key
		ident_id_cur = md5.new(client_agent_cur).hexdigest()
		#Check equals
		print (ident_id_cookie, ident_id_cur)
		if ident_id_cookie == ident_id_cur:
			SQL_id = "SELECT user_id from sessions WHERE session_id = %s AND ident_id = %s;"
			data_id = (session_id_cookie, ident_id_cookie)
			cur.execute(SQL_id, data_id)
			current_user_id = cur.fetchall()
			if current_user_id != 0 and current_user_id != None:
				SQL_name = "SELECT name from users WHERE id = %s;"
				data_name = (str(current_user_id[0][0]), )
				print(data_id)
				cur.execute(SQL_name, data_name)
				user_name = cur.fetchall()
				return str(user_name[0][0])
			else:
				print("DATABASE ERROR")
				return False
		else:
			print("COOKIE ERROR")
			return False
	except:
		return False #NO COOKIE


def logout(environ, start_response):
	#Psycopg open connect (PostgreSQL)	
	try:
		conn = psycopg2.connect("dbname=mydb user=postgres password=G898Q8QArma")
		conn.autocommit = True
		cur = conn.cursor()
	except:
		print "Cannot connect to db"
	
	#Parsing cookie (shall remove this block soon)
	try:
		cookies = environ['HTTP_COOKIE']
		cookies_session = parse_qs(cookies)["sessions"]
		session_list = cookies_session[0].split(',')
		session_id_cookie = session_list[0] #Cookie session_id
		ident_id_cookie = session_list[1] #Cookie ident_id
		SQL_SELEST = "SELECT user_id from sessions WHERE session_id = %s AND ident_id = %s;"
		data_select = (session_id_cookie, ident_id_cookie)
		cur.execute(SQL_SELEST, data_select)
		user_id = cur.fetchall()
		user_id = user_id[0][0]
		cur.execute("DELETE FROM sessions WHERE user_id = %s;", (user_id, ))
		return "LOGOUT USER_ID" + user_id
	except:
		return "ERROR! ALREADY LOGOUT"
	
