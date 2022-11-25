from flask import Flask, render_template, request, redirect, session 
import ibm_db
import re
from markupsafe import escape
from flask_db2 import DB2
from datetime import datetime
from sendemail import sendmail

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

    if total > int(s):
        msg = "Hello " + session['username'] + " , " + "you have crossed the monthly limit of Rs. " + str(s) + "/- !!!" + "\n" + "Thank you, " + "\n" + "Team Personal Expense Tracker."  
        sendmail(msg,session['email'])  
    
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
                          



# # #delete---the--data
@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
    print("hello")
    print(id)
    param = f"DELETE FROM ExpenseDetails WHERE  userid = " + id
    res = ibm_db.exec_immediate(conn, param)

    print('deleted successfully')    
    return redirect("/display")
 
    
# # #UPDATE---DATA
@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    param = "SELECT * FROM expenses WHERE  id = " + id
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    row = []
    while dictionary != False:
        temp = []
        temp.append(dictionary["ID"])
        temp.append(dictionary["USERID"])
        temp.append(dictionary["DATE"])
        temp.append(dictionary["EXPENSENAME"])
        temp.append(dictionary["AMOUNT"])
        temp.append(dictionary["PAYMODE"])
        temp.append(dictionary["CATEGORY"])
        row.append(temp)
        print(temp)
        dictionary = ibm_db.fetch_assoc(res)

    print(row[0])
    return render_template('edit.html', expenses = row[0])




@app.route('/update/<id>', methods = ['POST'])
def update(id):
  if request.method == 'POST' :
   
      date = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']
      p1 = date[0:10]
      p2 = date[11:13]
      p3 = date[14:]
      p4 = p1 + "-" + p2 + "." + p3 + ".00"

      sql = "UPDATE ExpenseDetails SET date = ? , expensename = ? , amount = ?, paymode = ?, category = ? WHERE id = ?"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, p4)
      ibm_db.bind_param(stmt, 2, expensename)
      ibm_db.bind_param(stmt, 3, amount)
      ibm_db.bind_param(stmt, 4, paymode)
      ibm_db.bind_param(stmt, 5, category)
      ibm_db.bind_param(stmt, 6, id)
      ibm_db.execute(stmt)

      print('successfully updated')
      return redirect("/display")
     
      

            
 
         
    
            
 #limit
@app.route("/limit" )
def limit():
       return redirect('/limitn')

@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
         number= request.form['number']

         sql = "INSERT INTO limits (userid, limitss) VALUES (?, ?)"
         stmt = ibm_db.prepare(conn, sql)
         ibm_db.bind_param(stmt, 1, session['id'])
         ibm_db.bind_param(stmt, 2, number)
         ibm_db.execute(stmt)
         
         return redirect('/limitn')
     
         
@app.route("/limitn") 
def limitn():
    
    param = f"SELECT id, limitss FROM limits WHERE userid = '{escape(session['id'])}' ORDER BY id DESC LIMIT 1"
    res = ibm_db.exec_immediate(conn, param)
    dictionary = ibm_db.fetch_assoc(res)
    row = []
    s = " /-"
    while dictionary != False:
        temp = []
        temp.append(dictionary["LIMITSS"])
        row.append(temp)
        dictionary = ibm_db.fetch_assoc(res)
        s = temp[0]
    
    return render_template("limit.html" , y= s)

#REPORT
@app.route("/today")
def today():
      date = datetime.today().strftime("%Y-%m-%d") 
      print(date)

      param1 = f"SELECT TIME(date) as tn, amount FROM ExpenseDetails WHERE userid = '{escape(session['id'])}' AND date = '{escape(date)}'"
      res1 = ibm_db.exec_immediate(conn, param1)
      dictionary1 = ibm_db.fetch_assoc(res1)
      texpense = []

      while dictionary1 != False:
          temp = []
          temp.append(dictionary1["TN"])
          temp.append(dictionary1["AMOUNT"])
          texpense.append(temp)
          print(temp)
          dictionary1 = ibm_db.fetch_assoc(res1)

      param = f"SELECT * FROM ExpenseDetails WHERE userid = '{escape(session['id'])}' AND date = '{escape(date)}' ORDER BY date DESC"
      print(param)
      res = ibm_db.exec_immediate(conn, param)
      dictionary = ibm_db.fetch_assoc(res)
      expense = []
      print(dictionary)
      while dictionary != False:
          temp = []
          temp.append(dictionary["USERID"])
          temp.append(dictionary["DATE"])
          temp.append(dictionary["EXPENSENAME"])
          temp.append(dictionary["AMOUNT"])
          temp.append(dictionary["PAYMODE"])
          temp.append(dictionary["CATEGORY"])
          expense.append(temp)
          print(temp)
          dictionary = ibm_db.fetch_assoc(res)

  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          print(x[3],x[5])
          total += int(x[3])
          if x[5] == "food":
              t_food += int(x[3])
            
          elif x[5] == "entertainment":
              t_entertainment  += int(x[3])
        
          elif x[5] == "business":
              t_business  += int(x[3])
          elif x[5] == "rent":
              t_rent  += int(x[3])
           
          elif x[5] == "EMI":
              t_EMI  += int(x[3])
         
          elif x[5] == "other":
              t_other  += int(x[3])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
     

@app.route("/month")
def month():
      year=datetime.today().strftime("%Y")
      month=datetime.today().strftime("%m")
      param1 = f"SELECT DATE(date) as dt, SUM(amount) as tot FROM ExpenseDetails WHERE userid = '{escape(session['id'])}' AND MONTH(date) = '{escape(month)}' AND YEAR(date) = YEAR(current timestamp) GROUP BY DATE(date) ORDER BY DATE(date)"
      res1 = ibm_db.exec_immediate(conn, param1)
      dictionary1 = ibm_db.fetch_assoc(res1)
      texpense = []

      while dictionary1 != False:
          temp = []
          temp.append(dictionary1["DT"])
          temp.append(dictionary1["TOT"])
          texpense.append(temp)
          print(temp)
          dictionary1 = ibm_db.fetch_assoc(res1)
      

      param = f"SELECT * FROM ExpenseDetails WHERE userid = '{escape(session['id'])}' AND MONTH(date) = '{escape(month)}' AND YEAR(date) = '{escape(year)}' ORDER BY date DESC"
      res = ibm_db.exec_immediate(conn, param)
      dictionary = ibm_db.fetch_assoc(res)
      expense = []
      while dictionary != False:
          temp = []
          temp.append(dictionary["USERID"])
          temp.append(dictionary["DATE"])
          temp.append(dictionary["EXPENSENAME"])
          temp.append(dictionary["AMOUNT"])
          temp.append(dictionary["PAYMODE"])
          temp.append(dictionary["CATEGORY"])
          expense.append(temp)
          print(temp)
          dictionary = ibm_db.fetch_assoc(res)

  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total +=int(x[3])
          if x[5] == "food":
              t_food += int(x[3])
            
          elif x[5] == "entertainment":
              t_entertainment  += int(x[3])
        
          elif x[5] == "business":
              t_business  += int(x[3])
          elif x[5] == "rent":
              t_rent  += int(x[3])
           
          elif x[5] == "EMI":
              t_EMI  += int(x[3])
         
          elif x[5] == "other":
              t_other  += int(x[3])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         
@app.route("/year")
def year():
      year=datetime.today().strftime("%Y")
      param1 = f"SELECT MONTH(date) as mn, SUM(amount) as tot FROM ExpenseDetails WHERE userid = '{escape(session['id'])}' AND YEAR(date) = '{escape(year)}' GROUP BY MONTH(date) ORDER BY MONTH(date)"
      res1 = ibm_db.exec_immediate(conn, param1)
      dictionary1 = ibm_db.fetch_assoc(res1)
      texpense = []

      while dictionary1 != False:
          temp = []
          temp.append(dictionary1["MN"])
          temp.append(dictionary1["TOT"])
          texpense.append(temp)
          print(temp)
          dictionary1 = ibm_db.fetch_assoc(res1)

      param = f"SELECT * FROM ExpenseDetails WHERE userid = '{escape(session['id'])}' AND YEAR(date) = '{escape(year)}' ORDER BY date DESC"
      res = ibm_db.exec_immediate(conn, param)
      dictionary = ibm_db.fetch_assoc(res)
      expense = []
      while dictionary != False:
          temp = []
          temp.append(dictionary["USERID"])
          temp.append(dictionary["DATE"])
          temp.append(dictionary["EXPENSENAME"])
          temp.append(dictionary["AMOUNT"])
          temp.append(dictionary["PAYMODE"])
          temp.append(dictionary["CATEGORY"])
          expense.append(temp)
          print(temp)
          dictionary = ibm_db.fetch_assoc(res)

  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0

      for x in expense:
          total +=int(x[3])
          if x[5] == "food":
              t_food += int(x[3])
            
          elif x[5] == "entertainment":
              t_entertainment  += int(x[3])
        
          elif x[5] == "business":
              t_business  += int(x[3])
          elif x[5] == "rent":
              t_rent  += int(x[3])
           
          elif x[5] == "EMI":
              t_EMI  += int(x[3])
         
          elif x[5] == "other":
              t_other  += int(x[3])
     
      
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

# #log-out
@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('email', None)
   return render_template('home.html')

             
if __name__ == "__main__":
    app.run(debug=True)

        
        


