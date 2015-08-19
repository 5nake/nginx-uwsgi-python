from jinja2 import Template, Environment, FileSystemLoader
from cgi import parse_qs, escape
from psycopg2 import extras
from pprint import pprint
import json
import time
import Cookie
import cgi
import re
import random
import string
import md5
import psycopg2

key = "Blast"

def response(environ, start_response, output, status, cookie, content_type):
	headers = [('Content-Type', '%s; charset=utf-8'%content_type), ('Content-Length', str(len(output)))]
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
<<<<<<< HEAD
=======
	with open('/home/user/myapp/templates/test/test.html', 'r') as f:
		article_id = int(f.read()) #TEMP for testing (id=2)
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab
	
	#URI BLOCK. Match (re.match()) objects are always True, and None if there's no match.
	status = "200 OK"
	cookie = False
	content_type = 'text/html'
	print(uri)
	if uri == "/":
<<<<<<< HEAD
		with open('/home/user/myapp/templates/p1.html', 'r') as f:
=======
		with open('/home/user/myapp/templates/test/p1.html', 'r') as f:
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab
			p1 = f.read()
		output = base_page.render(myblock=p1, name=name)
	elif uri == '/reg/':
		with open('/home/user/myapp/templates/reg.html', 'r') as f:
			reg_page = f.read()
		output = base_page.render(myblock=reg_page, name=name)
	elif uri == '/reg/reg/':
		output = reg(environ, start_response, cur)
		content_type = "application/json"
	elif uri == '/auth/':
		out = auth(environ, start_response, cur) #output + cookies in one tuple!
		output = out['output']
		output = json.dumps(output)
		content_type = "application/json"
		session_cookie = out['cookie']
		if session_cookie:
			cookie=session_cookie
	elif uri == '/check/auth/':
		output = check_auth(environ, start_response, cur)	
	elif uri == '/logout/':
		output = logout(environ, start_response, cur)
	elif re.match(r'/article/\d{1,4}$', uri):
		article_response = article(environ, start_response, cur, uri, name)
		if article_response['output'] == '404 Not Found':
			output = base_page.render(myblock=page_404, name=name)
			status="404 Not Found"
		else:
			output = base_page.render(myblock=article_response['output'], name=name)
	elif uri == '/add/article/':
		with open('/home/user/myapp/templates/add_article.html', 'r') as f:
			add_article_page = f.read()
		output = base_page.render(myblock=add_article_page, name=name)
	elif uri == '/add/article/add/':
		content_type = "application/json"
		output = add_article(environ, start_response, cur, name)
	elif uri == '/add/comment/add/':
		output = add_comment(environ, start_response, cur, name)
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
	return response(environ, start_response, output, status, cookie, content_type)

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
	email = cgi.escape(email)
	password = cgi.escape(password)
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
<<<<<<< HEAD
		return {'output': {'status': 'ok'}, 'cookie': session_cookie}
	else:
		return {'output': {'status': 'error', 'error': 'WRONG USER DATA!'}, 'cookie': False}
=======
		return {'output': "INSERT SESSION DATA", 'cookie': session_cookie}
	else:
		return {'output': "WRONG USER DATA!!", 'cookie': False}
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab



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
	reg_name = cgi.escape(reg_name)	
	reg_email = cgi.escape(reg_email)
	reg_password = cgi.escape(reg_password)
	#SQL block
	if reg_name == "" or reg_email == "" or reg_password == "":
<<<<<<< HEAD
		return json.dumps({'status': 'error', 'error': 'Please, fill all fields!'})
	else:
		if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", reg_email):
			return json.dumps({'status': 'error', 'error':'InValid Email!'})
		else:
			SQL_SELECT = "SELECT name, login from users WHERE name = %s OR login = %s;"
=======
		return json.dumps("Please fill all fields!")
	else:
		if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", reg_email):
			return json.dumps("InValid Email!")
		else:
			SQL_SELECT = "SELECT name, login from users WHERE name = %s AND login = %s;"
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab
			data_select = (str(reg_name), str(reg_email))	
			cur.execute(SQL_SELECT, data_select)
			users_db = cur.fetchall()
			if users_db == []:
				SQL_INSERT = "INSERT INTO users (name, login, password) VALUES (%s, %s, %s);"
				data_insert = (str(reg_name), str(reg_email), str(reg_password))
				cur.execute(SQL_INSERT, data_insert)
<<<<<<< HEAD
				return json.dumps({'status': 'ok'})
			else:
				db_name = str(users_db[0][0])
				db_email = str(users_db[0][1])
				print(users_db)
				if db_name == reg_name:
					return json.dumps({'status': 'error', 'error':'Name already exists!'})
				elif db_email == reg_email:
					return json.dumps({'status': 'error', 'error':'Email already exists!'})
=======
				return json.dumps("Registration successfull!")
			else:
				db_name = str(users_db[0][0])
				db_email = str(users_db[0][1])
				if db_name == reg_name:
					return json.dumps("Name already exists!")
				elif db_email == reg_email:
					return json.dumps("Email already exists!")
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab

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

def article(environ, start_response, cur, uri, name):
	article_id = uri[9:]

	conn = psycopg2.connect("dbname=mydb user=postgres password=G898Q8QArma")		
	dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	dict_cur.execute("SELECT * from articles WHERE article_id=%s;", (article_id, ))
	article_db = dict_cur.fetchall()
	article_db = article_db[0]
	if article_db == []:
		return {'output': '404 Not Found', 'status': "404 Not Found"}
	else:
		with open('/home/user/myapp/templates/article.html', 'r') as f:
			article_template = Template(f.read())
		article_author = article_db['article_author']	
		article_title = article_db['article_title']
		article_text = article_db['article_text']
		article_date = article_db['article_date']

		dict_cur.execute("SELECT * from comments WHERE article_idc=%s ORDER BY comment_id DESC;", (article_id, ))
		comments_db = dict_cur.fetchall()
		comments_db
		article_content = article_template.render(article_title = article_title, article_text = article_text, article_date = article_date, article_author = article_author, name=name, comments = comments_db)

		return {'output': article_content, 'status': '200 OK'}

def add_article(environ, start_response, cur, name):
	if name == "":
<<<<<<< HEAD
		return json.dumps({'status': 'error', 'error': 'unauthorized user!'})
=======
		return json.dumps("NONAME")
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab
	else:	
		#Form Parsing Block
		try:
			request_body_size = int(environ.get('CONTENT_LENGTH', 0))
		except (ValueError):
			request_body_size = 0
		request_body = environ['wsgi.input'].read(request_body_size)
		d = parse_qs(request_body)
		if len(d) < 3:
<<<<<<< HEAD
			return json.dumps({'status': 'error', 'error': 'Please, fill all fields!'})
=======
			return json.dumps("Please fill all fields!")
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab
		else:
			article_author = name
			article_date = time.strftime("%Y-%m-%d %H:%M:%S")
			user_date = d['user_date'][0]
			article_title = d['article_title'][0]
			article_title = cgi.escape(article_title)
			article_text = d['article_text'][0]
			article_text = cgi.escape(article_text)
			SQL_INSERT = "INSERT INTO articles (article_author, article_title, article_text, article_date) VALUES (%s, %s, %s, %s);"
			data_insert = (article_author, article_title, article_text, article_date)
			cur.execute(SQL_INSERT, data_insert)
<<<<<<< HEAD
			return json.dumps({'status': 'ok'})

def add_comment(environ, start_response, cur, name):
	if name == "":
		js_response = json.dumps({'status': 'error', 'error': 'unauthorized user!'})
=======
			return json.dumps("OK")

def add_comment(environ, start_response, cur, name):
	if name == "":
		js_response = json.dumps("NONAME")
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab
		return js_response
	else:
		#Form Parsing Block
		try:
			request_body_size = int(environ.get('CONTENT_LENGTH', 0))
		except (ValueError):
			request_body_size = 0
		request_body = environ['wsgi.input'].read(request_body_size)
		d = parse_qs(request_body)
		article_idc = d['location'][0]
		article_idc = article_idc[8:]
		comment_author = name
		comment_text = d['comment_text'][0]
		comment_date = time.strftime("%Y-%m-%d %H:%M:%S")
		SQL_INSERT = "INSERT INTO comments (article_idc, comment_author, comment_text, comment_date) VALUES (%s, %s, %s, %s);"
		data_insert = (article_idc, comment_author, comment_text, comment_date)
		cur.execute(SQL_INSERT, data_insert)
<<<<<<< HEAD
		js_response = json.dumps({'status': 'ok', 'comment_author': comment_author, 'comment_date': comment_date})
=======
		js_response = json.dumps({'comment_author': comment_author, 'comment_date': comment_date})
>>>>>>> 47ca6c2b3855790012c5e75d7a2427f648e08aab
		return js_response
