from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
import ibm_db
import re
from markupsafe import escape


app = Flask(__name__,template_folder='templates', static_folder='static')


conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=fjb77210; PWD=iIDykV67N2cpIlPR;", "", "")

@app.route("/")
def index():
    return render_template("index2.html")



@app.route("/login",methods=["GET", "POST"])
def login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
       
        sql = f"SELECT * from UserDetails where Username='{escape(username)}' and Password='{escape(password)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        account =ibm_db.fetch_both(stmt)
        print (account)
        
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['username'] = account[1]
            return redirect('/home')
        else:
            msg = 'Incorrect username (or) password !'
    return render_template('index2.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ''
    if request.method == 'POST' :
        msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql = f"SELECT * from UserDetails where Username='{escape(username)}' and Password='{escape(password)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        account =ibm_db.fetch_both(stmt)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = f"INSERT INTO userDetails VALUES('{escape(username)}','{escape(password)}')"
            stmt = ibm_db.exec_immediate(conn,insert_sql)
            msg = 'You have successfully registered !'
            return render_template('response.html')
    
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
