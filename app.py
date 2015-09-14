from flask import make_response
from flask import abort
from flask import jsonify
from flask import Flask, Response,render_template
from flask import request,redirect
import json
import requests
from elasticsearch import Elasticsearch
from flask.ext.bcrypt import Bcrypt
from threading import Thread
from flask.ext.mail import Mail
from flask.ext.mail import Message

# email server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'deathping1994@gmail.com'
MAIL_PASSWORD = 'bastard007'

# administrator list
ADMINS = ['deathping1994@gmail.com']


app = Flask("projectbase")
bcrypt = Bcrypt(app)
mail = Mail(app)
from functools import wraps
# from flask.ext.pymongo import PyMongo
# mongo=PyMongo(app)

# @app.after_request
# def after_request(response):
#   response.headers.add('Access-Control-Allow-Origin', '*')
#   response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#   response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
#   return response
from flask.ext.pymongo import PyMongo
mongo = PyMongo(app)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

def checkpass(user,pas):
    com = mongo.db.users.find({'username': user})
    for combo in com:
        print type(combo['password'])
        if bcrypt.check_password_hash(combo['password'],pas) and user==combo['username']:
            return True
        else:
            return False
def check_status(user,authkey):
    com = mongo.db.users.find({'username': user})
    for combo in com:
        if bcrypt.check_password_hash(authkey,combo['username']+combo['password']) and user==combo['username']:
            return True
        else:
            return False


@app.route('/')
def index():
    if not check_status(request.cookies.get("user"),request.cookies.get("authkey")):
        stat=False
    else:
        stat=True
    return render_template('index.html',user=request.cookies.get("user"),status=stat),200
@app.route('/new_user',methods=['POST'])
def new_user():
    print request.form['pass']
    mongo.db.users.insert({'username': request.form['user'],'password': bcrypt.generate_password_hash(request.form['pass'])})
    return jsonify({"success":"true"}),200
@app.route('/logout')
def logout():
    resp = make_response(render_template('index.html',user="null",status=False),200)
    resp.set_cookie("user","",expires=0)
    resp.set_cookie("authkey","",expires=0)
    return resp
@app.route('/search')
def search():
    if not check_status(request.cookies.get("user"),request.cookies.get("authkey")):
        stat=False
    else:
        stat=True
    return render_template('index.html',user=request.cookies.get("user"),status=stat),200

@app.route('/login_action',methods=['POST'])
def login_action():
    if not request.form or not 'user' in request.form or not 'pass' in request.form:
        return render_template('login.html',user="",status=False),200
    else:
        if checkpass(request.form['user'],request.form['pass']):
            resp = make_response(render_template('index.html',user=request.form['user'],status=True),200)
            resp.set_cookie("user",request.form['user'])
            com = mongo.db.users.find({'username': request.form['user']})
            for combo in com:
                print request.form['user']
                print combo['password']
                resp.set_cookie("authkey",bcrypt.generate_password_hash(request.form['user'] + combo['password']))
            return resp
        else:
            abort(401)
@app.route('/login')
def login():
    if not check_status(request.cookies.get("user"),request.cookies.get("authkey")):
        return render_template('login.html',user="",status=False),200
    else:
        return render_template('index.html',user=request.cookies.get("user"),status=True),200
@app.route('/register')
def register():
    if 'user' in request.cookies:
        if not check_status(request.cookies.get("user"),request.cookies.get("authkey")):
            stat=False
        else:
            stat=True
    else:
        stat=False
    return render_template('register.html',user=request.cookies.get("user"),status=stat),200

@app.route('/approve')
def approve_project():
    if not check_status(request.cookies.get("user"),request.cookies.get("authkey")):
        return render_template('login',user="",status=False),200
    else:
        return render_template("dashboard.html",user=request.cookies.get("user"),status=True),200


@app.route('/base0/api/v1.0/projects', methods=['GET'])

def create_project():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if len(request.args.get("authkey",""))==0 or len(request.args.get("title",""))==0:
        abort(400)
    # for s in request.form['stu']:
    #   print s
    task = {
        'authkey': bcrypt.generate_password_hash(request.args.get("authkey","")),
        'title': request.args.get("title",""),
        'description': request.args.get("description",""),
        'mentor': request.args.get("mentor",""),
        'languages': request.args.get("lang",""),
        'students':request.args.get("students",""),
        'approved': False,
        }
    es.index(index='sw',doc_type='projects',body=task)
    return jsonify(task), 201

#@app.route('/base0/api/v1.0/projects/update', methods=['POST'])

# def update_project():
#   print (request.args.get("q"))
#   es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#   qbody={
#           "query" : {
#           "match" : {
#              "title" : request.args.get("q","")
#                       }
#                   }
#           }
#   re=es.search(index="sw",body=qbody)
#   re=re['hits']
#   return jsonify(re), 201

@app.route('/base0/api/v1.0/projects/action', methods=['POST'])
def ae_project():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    data=request.get_json(force=True)
    data_id=data['id']
    print data_id
    if data["action"]== "approve":
        for id in data_id:
            print id
            body={
            "doc" : {
            "approved" : True
                    }
            };
            es.update(index="sw",doc_type='projects',id=id,body=body);
    else:
        for id in data_id:
            body={
            "doc" : {
            "approved" : False
                    }
            };
            es.update(index="sw",doc_type='projects',id=id,body=body);
    return "success", 200


@app.route('/feedback', methods=['GET'])
def feedback():
    send_email("feedback:projectbase",MAIL_USERNAME,ADMINS[0],"testmessage","<b>gaurav</b>")
    return "sent",200

@app.route('/base0/api/v1.0/projects/list', methods=['GET'])

def list_project():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    qbody={
            "query" : {
            "match" : {
            "mentor" : request.cookies.get("user")
                    }
                        }
            }
    re=es.search(index="sw",body=qbody)
    re=re['hits']
    return jsonify(re), 200

@app.route('/base0/api/v1.0/projects/search', methods=['GET'])

def search_project():
    print (request.args.get("q"))
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if not len(request.args.get("q")):
        qbody={ "query":{
                "match_all": {}}}
    else:
        qbody={
            "query" : {
            "match" : {
            "title" : request.args.get("q","")
                        }
                    }
            }
    re=es.search(index="sw",body=qbody)
    re=re['hits']
    return jsonify(re), 200

if __name__ == '__main__':
    app.run(debug=True)