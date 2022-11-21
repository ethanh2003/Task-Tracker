import os  # os is used to get environment variables IP & PORT
from datetime import datetime

from flask import Flask, session
from flask import render_template
from flask import request, redirect, url_for

from forms import CommentForm
from database import db
from models import User, Todo, Comment

app = Flask(__name__)  # create an app

# sqp setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = "abc"
db.init_app(app)
user = User


@app.route("/")
def index():
    global user
    return render_template('index.html')


@app.route('/task')
def task():
    global user
    if user == User:
        return render_template('login.html', message="Please Log In To access this page")
    todo_list = Todo.query.all()
    user_list = User.query.all()
    return render_template('task.html', todo_list=todo_list, user_list=user_list, user=user)


@app.route("/add", methods=["POST"])
def add():
    global user
    title = request.form.get("title")
    description = request.form.get("description")
    due = request.form.get("due")
    assigned = ', '.join(request.form.getlist("assigned"))
    due = datetime.strptime(due, "%Y-%m-%d")
    new_todo = Todo(title=title, description=description, due=due, assigned=assigned, complete=0, createdBy=user.id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("task"))


@app.route("/update/<int:todo_id>")
def update(todo_id: int):
    global user
    todo = Todo.query.filter_by(id=todo_id).first()
    if todo.complete == 2:
        todo.complete = 0
    else:
        todo.complete = int(todo.complete) + 1
    db.session.commit()
    return redirect(url_for("task"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id: int):
    global user
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("task"))


@app.route("/register", methods=('GET', 'POST'))
def register():
    global user
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            return render_template('register.html', message="Username or Email already in use")
        else:
            new_user = User(name=name, email=email, username=username, password=password, access=False)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    error = None
    if request.method == 'POST':
        Current_user = User.query.filter_by(username=request.form['username']).first()
        if Current_user is None:
            error = 'Invalid Username. Please try again.'
        elif Current_user.password != request.form['password']:
            error = 'Invalid Password. Please try again.'
            Current_user = None
        else:
            session["user"] = Current_user.id
            global user
            user = Current_user
            return redirect(url_for('task'))
    return render_template('login.html', error=error)


@app.route("/updateUser/<int:user_id>", methods=['GET', 'POST'])
def updateUser(user_id: int):
    global user
    user_list = User.query.all()
    if request.method == 'POST':
        editUser = User.query.filter_by(id=user_id).first()
        if request.form.get("updatePass", False) != editUser.password:
            editUser.password = request.form["updatePass"]
        if request.form.get("editEmail", False) != editUser.email:
            editUser.email = request.form["editEmail"]
        if request.form.get("editUsername", False) != editUser.username:
            editUser.username = request.form["editUsername"]
        if request.form.get("editName", False) != editUser.name:
            editUser.name = request.form["editName"]
        if user.access == 1:
            if request.form.get("editAccess", False) == "Basic":
                access = False
            elif request.form.get("editAccess", False) == "Admin":
                access = True
            if access != editUser.access:
                editUser.access = access
        db.session.commit()
    user = User.query.filter_by(id=user.id).first()
    return redirect(url_for("viewUsers"))


@app.route('/ViewUsers', methods=['GET', 'POST'])
def viewUsers():
    global user
    user_list = User.query.all()
    if user == User:
        return render_template('login.html', message="Please Log In To access this page")
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        access = request.form.get("access")
        if int(access) == 0:
            access = False
        elif int(access) == 1:
            access = True
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            return render_template('ViewUsers.html', user_list=user_list, user=user,
                                   error="Username or Email already in use")
        else:
            new_user = User(name=name, email=email, username=username, password=password, access=access)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("viewUsers"))
    return render_template('ViewUsers.html', user_list=user_list, user=user)


@app.route("/deleteUser/<int:user_id>")
def deleteUser(user_id: int):
    global user
    deletedUser = User.query.filter_by(id=user_id).first()
    db.session.delete(deletedUser)
    db.session.commit()
    return redirect(url_for("viewUsers"))


@app.route("/logout")
def logout():
    global user
    user = User
    return render_template('index.html')


@app.route('/editTask/<int:task_id>', methods=['GET', 'POST'])
def editTask(task_id):
    global user
    if user:
        user_list = User.query.all()
        if request.method == 'POST':
            editedTask = Todo.query.filter_by(id=task_id).first()
            if request.form.get("editTitle", False) != editedTask.title:
                editedTask.title = request.form["editTitle"]
            if request.form.get("editDescription ", False) != editedTask.description:
                editedTask.description = request.form["editDescription "]
            if request.form.get("editDue", False) != editedTask.due:
                due = datetime.strptime(request.form["editDue"], "%Y-%m-%d")
                editedTask.due = due
            if request.form.get("assigned", False) != editedTask.assigned:
                editedTask.assigned = ', '.join(request.form.getlist("assigned"))

            db.session.commit()
            return redirect(url_for("task"))
        return render_template('editTask.html', user_list=user_list, user=user,
                               todo=Todo.query.filter_by(id=task_id).first())
    else:
        redirect(url_for('viewTask', task_id=task_id))


@app.route('/viewTask/<int:task_id>')
def viewTask(task_id):
    global user
    user_list = User.query.all()
    if user == User:
        return redirect(url_for('login'))
    else:
        form = CommentForm()
        return render_template('viewTask.html', user=user, user_list=user_list,
                               todo=Todo.query.filter_by(id=task_id).first(), form=form)


@app.route('/task/<task_id>/comment', methods=['POST'])
def new_comment(task_id):
    global user
    if user == User:
        return render_template('login.html', message="Please Log In To access this page")
    else:
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(task_id), user.id)
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('viewTask', task_id=task_id))


@app.route("/deleteComment/<int:comment_id>")
def deleteComment(comment_id: int):
    global user
    comment = Comment.query.filter_by(id=comment_id).first()
    task_id = comment.todo_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('viewTask', task_id=task_id))


@app.route('/pin/<task_id>')
def pinTask(task_id: str):
    global user
    user_id = user.id
    edit_user = User.query.filter_by(id=user_id).first()
    pinned = str(edit_user.pinnedTask)
    if edit_user.pinnedTask != "":
        if task_id not in pinned:
            pinned = pinned + '(' + task_id + ')'
    else:
        pinned = "(" + task_id + ")"
    edit_user.pinnedTask = pinned
    db.session.commit()
    user = User.query.filter_by(id=user.id).first()
    return redirect(url_for('task'))


@app.route('/unpin/<task_id>')
def unpinTask(task_id: str):
    global user
    user_id = user.id
    edit_user = User.query.filter_by(id=user_id).first()
    pinned = str(edit_user.pinnedTask)
    remove = '('+task_id+')'
    remove = str(remove)
    pinned = pinned.replace(remove, "")
    print(remove)
    print(pinned)
    edit_user.pinnedTask = pinned
    db.session.commit()
    user = User.query.filter_by(id=user.id).first()
    return redirect(url_for('task'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)), debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000
