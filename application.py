import os
import requests
import re


from flask import Flask, session,render_template, request, redirect, url_for,jsonify

from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/pythonlogin",methods=['GET','POST'])
def login():
    msg=''
    if request.method =='POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        account = db.execute('select * from account where username= :username and password = :password',{"username" : username ,"password":password}).fetchone()
        if account:
            session['loggedin']=True
            session['id']=account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg='incorrect username/password'   

    return render_template('index.html',msg=msg)
@app.route("/pythonlogin/register", methods=['GET','POST'])
def register():
    msg=''
    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account=db.execute('SELECT * FROM account WHERE username = :username', {"username":username}).fetchone()
        
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            db.execute('INSERT INTO account(username,password,email) VALUES (:username,:password,:email)', {"username":username,"password":password,"email":email})
            db.commit()
            msg = 'You have successfully registered!'   
    else:
        request.form == 'POST'
        msg="Please fill out the form"
    return render_template('register.html',msg=msg)       

@app.route('/pythonlogin/home',methods =['GET','POST'])
def home():
    #search function for book
    if request.method == "POST":
        searchQuery = request.form.get("searchQuery")
        #return value from search
        searchResult1 = db.execute("SELECT isbn FROM books WHERE isbn ILIKE :search OR author ILIKE :search OR title ILIKE :search",{"search": searchQuery}).fetchone()
        searchResult2 = db.execute("SELECT title FROM books WHERE isbn ILIKE :search OR author ILIKE :search OR title ILIKE :search",{"search": searchQuery}).fetchone()

        #add search result to the list
        
        session1 = []
        session2 = []
        #add each resul to the list
        for i in searchResult1:
            session1.append(i)
        for i in searchResult2:
            session2.append(i)    
            
        return render_template("home.html",book1=session1,book2=session2)

    return render_template("home.html")
        

            



@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/pythonlogin/profile/<isbn>')
def profile(isbn):

    
    profile = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json" , params={"key":"Ijw6y4OitnkcAQseynImWA","isbns":isbn})
     
    data=res.json()

    return render_template("profile.html",profile=profile,data=data)

    

    
    


