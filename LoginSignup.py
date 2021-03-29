from flask import Flask,request,Response,json
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb
import json
from json import JSONEncoder
import re
import bcrypt

app = Flask(__name__)
CORS(app)

# Secret keyss
app.secret_key = "1234567234"

# Database connection
app.config["MYSQL_HOST"]=""
app.config["MYSQL_USER"]=""
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]=""

db=MySQL(app)

# User register
@app.route('/register',methods=["POST"])
def register():

    if request.method=="POST":

        # json object
        jsonRegister = request.get_json()
        # Users field
        name = jsonRegister['name']
        email = jsonRegister['email']
        password = jsonRegister['password']
        confirm = jsonRegister['confirm']
        securePassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        # Database select quarry
        cursor.execute("select email from users.usersRegister where email='" + email + "'")
        fetchValueFromQuary = cursor.fetchall()

        # Email pattern
        pattern = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        patternCompile = re.compile(pattern)
        emailPattern = re.search(patternCompile, email)

        # Check email already exist or not
        if fetchValueFromQuary:
            if fetchValueFromQuary[0]['email'] == email:
                return Response(json.dumps({"Status_code": 404, "Message": "Email address already exist"}), status=404,mimetype='application/json')
        else:
                # Check email pattern
                if emailPattern:

                    # Check password equal to confirm password
                    if password==confirm:
                        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                        # Database insert quarry
                        cursor.execute("insert into usersRegister(name, email, password) values (%s,%s,%s)",(name,email,securePassword))
                        db.connection.commit()
                        return Response(json.dumps({"Status_code":200, "Message": "Register successfully"}), status=200, mimetype='application/json')

                    else:
                        return Response(json.dumps({"Status_code": 404, "Message": "Password does not match"}), status=404,mimetype='application/json')
                else:
                    return Response(json.dumps({"Status_code": 404, "Message": "Invalid email address"}), status=404, mimetype='application/json')
        db.connection.close()


# User Login
@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        # json object
        jsonLogin = request.get_json()
        # User field
        email = jsonLogin['email']
        password = jsonLogin['password'].encode('utf-8')

        cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
        # Database select quarry
        cur.execute("select id,name,email,password from users.usersRegister where email='"+email+"'")

        fetchValueFromQuary = cur.fetchall()
        

        # Check email exist or not
        if fetchValueFromQuary:
            # Check password exist or not
            checkPassword = bcrypt.checkpw(password, fetchValueFromQuary[0]['password'].encode('utf-8'))
            if fetchValueFromQuary[0]['email']==email and checkPassword:
                response ={
                        "status_code": 200,
                        "Message": "Login successfully",
                        "Id": fetchValueFromQuary[0]['id'],
                        "name": fetchValueFromQuary[0]['name']

                    }

                return Response(json.dumps(response), status=200,mimetype='application/json')
            else:
                return Response(json.dumps({"Status_code": 404, "Message": "Password does not match"}), status=404,mimetype='application/json')

        return Response(json.dumps({"Status_code": 404, "Message": "Email does not exist"}), status=404,mimetype='application/json')


@app.route('/imageupload',methods=["POST"])
def upload():
    if request.method=="POST":
        # json object
        jsonRegister = request.get_json()
        # Users field
        id = jsonRegister['id']
        path = jsonRegister['path']

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

        # Convert digital data to binary format
        
        cursor.execute("insert into uploadimage (id,images) values (%s,%s)",(id,path))
        db.connection.commit()
        cursor.execute("select serialId from users.uploadimage  where id='" + id + "'ORDER BY serialId DESC" )
        fetchValueFromQuary = cursor.fetchall()
        
        response = {
            "status_code": 200,
            "Message": "Image uploaded successfully",
            "Id": fetchValueFromQuary[0]['serialId']
        }

        return Response(json.dumps(response), status=200, mimetype='application/json')

        
    db.connection.close()
