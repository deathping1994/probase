import smtplib
from datetime import datetime
from flask import jsonify
from flask import Flask
from flask import request
from flask.ext.cors import CORS,cross_origin
import requests
from elasticsearch import Elasticsearch
from flask.ext.bcrypt import Bcrypt
from flask.ext.pymongo import PyMongo
from functools import wraps
from bs4 import BeautifulSoup
from bson.json_util import dumps
app = Flask("projectbase")
bcrypt = Bcrypt(app)
mongo = PyMongo(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

def adminlogin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json(force=True)
        if not check_status(data['authkey'],'E'):
            return jsonify(error="Teachers Login Required! This Event Will Be Reported.")
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json(force=True)
        if not check_status(data['authkey'],data['usertype']):
            return jsonify(error="Login Required")
        return f(*args, **kwargs)
    return decorated_function


def check_status(authkey, usertype):
    res= mongo.db.users.find_and_modify({'authkey': authkey,'usertype': usertype},{"$set":{"loggedat":datetime.utcnow()}})
    print res

    if res is not None:
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


def currentuser(authkey,usertype):
    curruser=mongo.db.users.find_one({'authkey': authkey,'usertype': usertype})
    if curruser is not None:
        return curruser['user']
    else:
        return "NULL"


@app.route('/projects/<user>',methods=['GET','POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def list_projects(user):
    try:
        if len(user)!=0:
            members=[user]
            query={"members": { "$in": members }}
            groups = mongo.db.groups.find(query,{"_id": 1})

            if groups.count()==0:
                return jsonify(success="You don't have any projects.",error=""),200
            else:
                print "insid"
                groupid=[]
                for group in groups:
                    id=str(group['_id'])
                    groupid.append(id)
                return jsonify(sccesss="Found projects",groupid=groupid),200
        else:
            return jsonify(error="No user specified"),500
    except Exception :
        jsonify(error="OOps ! Something went wrong."),500


@app.route('/feedback',methods=["POST","GET"])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
@login_required
def feedback():
    data=request.get_json(force=True)
    if data['msg']== "":
        return jsonify(error="Sorry, we Couldn't find you feedback. May be you missed something !"),200
    else:
        try:

            toaddrs = 'deathping1994@gmail.com'
            if data['from'] != "":
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

@app.route('/',methods=['POST','GET'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
@login_required
def hello_world():
    return jsonify(success="It works!")


@app.route('/login_action', methods=['GET', 'POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def login_action():
    data = request.get_json(force=True)
    print "inside login_action"
    if data['user']== "" or data['pass']=="":
        return jsonify(error="Enter User name and password")
    else:
        c = requests.Session()
        print "c created"
        try:
            c.get("https://webkiosk.jiit.ac.in")
            if data['usertype']=='S':
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
            else:
                params ={'x':'',
                    'txtInst':'Institute',
                    'InstCode':'JIIT',
                    'txtuType':'Member Type',
                    'UserType':data['usertype'],
                    'txtCode':'Employee Code',
                    'MemberCode':data['user'],
                    'DOB':"",
                    'DATE1':"",
                    'txtPin':'Password/Pin',
                    'Password':data['pass'],
                    'BTNSubmit':'Submit'}
            cook=c.cookies['JSESSIONID']
            cooki=dict(JSESSIONID=cook)
            reslogin=c.post("https://webkiosk.jiit.ac.in/CommonFiles/UserActionn.jsp", data=params,cookies=cooki)
            if "Error1.jpg" in reslogin.content:
                html=BeautifulSoup(reslogin.content,'html.parser')
                c.close()
                return jsonify(error=html.b.font.text),200
            else:
                # if data['usertype']=='S'
                #     url ="https://webkiosk.jiit.ac.in/StudentFiles/Academic/StudentAttendanceList.jsp"
                # res=c.get("https://webkiosk.jiit.ac.in/StudentFiles/Academic/StudentAttendanceList.jsp")
                # if data['user'] in res.content:
                c.close()
                authkey=bcrypt.generate_password_hash(data['user']+data['pass'])
                mongo.db.users.create_index("loggedat",expireAfterSeconds=120)
                mongo.db.users.update({"user" : data['user']}, {"$set" : {"authkey":authkey,"usertype":data['usertype'],"loggedat":datetime.utcnow()}},upsert=True)
                return jsonify(error="",success="Succcessfully Logged in!",authkey=authkey,usertype=data['usertype'])
                # elif "Timeout" in res.content:
                #     raise requests.ConnectionError
                # elif "not a valid" in res.content:
                #     c.close()
                #     return jsonify(error="Could Not Login,Invalid Details!")
                # else:
                #     c.close()
                #     return jsonify(error="Could Not Login,Invalid Details! Check your DOB")
        except (Exception) as error:
            print str(error)
            c.close()
            return jsonify(error="Could Not Connect to Internet. Webkiosk May be Down or unreachable")


@app.route('/logout',methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
@login_required
def logout():
    data = request.get_json(force=True)
    if not check_status(data['authkey'],data['usertype']):
        return jsonify(error="You need to be logged in before logging out !")
    else:
        mongo.db.users.remove({"authkey": data['authkey']},safe=True)
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
@login_required
def create_group():
    data=request.get_json(force=True)
    if data['title'] == "" or len(data['members'])==0:
        return jsonify(error="Incomplete Details provided")
    else:
        try:
            print "trying to insert in mongodb"
            members=data['membersid']
            query={'projecttype': data['projecttype'] ,'members':{ "$in": members } }
            group = mongo.db.groups.find_one(query)
            print type(group)
            # print group.count()
            if group is None and currentuser(data['authkey'],data['usertype']) in members:
                res=mongo.db.groups.insert({"projecttype":data['projecttype'],"members":data['membersid']})
                print res
                task = {
                    'title': data['title'],
                    'description': data['description'],
                    'members': data['members'],
                    'projecttype': data['projecttype'],
                    'approved': False,
                    'evaluated': False,
                    'groupid':str(res)
                    }
                print es.index(index='projects', doc_type='projects', body=task)
                return jsonify(success="Group Successfully registered!")
            elif group is None and currentuser(data['authkey'],data['usertype']) not in members:
                return jsonify(error="You are not authorised to register this group, this event will be reported !")
            else:
                return jsonify(error="Group Already registered, Use update project option to make changes to your existing project. ")
        except Exception as e:
            print e
            return jsonify(error="Oops ! Something Went wrong, Try Again")


@app.route('/v1/projects/<project_id>',methods=['POST','GET'])
def display_project(project_id):
    re=es.search(index="sw",id=project_id)
    return jsonify(re), 200

@app.route('/v1/projects/update/<group_id>',methods=['POST','GET'])
def update_project(project_id):
    data=request.get_json(force=True)
    members=mongo.db.groups.find_one({"id":data['group_id']})
    try:
        if currentuser(data['authkey'],data['usertype']) in members['members']:
            qbody={}
            if data['description'] is not None:
                qbody.__setitem__("description",data['description'])
            if data['additional_links'] is not None:
                qbody.__setitem__("additional_links",data['additional_links'])
            if data['synopsis'] is not None:
                qbody.__setitem__("synopsis",data['synopsis'])
            if data['projectreport'] is not None:
                qbody.__setitem__("projectreport",data['projectreport'])
            re=es.update(index="sw",doc_type='projects',id=members['id'],body=qbody)
            return jsonify(re), 200
        else:
            return jsonify(error="Either You are not part of this group or your project has already been evaluated"),200
    except Exception:
        return jsonify(error="Oops something went wrong ! Try again After sometime."),200

#
# @app.route('/base0/api/v1.0/projects/action', methods=['POST'])
# @login_required
# def ae_project():
#     es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#     data=request.get_json(force=True)
#     data_id=data['id']
#     print data_id
#     if data["action"]== "approve":
#         for id in data_id:
#             print id
#             body={
#             "doc" : {
#             "approved" : True
#                     }
#             };
#             es.update(index="sw",doc_type='projects',id=id,body=body);
#     else:
#         for id in data_id:
#             body={
#             "doc" : {
#             "approved" : False
#                     }
#             };
#             es.update(index="sw",doc_type='projects',id=id,body=body);
#     return "success", 200
#
#
# @app.route('/base0/api/v1.0/projects/list', methods=['GET'])
# def list_project():
#     es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#     qbody={
#             "query" : {
#             "match" : {
#             "mentor" : request.cookies.get("user")
#                     }
#                         }
#             }
#     re=es.search(index="sw",body=qbody)
#     re=re['hits']
#     return jsonify(re), 200

#
@app.route('/v1/projects/search', methods=['GET','POST'])
@cross_origin(origin='0.0.0.0',headers=['Content- Type','Authorization'])
def search_project():
    try:
        data=request.get_json(force=True)
        re=es.search(index="projects",q=data['query'])
        re=re['hits']
        return jsonify(re), 200
    except Exception :
        return jsonify(error="Oops ! something went wrong."),500
if __name__ == '__main__':
    app.run(host="0.0.0.0")