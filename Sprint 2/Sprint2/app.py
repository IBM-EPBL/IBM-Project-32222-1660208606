from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
import ibm_db
import re
from markupsafe import escape


app = Flask(__name__,template_folder='templates', static_folder='static')


conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=fjb77210; PWD=iIDykV67N2cpIlPR;", "", "")

app = Flask(__name__)
app.secret_key="secret-key"



# #HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")



# #SIGN--UP--OR--REGISTER
@app.route("/signup")
def signup():
    return render_template("signup.html")



@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql = f"SELECT * from UserDetails where Username='{escape(username)}'"
        stmt = ibm_db.exec_immediate(conn, sql)
        account =ibm_db.fetch_both(stmt)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = f"INSERT INTO userDetails VALUES('{escape(username)}','{escape(email)}','{escape(password)}')"
            stmt = ibm_db.exec_immediate(conn,insert_sql)
            msg = 'You have successfully registered !'
            return render_template('signup.html', msg = msg)
    
    return render_template("register.html")
        


        
#  #LOGIN--PAGE    
@app.route("/signin")
def signin():
    return render_template("login.html")
        
@app.route('/login',methods =['GET', 'POST'])
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
    return render_template('login.html', msg = msg)

# #ADDING----DATA
@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']

    insert_sql = f"INSERT INTO ExpenseDetails VALUES('{escape(session['id'])}','{escape(date)}','{escape(expensename)}','{escape(amount)}','{escape(paymode)}','{escape(category)}')"
    stmt = ibm_db.exec_immediate(conn,insert_sql)
    print(session['id'])
    print(date + " " + expensename + " " + amount + " " + paymode + " " + category)


    print("Expenses added")

    param = f"SELECT * FROM ExpenseDetails WHERE userid ='{escape(session['id'])}' AND MONTH(date) = MONTH(current timestamp) AND YEAR(date) = YEAR(current timestamp) ORDER BY date DESC"
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    print(dictionary)
    expense = []
    while dictionary != False:
        temp = []
        temp.append(dictionary['USERID'])
        temp.append(dictionary['DATE'])
        temp.append(dictionary['EXPENSENAME'])
        temp.append(dictionary['AMOUNT'])
        temp.append(dictionary['PAYMODE'])
        temp.append(dictionary['CATEGORY'])
        expense.append(temp)
        print(temp)
        dictionary = ibm_db.fetch_assoc(res)

    total=0
    for x in expense:
          total += int(x[3])

    param = f"SELECT id, limitss FROM limits WHERE userid = '{escape(session['id'])}' ORDER BY id DESC LIMIT 1"
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    row = []
    s = 0
    while dictionary != False:
        temp = []
        temp.append(dictionary["LIMITSS"])
        row.append(temp)
        dictionary = ibm_db.fetch_assoc(res)
        s = temp[0]
    
    return redirect("/display")



# #DISPLAY---graph 
@app.route("/display")
def display():
    print(session["username"],session['id'])

    param = f"SELECT * FROM ExpenseDetails WHERE userid = '{escape(session['id'])}' ORDER BY date DESC"
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    expense = []
    while dictionary != False:
        temp = []
        temp.append(dictionary['USERID'])
        temp.append(dictionary['DATE'])
        temp.append(dictionary['EXPENSENAME'])
        temp.append(dictionary['AMOUNT'])
        temp.append(dictionary['PAYMODE'])
        temp.append(dictionary['CATEGORY'])
        expense.append(temp)
        print(temp)
        dictionary = ibm_db.fetch_assoc(res)

    return render_template('display.html' ,expense = expense)



if __name__ == "__main__":
    app.run(debug=True)