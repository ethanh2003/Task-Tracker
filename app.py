
import os                 # os is used to get environment variables IP & PORT
from flask import Flask   # Flask is the web app that we will customize
from flask import render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
user = None;

app = Flask(__name__)     # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4150))
    email = db.Column(db.String(4150),unique=True)
    username = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100))
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(4150))
    assigned = db.Column(db.String(100))
    due = db.Column(db.Date)
    complete = db.Column(db.Integer)
@app.route("/")
def index():
    
    return render_template('index.html')
@app.route('/task')
def task():
    todo_list = Todo.query.all()
    user_list = User.query.all()
    return render_template('task.html',todo_list=todo_list,user_list=user_list)
@app.route("/add", methods=["POST"])
def add():
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
    todo = Todo.query.filter_by(id=todo_id).first()
    if(todo.complete == 2):
        todo.complete = 0
    else:
        todo.complete = int(todo.complete)+1
    db.session.commit()
    return redirect(url_for("task"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("task"))
@app.route("/register",methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name =  request.form.get("name")
        email =  request.form.get("email")
        username =  request.form.get("username")
        password =  request.form.get("password")
        new_user = User(name=name,email=email,username=username,password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if(user==None):
            error = 'Invalid Username. Please try again.'
            user=None;
        elif user.password!=request.form['password']:
            error = 'Invalid Password. Please try again.'
            user=None;
        else:
            return redirect(url_for('task'))
    return render_template('login.html', error=error)





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host=os.getenv('IP', '127.0.0.1'),port=int(os.getenv('PORT', 5000)),debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000
