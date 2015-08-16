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

key = "Blast"

def response(environ, start_response, output, status, cookie):
	headers = [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))]
	if cookie:
		set_cookies = ('Set-Cookie', cookie)
		headers.insert(0, set_cookies)
	start_response(status, headers)
	http_response = [ output.encode("utf-8") ]
	print(environ)
	return http_response

def application(environ, start_response):
	#DATABASE OPEN CONNECT	
	try:
		conn = psycopg2.connect("dbname=mydb user=postgres password=G898Q8QArma")
		conn.autocommit = True
		cur = conn.cursor()
	except:
		print "Cannot connect to db"

	name = check_auth(environ, start_response, cur) #Check auth
	uri = environ['REQUEST_URI']
	with open('/home/user/myapp/templates/base.html', 'r') as f:
		base_page = Template(f.read())
	with open('/home/user/myapp/templates/404.html') as f:
		page_404 = f.read()
	with open('/home/user/myapp/templates/test/test.html', 'r') as f:
		article_id = int(f.read()) #TEMP for testing (id=2)
	
	#URI BLOCK. Match (re.match()) objects are always True, and None if there's no match.
	status = "200 OK"
	cookie = False
	print(uri)
	if uri == "/":
		with open('/home/user/myapp/templates/test/p1.html', 'r') as f:
			p1 = f.read()
		output = base_page.render(myblock=p1, name=name)
	elif uri == '/reg/':
		with open('/home/user/myapp/templates/reg.html', 'r') as f:
			reg_page = f.read()
		output = base_page.render(myblock=reg_page, name=name)
	elif uri == '/reg/reg/':
		output = reg(environ, start_response, cur)
	elif uri == '/auth/':
		out = auth(environ, start_response, cur) #output + cookies in one tuple!
		output = out['output']
		session_cookie = out['cookie']
		if session_cookie:
			cookie=session_cookie
	elif uri == '/check/auth/':
		output = check_auth(environ, start_response, cur)	
	elif uri == '/logout/':
		output = logout(environ, start_response, cur)
	elif re.match(r'/article/\d', uri):
		article_response = article(environ, start_response, cur, uri)
		if article_response['output'] == '404 Not Found':
			output = base_page.render(myblock=page_404, name=name)
			status="404 Not Found"
		else:
			output = base_page.render(myblock=article_response['output'])
	elif uri == '/add/article/':
		with open('/home/user/myapp/templates/add_article.html', 'r') as f:
			add_article_page = f.read()
		output = base_page.render(myblock=add_article_page, name=name)
	elif uri == '/add/article/add/':
		output = add_article(environ, start_response, cur)
	elif re.match(r'/contacts/.*', uri):
		with open('/home/user/myapp/templates/contacts.html', 'r') as f:
			contacts_page = f.read()
		output = base_page.render(myblock=contacts_page, name=name)	
	else:
		output = base_page.render(myblock=page_404, name=name)
		status="404 Not Found"
	if cur is not None:
		cur.close()
		conn.close()
	return response(environ, start_response, output, status, cookie)

def auth(environ, start_response, cur):
	#DEF Block
	global key
	session_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(32))
	client_agent = environ['HTTP_USER_AGENT'] + key
	ident_id = md5.new(client_agent).hexdigest()
	ident = psycopg2.Binary(ident_id)
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
	SQL_SELECT = "SELECT id FROM users WHERE login = %s AND password = %s;"
	data_select = (str(email), str(password))
	cur.execute(SQL_SELECT, data_select)
	user_id = cur.fetchall()
	if user_id != []:
		#INSERT SESSION DATA
		SQL_insert = "INSERT INTO sessions (user_id, session_id, ident_id) VALUES (%s, %s, %s);"
		data_insert = (str(user_id[0][0]), str(session_id), ident)
		cur.execute(SQL_insert, data_insert)
		#INSERT COOKIES
		expires = time.time() + 30 * 24 * 3600
		session_expires = time.strftime("%a, %d-%b-%Y, %T GMT", time.gmtime(expires))
		session_cookie = "sessions=%s,%s; PATH=/; EXPIRES=%s"%(session_id, ident_id, session_expires)
		return {'output': "INSERT SESSION DATA", 'cookie': session_cookie}
	else:
		return {'output': "WRONG USER DATA!!", 'cookie': False}



def reg(environ, start_response, cur):
	#Form Parsing Block
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0
	request_body = environ['wsgi.input'].read(request_body_size)
	d = parse_qs(request_body)
	
	reg_name = d.get('reg_name', [''])[0]
	reg_email = d.get('reg_email', [''])[0]
	reg_password = d.get('reg_password', [''])[0]
	reg_name = escape(reg_name)	
	reg_email = escape(reg_email)
	reg_password = escape(reg_password)
	
	#SQL block
	if reg_name == "" or reg_email == "" or reg_password == "":
		return "Please fill all fields!"
	else:
		SQL_SELECT = "SELECT name, login from users WHERE name = %s AND login = %s;"
		data_select = (str(reg_name), str(reg_email))	
		cur.execute(SQL_SELECT, data_select)
		users_db = cur.fetchall()
		if users_db == []:
			SQL_INSERT = "INSERT INTO users (name, login, password) VALUES (%s, %s, %s);"
			data_insert = (str(reg_name), str(reg_email), str(reg_password))
			cur.execute(SQL_INSERT, data_insert)
			return "Registration successfull!"
		else:
			db_name = str(users_db[0][0])
			db_email = str(users_db[0][1])
			if db_name == reg_name:
				return "Name already exists!"
			elif db_email == reg_email:
				return "Email already exists!"

def check_auth(environ, start_response, cur):
	global key
	try:
		cookies = environ['HTTP_COOKIE']
	except:
		cookies = False
	
	if cookies == False:
		return False #NO COOKIE
	else:
		cookies_session = parse_qs(cookies)["sessions"]
		session_list = cookies_session[0].split(',')
		session_id_cookie = session_list[0] #Cookie session_id
		ident_id_cookie = session_list[1] #Cookie ident_id
		#Getting current Client Agent (MD5)
		client_agent_cur = environ['HTTP_USER_AGENT'] + key
		ident_id_cur = md5.new(client_agent_cur).hexdigest()
		#Check equals
		if ident_id_cookie == ident_id_cur:
			SQL_SELECT = "SELECT user_id, name from sessions INNER JOIN users ON users.id = sessions.user_id WHERE sessions.session_id = %s AND sessions.ident_id = %s;"
			data_select = (session_id_cookie, ident_id_cookie)
			cur.execute(SQL_SELECT, data_select)
			SQL_SELECT_DATA = cur.fetchall()
			if SQL_SELECT_DATA == []:
				return False
			else:			
				current_user_id = SQL_SELECT_DATA[0][0]
				current_user_name = SQL_SELECT_DATA[0][1]
				return current_user_name
		else:
			print("COOKIE ERROR")
			return False


def logout(environ, start_response, cur):
	#Parsing cookie (shall remove this block soon)
	try:
		cookies = environ['HTTP_COOKIE']
	except:
		cookies = False
		return "ERROR! ALREADY LOGOUT"
	if cookies == False:
		return False #NO COOKIE
	else:
		cookies_session = parse_qs(cookies)["sessions"]
		session_list = cookies_session[0].split(',')
		session_id_cookie = session_list[0] #Cookie session_id
		ident_id_cookie = session_list[1] #Cookie ident_id
		SQL_SELECT = "SELECT user_id from sessions WHERE session_id = %s AND ident_id = %s;"
		data_select = (session_id_cookie, ident_id_cookie)
		cur.execute(SQL_SELECT, data_select)
		user_id = cur.fetchall()
		print(user_id)
		user_id = user_id[0][0]
		cur.execute("DELETE FROM sessions WHERE user_id = %s;", (user_id, ))
		return "LOGOUT"

def article(environ, start_response, cur, uri):
	article_id = uri[9:]
	cur.execute("SELECT * from articles WHERE article_id = %s;", (article_id, ))
	article_db = cur.fetchall()
	if article_db == []:
		return {'output': '404 Not Found', 'status': "404 Not Found"}
	else:
		with open('/home/user/myapp/templates/article.html', 'r') as f:
			article_template = Template(f.read())
		article_author = article_db[0][1]	
		article_title = article_db[0][2]
		article_text = article_db[0][3]
		article_date = article_db[0][4]
		article_page = article_template.render(article_title = article_title, article_text = article_text, article_date = article_date, article_author = article_author)
		return {'output': article_page, 'status': '200 OK'}

def add_article(environ, start_response, cur):
	#Form Parsing Block
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0
	request_body = environ['wsgi.input'].read(request_body_size)
	d = parse_qs(request_body)
	article_author = d['article_author'][0]
	article_title = d['article_title'][0]
	article_text = d['article_text'][0]
	article_date = d['article_date'][0]
	SQL_INSERT = "INSERT INTO articles (user_name, article_title, article_text, article_date) VALUES (%s, %s, %s, %s);"
	data_insert = (article_author, article_title, article_text, article_date)
	cur.execute(SQL_INSERT, data_insert)
	return "OK"
