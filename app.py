
import os                 # os is used to get environment variables IP & PORT
from flask import Flask, session   # Flask is the web app that we will customize
from flask import render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_session import Session

app = Flask(__name__)     # create an app

#sqp setup
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
    createdBy = db.Column(db.Integer)

user = User
@app.route("/")
def index():
    global user
    return render_template('index.html')

@app.route('/task')
def task():
    global user
    if(user==User):
        return render_template('login.html',message="Please Log In To access this page")
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
    new_todo = Todo(title=title,description=description,due=due,assigned=assigned, complete=0,createdBy=user.id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("task"))

@app.route("/update/<int:todo_id>")
def update(todo_id: int):
    global user
    todo = Todo.query.filter_by(id=todo_id).first()
    if(todo.complete == 2):
        todo.complete = 0
    else:
        todo.complete = int(todo.complete)+1
    db.session.commit()
    return redirect(url_for("task"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id: int):
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
        return redirect(url_for('login'))
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
def updateUser(user_id: int):
    global user
    if request.method == 'POST':
        editUser = User.query.filter_by(id=user_id).first()
        if(request.form.get("updatePass", False)!=editUser.password):
            editUser.password=request.form["updatePass"]
        if(request.form.get("editEmail", False)!=editUser.email):
            editUser.email=request.form["editEmail"]
        if(request.form.get("editUsername", False)!=editUser.username):
            editUser.username=request.form["editUsername"]
        if(request.form.get("editName", False)!=editUser.name):
            editUser.name=request.form["editName"]
        if user.access==1:
            if(request.form.get("editAccess", False)=="Basic"):
                access=False
            elif(request.form.get("editAccess", False)=="Admin"):
                access = True
            if(access!=editUser.access):
                editUser.access=access
        db.session.commit()
    return redirect(url_for("task"))

@app.route('/ViewUsers', methods=['GET', 'POST'])
def viewUsers():
    global user
    if(user==User):
        return render_template('login.html',message="Please Log In To access this page")
    if request.method == 'POST':
        name =  request.form.get("name")
        email =  request.form.get("email")
        username =  request.form.get("username")
        password =  request.form.get("password")
        access = request.form.get("access")
        if(int(access) == 0):
            access=False
        elif(int(access) == 1):
            access = True
        new_user = User(name=name,email=email,username=username,password=password,access=(access))
        db.session.add(new_user)
        db.session.commit()
    user_list = User.query.all()
    return render_template('ViewUsers.html',user_list=user_list,user=user)

@app.route("/deleteUser/<int:user_id>")
def deleteUser(user_id: int):
    global user
    deleteUser = User.query.filter_by(id=user_id).first()
    db.session.delete(deleteUser)
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
