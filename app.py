from flask import make_response,render_template
from flask import abort
from flask import jsonify
from flask import Flask, Response
from flask import request,redirect
import json
import requests
from elasticsearch import Elasticsearch
from flask.ext.bcrypt import Bcrypt
from flask.ext.pymongo import PyMongo
from functools import wraps
app = Flask("projectbase")
bcrypt = Bcrypt(app)
mongo = PyMongo(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_status(request.cookies.get("user"),request.cookies.get("authkey")):
            return jsonify({"Error":"Login Required"}),401
        return f(*args, **kwargs)
    return decorated_function

def send_request(request_type,UserType,MemberCode,DATE1,Password):
    if(request_type == 'login'):
        with requests.Session() as c:
            c.get("https://webkiosk.jiit.ac.in/")
            params ={'x':'',
                'txtInst':'Institute',
                'InstCode':'JIIT',
                'txtuType':'Member Type',
                'UserType':UserType,
                'txtCode':'Enrollment No',
                'MemberCode':MemberCode,
                'DOB':'DOB',
                'DATE1':DATE1,
                'txtPin':'Password/Pin',
                'Password':Password,
                'BTNSubmit':'Submit'}
            cook=c.cookies['JSESSIONID']
            cooki=dict(JSESSIONID=cook)
            print cooki
    c.post("https://webkiosk.jiit.ac.in/CommonFiles/UserActionn.jsp", data=params,cookies=cooki)
    response=c.get("https://webkiosk.jiit.ac.in/StudentFiles/Academic/StudentAttendanceList.jsp")
    print response.content
    return response.content

def checkpass(user,pas,UserType,DATE1):
    MemberCode=user
    com = mongo.db.users.find({'username': user})
    for combo in com:
        print type(combo['password'])
        if bcrypt.check_password_hash(combo['password'],pas) and user==combo['username']:
            return True
        else:
            data=send_request("login",UserType,MemberCode,DATE1,pas)
            if user in data:
                mongo.db.users.insert({'username': user,'password': bcrypt.generate_password_hash(pas)})
                return True
            else:
                return False
    data=send_request("login",UserType,MemberCode,DATE1,pas)
    if user in data:
                mongo.db.users.insert({'username': user,'password': bcrypt.generate_password_hash(pas)})
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

@app.route('/logout')
@login_required
def logout():
    resp = make_response(render_template('index.html',user="null",status=False),200)
    resp.set_cookie("user","",expires=0)
    resp.set_cookie("authkey","",expires=0)
    return resp

@app.route('/login_action',methods=['POST'])
def login_action():
    if not request.form or not 'user' in request.form or not 'pass' in request.form:
        return jsonify({"Error":"Enter User name and password"}),403
    else:
        if checkpass(request.form['user'],request.form['pass'],request.form['UserType'],request.form['DATE1']):
            return jsonify({"success":"logged in","authkey":bcrypt.generate_password_hash(request.form['user'] + request.form['pass'])}),200
        else:
            return jsonify({"Error":"Incorrect Username Password"}),403

@app.route('/base0/api/v1.0/projects', methods=['GET'])
@login_required
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
@login_required
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