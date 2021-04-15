from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY']='S3N10R'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///senior.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
class Employers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)

class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    employerId = db.Column(db.Integer , nullable=False)
    admin = db.Column(db.Boolean)

class Points(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    includedAt = db.Column(db.String(50), nullable=False)
    employerId = db.Column(db.Integer , nullable=False)
    employeeId = db.Column(db.Integer , nullable=False)
    
def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):

    token = None

    if 'x-access-tokens' in request.headers:
        token = request.headers['x-access-tokens']

    if not token:
        return jsonify({'message': 'a valid token is missing',"system": "legacy"})

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'])
        current_user = Employees.query.filter_by(public_id=data['public_id']).first()
    except Exception as e :
        print(e)
        return jsonify({'message': 'token is invalid',"system": "legacy"})

    return f(current_user, *args, **kwargs)
   return decorator


@app.route('/register', methods=['GET', 'POST'])
def signup_user():  
    data = request.get_json(force=True)  
    print(data['name'])
    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Employees(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, employerId=data['employerId'],admin=False) 
    db.session.add(new_user)  
    db.session.commit()    
    return jsonify({'message': 'registered successfully',"system": "legacy"})

@app.route('/login', methods=['GET', 'POST'])  
def login_user(): 
 
  auth = request.authorization   
  print(auth.password)
  if not auth or not auth.username or not auth.password:  
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

  user = Employees.query.filter_by(name=auth.username).first()   
  print(user)
     
  if check_password_hash(user.password, auth.password):
    token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])  
    return jsonify({'message' : 'session token',"system": "legacy",'token' : token.decode()}) 

  return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})


#employer registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():  
    data = request.get_json(force=True)  
    print(data['name'])
    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Employers(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False) 
    db.session.add(new_user)  
    db.session.commit()    
    return jsonify({'message': 'registered successfully',"system": "legacy"})

@app.route('/signin', methods=['GET', 'POST'])  
def login(): 
 
  auth = request.authorization   
  print(auth.password)
  if not auth or not auth.username or not auth.password:  
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

  user = Employers.query.filter_by(name=auth.username).first()   
  print(user)
     
  if check_password_hash(user.password, auth.password):
    token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])  
    return jsonify({'token' : token.decode()}) 

  return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/employees', methods=['GET'])
def get_all_employees():  
   
   employees = Employees.query.all() 

   result = []   

   for user in employees:   
        employee_data = {}   
        employee_data['public_id'] = user.public_id  
        employee_data['name'] = user.name 
        employee_data['password'] = user.password
        employee_data['employerId'] = user.employerId
        employee_data['admin'] = user.admin 

        result.append(employee_data)   

   return jsonify({'message': 'successfully',"system": "legacy",'users': result})


@app.route('/mark', methods=['POST', 'GET'])
@token_required
def create_mark(current_user):
   
  # data = request.get_json() 
   new_mark = Points(includedAt=datetime.datetime.utcnow() , employerId=current_user.employerId, employeeId=current_user.id)  
   db.session.add(new_mark)   
   db.session.commit()   

   return jsonify({'message' : 'new check in created',"system": "legacy"})



@app.route('/marks', methods=['POST', 'GET'])
@token_required
def get_marks(current_user):

    marks = Points.query.filter_by(employeeId=current_user.id).all()

    output = []
    for mark in marks:

        mark_data = {}
        mark_data['includedAt'] = mark.includedAt
        mark_data['employerId'] = mark.employerId
        mark_data['employeeId'] = mark.employeeId
        output.append(mark_data)

    return jsonify({'message' : 'your check in history',"system": "legacy",'list_of_marks' : output})



if  __name__ == '__main__':  
     app.run(debug=True)



