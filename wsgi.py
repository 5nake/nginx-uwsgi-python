from jinja2 import Template
from cgi import parse_qs, escape
from psycopg2 import extras
#import cgitb; cgitb.enable()
import json
import time
import cgi
import os
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
	
	#URI BLOCK. Match (re.match()) objects are always True, and None if there's no match.
	status = "200 OK"
	cookie = False
	content_type = 'text/html'
	print(uri)
	if uri == "/":
		output = base_page.render(myblock=main_page(environ, start_response, conn), name=name)
	elif re.match(r'/[?]page=\d{1,3}$', uri):
		d = parse_qs(environ['QUERY_STRING'])
		page = int(d['page'][0])
		output = base_page.render(myblock=main_page(environ, start_response, conn, page), name=name)
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
		article_response = article(environ, start_response, conn, uri, name)
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
	elif uri == '/showmore/comments/':
		output = show_more_comments(environ, start_response, conn)
	elif uri == '/delete/comment/':
		output = delete_comment(environ, start_response, cur)
	elif uri == '/add/image/add/':
		output = add_image(environ, start_response, cur)
	elif re.match(r'/file/upload/.*', uri):
		output = add_image(environ, start_response, cur)
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
	request_body_size = int(environ.get('CONTENT_LENGTH', 0))
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
		return {'output': {'status': 'ok'}, 'cookie': session_cookie}
	else:
		return {'output': {'status': 'error', 'error': 'WRONG USER DATA!'}, 'cookie': False}



def reg(environ, start_response, cur):
	#Form Parsing Block
	request_body_size = int(environ.get('CONTENT_LENGTH', 0))
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
		return json.dumps({'status': 'error', 'error': 'Please, fill all fields!'})
	else:
		if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", reg_email):
			return json.dumps({'status': 'error', 'error':'InValid Email!'})
		else:
			SQL_SELECT = "SELECT name, login from users WHERE name = %s OR login = %s;"
			data_select = (str(reg_name), str(reg_email))	
			cur.execute(SQL_SELECT, data_select)
			users_db = cur.fetchall()
			if users_db == []:
				SQL_INSERT = "INSERT INTO users (name, login, password) VALUES (%s, %s, %s);"
				data_insert = (str(reg_name), str(reg_email), str(reg_password))
				cur.execute(SQL_INSERT, data_insert)
				return json.dumps({'status': 'ok'})
			else:
				db_name = str(users_db[0][0])
				db_email = str(users_db[0][1])
				print(users_db)
				if db_name == reg_name:
					return json.dumps({'status': 'error', 'error':'Name already exists!'})
				elif db_email == reg_email:
					return json.dumps({'status': 'error', 'error':'Email already exists!'})

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

def article(environ, start_response, conn, uri, name):
	article_id = uri[9:]
	dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	dict_cur.execute("SELECT * from articles WHERE article_id=%s;", (article_id, ))
	article_db = dict_cur.fetchall()
	if article_db == []:
		return {'output': '404 Not Found', 'status': "404 Not Found"}
	else:
		with open('/home/user/myapp/templates/article.html', 'r') as f:
			article_template = Template(f.read())
		article_db = article_db[0]
		article_author = article_db['article_author']	
		article_title = article_db['article_title']
		article_text = article_db['article_text']
		article_text = escape_article_text(article_text) # def escape_article_text(text)
		article_date = article_db['article_date']
		dict_cur.execute("SELECT * from comments WHERE article_idc=%s ORDER BY comment_id DESC LIMIT 5;", (article_id, ))
		comments_db = dict_cur.fetchall()
		article_content = article_template.render(article_title = article_title, article_text = article_text, article_date = article_date, article_author = article_author, name=name, comments = comments_db)
		return {'output': article_content, 'status': '200 OK'}

def add_article(environ, start_response, cur, name):
	if name == "":
		return json.dumps({'status': 'error', 'error': 'unauthorized user!'})
	else:	
		#Form Parsing Block
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
		request_body = environ['wsgi.input'].read(request_body_size)
		d = parse_qs(request_body)
		print(d)
		if len(d) < 3:
			return json.dumps({'status': 'error', 'error': 'Please, fill all fields!'})
		else:
			article_author = name
			article_date = time.strftime("%Y-%m-%d %H:%M:%S")
			user_date = d['user_date'][0]
			article_title = d['article_title'][0]
			article_title = cgi.escape(article_title)
			article_text = d['article_text'][0]
			SQL_INSERT = "INSERT INTO articles (article_author, article_title, article_text, article_date) VALUES (%s, %s, %s, %s);"
			data_insert = (article_author, article_title, article_text, article_date)
			cur.execute(SQL_INSERT, data_insert)
			return json.dumps({'status': 'ok'})

def add_comment(environ, start_response, cur, name):
	if name == "":
		js_response = json.dumps({'status': 'error', 'error': 'unauthorized user!'})
		return js_response
	else:
		#Form Parsing Block
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
		request_body = environ['wsgi.input'].read(request_body_size)
		d = parse_qs(request_body)
		article_idc = d['location'][0]
		article_idc = article_idc[8:]
		comment_author = name
		comment_text = d['comment_text'][0]
		comment_text = cgi.escape(comment_text)
		comment_date = time.strftime("%Y-%m-%d %H:%M:%S")
		SQL_INSERT = "INSERT INTO comments (article_idc, comment_author, comment_text, comment_date) VALUES (%s, %s, %s, %s);"
		data_insert = (article_idc, comment_author, comment_text, comment_date)
		cur.execute(SQL_INSERT, data_insert)
		js_response = json.dumps({'status': 'ok', 'comment_author': comment_author, 'comment_text': comment_text, 'comment_date': comment_date})
		return js_response

def show_more_comments(environ, start_response, conn):
	request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	request_body = environ['wsgi.input'].read(request_body_size)
	d = parse_qs(request_body)
	article_idc = d['location'][0]
	article_idc = article_idc[8:]
	js_counter = int(d['counter'][0])

	dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	dict_cur.execute("SELECT * from comments WHERE article_idc=%s ORDER BY comment_id DESC LIMIT 6 OFFSET %s;", (article_idc, js_counter))
	dict_response = dict_cur.fetchall()
	if dict_response == []:
		js_response = json.dumps({'status': 'error', 'error': 'nothing to load'})
	else:
		for comment in dict_response:
			comment['comment_date'] = str(comment['comment_date'])
		if len(dict_response) == 5:
			js_response = json.dumps({'status': 'ok', 'data': 'last_data', 'response': dict_response})
		else:
			dict_response = dict_response[:5]
			js_response = json.dumps({'status': 'ok', 'response': dict_response})
	return js_response

def main_page(environ, start_response, conn, current_page=1):
	dict_cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)	
	dict_cur.execute("SELECT COUNT (*) FROM articles;")
	articles_count = dict_cur.fetchone()
	articles_count = articles_count['count']
	article_numbers = (current_page * 5) - 5
	if articles_count % 5 == 0:
		articles_pages = articles_count / 5
	else:
		articles_pages = (articles_count // 5) + 1
	pages = []
	for i in range(1, articles_pages + 1):
		pages.append(i)
	dict_cur.execute("SELECT * from articles ORDER BY article_id DESC LIMIT 5 OFFSET %s;", (article_numbers, ))
	dict_response = dict_cur.fetchall()
	with open('/home/user/myapp/templates/main.html', 'r') as f:
		main_template = Template(f.read())
	for text in dict_response:
		text['article_text'] = escape_article_text(text['article_text'][:400] + '...') # def escape_article_text(text)
	main_content = main_template.render(articles = dict_response, pages = pages, current_page=current_page)
	return main_content

def delete_comment(environ, start_response, cur):
	request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	request_body = environ['wsgi.input'].read(request_body_size)
	d = parse_qs(request_body)
	comment_id = d['comment_id'][0]
	cur.execute("DELETE FROM comments * WHERE comment_id = %s;", (comment_id, ))
	return "ok"

def add_image(environ, start_response, cur):
	cur.execute("INSERT INTO images VALUES(DEFAULT);")
	cur.execute("SELECT img_id FROM images ORDER BY img_id DESC LIMIT 1;")
	image_id = cur.fetchone()

	fs = cgi.FieldStorage(fp=environ['wsgi.input'],environ=environ)
	callback = fs['CKEditorFuncNum'].value
	http_path = "/img/img%s.jpg"%image_id
	image = fs['upload'].file
	save_image = bytearray(image.read())
	file = open("/home/user/myapp/static/img/img%s.jpg"%image_id, "wb")
	file.write(save_image)
	file.close()
	return "<script>window.parent.CKEDITOR.tools.callFunction(%s, '%s');</script>"%(callback, http_path)

def escape_article_text(text):
	ban_tags = re.findall(r'\<(?:script|html|iframe|a).*?\<\/(?:script|html|iframe|a)(?:\>|\s+[^>]*\>)', text) + re.findall(r'\<\/(?:script|html|div|form|body)(?:\>|\s+[^>]*\>)', text) + re.findall(r'onclick/i', text) # onclick unfinished
	for ban_tag in ban_tags:
		text = text.replace(ban_tag, '<span style="color:red; font-style:italic;">PROHIBITED TAG</span>')
	return text
