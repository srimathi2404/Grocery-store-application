from config import app 
from flask import Flask,request,jsonify
import os
from models import Users,role,RolesUsers,logs,db,get_pend_manager,approve_managers
import jwt
import datetime
import json
from tokengen import *
import hashlib

@app.route('/drop_table')
def drop():
    db.drop_all()
    db.create_all()
    return "Table dropped"


@app.post('/')
def user_login():
    if request.method=="POST":
        data=request.json
        print(data)
        username=data['username'] 
        password=data['password']
        encoded_password = password.encode('utf-8')
        hashed_password = hashlib.sha256(encoded_password).hexdigest()
        # m=Users.query.filter_by(username=username).first()
        m=db.session.query(Users).filter(Users.username==username).first()
        r=db.session.query(RolesUsers).filter(RolesUsers.user_id==username).first()

        if m :
            if r.role_id==1 or r.role_id==2 or (r.role_id==3 and m.active==True):
                if m.password==hashed_password :
                    # role_users=RolesUsers.query.filter_by(user_id=username).first()
                    toke = m.get_auth_token()
                    roles=db.session.query(role).filter(role.id==r.role_id).first()

                    now_time=datetime.now()
                    log_check = logs.query.filter_by(username = username).first()
                    if log_check:
                        log_check.timestamp = str(now_time)
                        db.session.add(log_check)
                        db.session.commit()
                    else:
                        new_log = logs(username = data['username'], timestamp = str(now_time))
                        db.session.add(new_log)
                        db.session.commit()
                else:
                    return jsonify({'message':'Invali'})
            else:
                return jsonify({'message':'manager login is invalid'})
                
        else:
             return jsonify({'message':'Invalid'})
        return jsonify({'token':toke,'role':roles.name,'username':r.user_id})
    else:
        return KeyError

@app.post('/signup')
def signup():
    is_manager=request.args.get('is_manager')
    data=request.json
    username=data['username']
    password=data['password']
    fname=data['fname']
    lname=data['lname']
    email=data['email']
    mobile=data['mobile']
    if is_manager:
        role=["manager"]
        active=False

    else:
        role=["user"]
        active=True
    is_auth=True
    encoded_password = password.encode('utf-8')
    hashed_password = hashlib.sha256(encoded_password).hexdigest()
    app.security.datastore.create_user(username=username,first_name=fname, last_name=lname,roles=role, mobile_no=mobile, email=email,password=hashed_password, authenticated=is_auth,purchase=0,active=active)
    db.session.commit()
    # create_user(username,password,fname,lname,email,mobile,0,1)

    return jsonify({'message':'user created'})
@app.route('/pending_manager')
def pend_manager():
    if request.method=="GET":
        list=get_pend_manager()
        return jsonify({'manager':list})
@app.route('/pending_manager/<username>',methods=["POST"])
def approve_manager(username):
    approve_managers(username)
    
    return jsonify({'message':'approved'})

    
