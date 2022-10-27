
import os                 # os is used to get environment variables IP & PORT
from flask import Flask, session   # Flask is the web app that we will customize
from flask import render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_session import Session


app = Flask(__name__)     # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "abc"  

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4150))
    email = db.Column(db.String(4150),unique=True)
    username = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100))
    access = db.Column(db.Boolean)#True if admin, False otherwise
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(4150))
    assigned = db.Column(db.String(100))
    due = db.Column(db.Date)
    complete = db.Column(db.Integer)
user = User
@app.route("/")
def index():
    global user
    return render_template('index.html')
@app.route('/task')
def task():
    global user
    todo_list = Todo.query.all()
    user_list = User.query.all()
    return render_template('task.html',todo_list=todo_list,user_list=user_list,user=user)
@app.route("/add", methods=["POST"])
def add():
    global user
    title = request.form.get("title")
    description = request.form.get("description")
    due=request.form.get("due")
    assigned = ', '.join(request.form.getlist("assigned"))
    due = datetime.strptime(due,"%Y-%m-%d")
    new_todo = Todo(title=title,description=description,due=due,assigned=assigned, complete=0)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("task"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    global user
    todo = Todo.query.filter_by(id=todo_id).first()
    if(todo.complete == 2):
        todo.complete = 0
    else:
        todo.complete = int(todo.complete)+1
    db.session.commit()
    return redirect(url_for("task"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    global user
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("task"))
@app.route("/register",methods=('GET', 'POST'))
def register():
    global user
    if request.method == 'POST':
        name =  request.form.get("name")
        email =  request.form.get("email")
        username =  request.form.get("username")
        password =  request.form.get("password")
        new_user = User(name=name,email=email,username=username,password=password,access=False)
        db.session.add(new_user)
        db.session.commit()
    return render_template('register.html',user=user)
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    error = None
    if request.method == 'POST':
        Current_user = User.query.filter_by(username=request.form['username']).first()
        if(Current_user==None):
            error = 'Invalid Username. Please try again.'
            Current_user=None;
        elif Current_user.password!=request.form['password']:
            error = 'Invalid Password. Please try again.'
            Current_user=None;
        else:
            session["user"] = Current_user.id
            global user
            user = Current_user
            return redirect(url_for('task'))
    return render_template('login.html', error=error)
@app.route("/updateUser/<int:user_id>", methods=['GET', 'POST'])
def updateUser(user_id):
    global user
    if request.method == 'POST':
        User = User.query.filter_by(id=user_id).first()
        if(request.form["updatePass"]!=User.password):
            User.password=request.form["updatePass"]
        if(request.form["editEmail"]!=User.email):
            User.email=request.form["editEmail"]
        if(request.form["editAccess"]=="Basic"):
            access=False
        elif(request.form["editAccess"]=="Admin"):
            access = True
        if(access!=User.access):
            User.access=access
        db.session.commit()
    return redirect(url_for("viewUsers"))
@app.route('/ViewUsers')
def viewUsers():
    global user
    user_list = User.query.all()
    return render_template('ViewUsers.html',user_list=user_list,user=user)
@app.route("/deleteUser/<int:user_id>")
def deleteUser(user_id):
    global user
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("viewUsers"))
@app.route("/logout")
def logout():
    global user
    user=User
    return render_template('index.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000
