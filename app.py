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


def check_status(authkey,usertype):
    if mongo.db.users.find_one({'authkey': authkey,'usertype': usertype}):
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
    print curruser
    if curruser is not None:
        return curruser['user']
    else:
        return "NULL"

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
        if groups.count()==0:
            return jsonify(success="No Conflicting Groups found. Proceed to next step.",error="")
        else:
            return jsonify(error="Someone in your group is also a member in other group.",groups=groups)
    else:
        return jsonify(error="At least one member is required per project.")


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
            print reslogin.content
            if "Locked" in reslogin.content:
                c.close()
                return jsonify(error="Account Locked. Contact ADMINISTRATOR.")
            elif "Invalid" in reslogin.content:
                c.close()
                return jsonify(error="Could Not Login,Invalid Details!")
            elif "valid user" in reslogin.content:
                c.close()
                return jsonify(error="You Probably entered incorrect DOB.")
            else:
                res=c.get("https://webkiosk.jiit.ac.in/StudentFiles/Academic/StudentAttendanceList.jsp")
                if data['user'] in res.content:
                    c.close()
                    authkey=bcrypt.generate_password_hash(data['user']+data['pass'])
                    mongo.db.users.update({"user" : data['user']}, {"$set" : {"authkey":authkey,"usertype":data['usertype']}},upsert=True)
                    return jsonify(error="",success="Succcessfully Logged in!",authkey=authkey,usertype=data['usertype'])
                elif "Timeout" in res.content:
                    raise requests.ConnectionError
                elif "not a valid" in res.content:
                    c.close()
                    return jsonify(error="Could Not Login,Invalid Details!")
                else:
                    c.close()
                    return jsonify(error="Could Not Login,Invalid Details! Check your DOB")
        except (requests.ConnectionError,requests.HTTPError) as error:
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
            query={'projecttype': data['projecttype'] ,"members": members }
            group = mongo.db.groups.find_one(query)
            print type(group)
            if group is None and currentuser(data['authkey'],data['usertype']) in members:
                task = {
                    'title': data['title'],
                    'description': data['description'],
                    'members': data['members'],
                    'projecttype': data['projecttype'],
                    'approved': False
                    }
                es.index(index='projects', doc_type='projects', body=task)
                res=mongo.db.groups.insert({"projecttype":data['projecttype'],"members":data['membersid']})
                return jsonify(success="Group Successfully registered!")
            elif group is None and currentuser(data['authkey'],data['usertype']) not in members:
                return jsonify(error="You are not authorised to register this group, this event will be reported !")
            else:
                return jsonify(error="Group Already registered, Use update project option to make changes to your existing project. ")
        except Exception as e:
            print e
            return jsonify(error="Oops ! Something Went wrong, Try Again")


# @app.route('/v1/projects/update/<project_id>',methods=['POST','GET'])
# def update_project():
#     data=request.get_json(force=True)
#     qbody={
#           "query" : {
#           "match" : {
#              "title" : request.args.get("q","")
#                       }
#                   }
#           }
#     re=es.search(index="sw",body=qbody)
#     re=re['hits']
#     return jsonify(re), 201

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
# @app.route('/base0/api/v1.0/projects/search', methods=['GET'])
# def search_project():
#     print (request.args.get("q"))
#     es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
#     re=es.search(index="projects", )
#     re=re['hits']
#     return jsonify(re), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0")