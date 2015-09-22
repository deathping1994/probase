import smtplib
from flask import jsonify
from flask import Flask
from flask import request
from flask.ext.cors import CORS,cross_origin
import requests
from elasticsearch import Elasticsearch
from flask.ext.bcrypt import Bcrypt
from flask.ext.pymongo import PyMongo
from functools import wraps
app = Flask("projectbase")
bcrypt = Bcrypt(app)
mongo = PyMongo(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json(force=True)
        if not check_status(data['authkey']):
            return jsonify(error="Login Required")
        return f(*args, **kwargs)
    return decorated_function


def check_status(authkey):
    if mongo.db.users.find_one({'authkey': authkey}):
        return True
    else:
        return False
#
# def verify_group(students,projecttype):
#     if len(students)!=0
#         query={'projecttype': projecttype ,"members": { $in: students[] }}
#         groups = mongo.db.groups.find(query)
#         if groups.size()==0:
#             return True
#         else
#             return False


@app.route('/check_group')
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
@login_required
def check_group():
    data=request.get_json(force=True)
    if len(data['members'])!=0:
        members=data['members']
        query={'projecttype': data['projecttype'] ,
               "members": { "$in": members }}
        groups = mongo.db.groups.find(query)
        if groups.size()==0:
            return jsonify(success="No Conflicting Groups found. Proceed to next step.",error="")
        else:
            return jsonify(error="Someone in your group is also a member in other group.",groups=groups)
    else:
        return jsonify(error="At least one member is required per project.")


@app.route('/feedback')
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def feedback():
    data=request.get_json(force=True)
    if data['msg']=="":
        return jsonify(error="Sorry, we Couldn't find you feedback. May be you missed something !"),200
    else:
        try:

            toaddrs = 'deathping1994@gmail.com'
            if data['from'] !="":
                fromaddr=data['from']
            else:
                fromaddr="deathping1994@gmail.com"
            mailserver = smtplib.SMTP("smtp.gmail.com:587")
            mailserver.starttls()
            mailserver.login(fromaddr,"bastard007")
            mailserver.sendmail(fromaddr,toaddrs,data['msg'])
            mailserver.quit()
            return jsonify(success="Your Feedback is Valuable to us and has been duly recorded, Thanks for your time !",error="")
        except Exception as err:
            print err
            mongo.db.log.insert({"error":str(err)})
            return jsonify(error="We are really sorry, something went wrong on our end. " +"/n"
                                 "Event has been reported and will soon be acted upon. Stay Tuned!"),200

@app.route('/')
def hello_world():
    return jsonify(success="It works!")


@app.route('/login_action', methods=['GET', 'POST'])
@cross_origin(origin='0.0.0.0', headers=['Content- Type', 'Authorization'])
def login_action():
    data = request.get_json(force=True)
    if data['user']== "" or data['pass']=="" or data['date1']=="":
        return jsonify(error="Enter User name and password")
    else:
        c = requests.Session()
        try:
            c.get("https://webkiosk.jiit.ac.in")
            params ={'x':'',
                'txtInst':'Institute',
                'InstCode':'JIIT',
                'txtuType':'Member Type',
                'UserType':data['usertype'],
                'txtCode':'Enrollment No',
                'MemberCode':data['user'],
                'DOB':'DOB',
                'DATE1':data['date1'],
                'txtPin':'Password/Pin',
                'Password':data['pass'],
                'BTNSubmit':'Submit'}
            cook=c.cookies['JSESSIONID']
            cooki=dict(JSESSIONID=cook)
            reslogin=c.post("https://webkiosk.jiit.ac.in/CommonFiles/UserActionn.jsp", data=params,cookies=cooki)
            if "Timeout" in reslogin.content:
                for i in(0,3):
                    c.get("https://webkiosk.jiit.ac.in/index.jsp")
                    params ={'x':'',
                        'txtInst':'Institute',
                        'InstCode':'JIIT',
                        'txtuType':'Member Type',
                        'UserType':data['usertype'],
                        'txtCode':'Enrollment No',
                        'MemberCode':data['user'],
                        'DOB':'DOB',
                        'DATE1':data['date1'],
                        'txtPin':'Password/Pin',
                        'Password':data['pass'],
                        'BTNSubmit':'Submit'}
                    cook=c.cookies['JSESSIONID']
                    cooki=dict(JSESSIONID=cook)
                    reslogin=c.post("https://webkiosk.jiit.ac.in/CommonFiles/UserActionn.jsp", data=params,cookies=cooki)
                    if "Locked" not in reslogin.content:
                        break
                    elif i==2:
                        raise requests.ConnectionError
                res=c.get("https://webkiosk.jiit.ac.in/StudentFiles/Academic/StudentAttendanceList.jsp")
                if data['user'] in res.content:
                    c.close()
                    authkey=bcrypt.generate_password_hash(data['user']+data['pass'])
                    mongo.db.users.insert({"user" : data['user'] , "authkey" : authkey})
                    return jsonify(error="",success="Succcessfully Logged in!",authkey=authkey)
                else:
                    print res.content
                    c.close()
                    return jsonify(error="Could Not Login,Invalid Details!")
            else:
                c.close()
                return jsonify(error="Account Locked. Contact ADMINISTRATOR.")
        except (requests.ConnectionError,requests.HTTPError) as error:
            print error
            return jsonify(error="Could Not Connect to Internet. Webkiosk May be Down or unreachable")


@app.route('/logout',methods=['GET', 'POST'])
@cross_origin(origin='0.0.0.0',headers=['Content- Type','Authorization'])
def logout():
    data = request.get_json(force=True)
    if not check_status(data['authkey']):
        return jsonify(error="Login Required")
    else:
        mongo.db.users.find_one_and_delete({"authkey":data['authkey']})
        return jsonify(success="Successfully Logged Off!")


@app.route('/status', methods=['GET', 'POST'])
@cross_origin(origin='0.0.0.0',headers=['Content- Type','Authorization'])
def temp():
    data=request.get_json(force=True)
    if check_status(data['authkey']):
        return jsonify(status="logged in")
    else:
        return jsonify(status="NOt logged in")


@app.route('/v1/project/create', methods=['GET','POST'])
# @login_required
def create_group():
    data=request.get_json(force=True)
    if data['title'] == "" or len(data['members'])==0:
        return jsonify(error="Incomplete Details provided")
    else:
        try:
            print "trying to insert in mongodb"
            res=mongo.db.groups.insert({"projecttype":data['projecttype'],"members":data['membersid']})
            print "Document inserted"
            print str(res)
            if str(res)!="NULL":
                task = {
                    'title': data['title'],
                    'description': data['description'],
                    'members': data['members'],
                    'projecttype': data['projecttype'],
                    'approved': False
                    }
                # es.index(index='projects', doc_type='projects', body=task)
                return jsonify(success="Group Successfully registered!")
            else:
                print "in else part"
                raise Exception
        except Exception as e:
            print e
            return jsonify(error="Oops ! Something Went wrong, Try Again")

@app.route('/v1/projects/update/<project_id>',methods=['POST','GET'])
def update_project():
    data=request.get_json(force=True)
    qbody={
          "query" : {
          "match" : {
             "title" : request.args.get("q","")
                      }
                  }
          }
    re=es.search(index="sw",body=qbody)
    re=re['hits']
    return jsonify(re), 201


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
    app.run(host="0.0.0.0")