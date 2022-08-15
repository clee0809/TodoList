from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from forms import TodoListForm, RegisterForm, LoginForm, AlarmListForm
from flask_bootstrap import Bootstrap
from datetime import date, datetime
from flask_login import UserMixin, login_user, current_user, LoginManager, logout_user
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_
import os
from flask_migrate import Migrate #https://flask-migrate.readthedocs.io/en/latest/ 
# >$env:FLASK_APP='main'


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') #sessions for authentication
Bootstrap(app)

## ---------------------- DB -------------------------------------##
# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///cafes.db') # production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Todo(db.Model):
    __tablename__="todos"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    reminder = db.Column(db.Time)
    important = db.Column(db.Boolean, default=False)
    user = relationship("User", back_populates="todo_list")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)    

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    todo_list = relationship("Todo", back_populates="user")

db.init_app(app)
db.create_all()
## ---------------------- DB -------------------------------------##


@app.route('/', methods=["GET", "POST"])
def home():
    form = TodoListForm()
    # todo_list = Todo.query.all()
    # print(f'CURRENT USER: {current_user}')

    if current_user.is_authenticated:
        # todo_list = Todo.query.filter_by(user_id=current_user.id, important=None).order_by(Todo.due_date)
        # todo_list = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.due_date)
        todo_list = Todo.query.filter(and_(Todo.user_id == current_user.id, Todo.important == False)).order_by(Todo.due_date)
        todo_important = Todo.query.filter_by(user_id=current_user.id, important=True).order_by(Todo.due_date)
        # print(f'TYPE: {type(todo_list)}')
       
    else:
        flash("Please login or register to add/view your tasks.")
        todo_list=[]
        todo_important=[]

    if request.method == 'POST' and current_user.is_authenticated:  # form.validate_on_submit():

        if form.validate():
            print("validated?")
            print(form.todo, form['due_date'], form.due_date.raw_data[0], type(form.due_date.raw_data[0]))
            print(f'TIME: {form.end_time.raw_data[0]}', type(form.end_time.data))
            # print(f'{form.end_time.data.strftime("%I:%M %p")}') # HH:MM am pm
            # print(f"DATETIME: {form.due_date.raw_data[0]}")
            datetype_due_date = datetime.strptime(form.due_date.raw_data[0], "%Y-%m-%d").date()
            print(type(datetype_due_date))
            new_todo = Todo(
                title=form.todo.data,
                complete=False,
                due_date=datetype_due_date,
                reminder=form.end_time.data,
                user=current_user
            )
            print(new_todo.due_date)
            db.session.add(new_todo)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            if not current_user.is_authenticated:
                flash("Please login or register to add/view your tasks.")
            else:
                print("not validated")
                flash("Please enter task and due date.")
    return render_template("index.html", todo_list=todo_list, todo_important=todo_important, form=form)


@app.route('/edit/<int:todo_id>', methods=["GET", "POST"])
def edit(todo_id):
    todo = Todo.query.get(todo_id)
    # print(type(todo.due_date), todo.due_date)
    form = TodoListForm(
        todo=todo.title,
        complete=todo.complete,
        due_date=todo.due_date,
        end_time = todo.reminder,
        important=todo.important
    )
    # if request.method == 'POST':  # 
    if form.validate_on_submit():
        # print(f'CANCEL BUTTON: {form.btn_cancel.data}')
        # print(f'EDIT BUTTON: {form.btn_edit.data}')
        if form.btn_cancel.data:
            # print('CANCEL BUTTON CLICKED')
            return redirect(url_for('home'))

        # print(form.due_date.raw_data[0], type(form.due_date.raw_data[0]))
        datetype_due_date = datetime.strptime(
            form.due_date.raw_data[0], "%Y-%m-%d").date()
        todo.title = form.todo.data
        todo.complete = form.complete.data
        todo.due_date = datetype_due_date
        todo.reminder = form.end_time.data
        todo.important = form.important.data
        db.session.commit()
        return redirect(url_for('home'))    
    
    return render_template("edit.html", form=form)


@app.route("/delete/<int:todo_id>")
def delete(todo_id):    
    delete_todo = Todo.query.get(todo_id)
    db.session.delete(delete_todo)
    db.session.commit()
    return redirect(url_for('home'))


# user register
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    else:
        flash("Fill out this form to register.")
    return render_template("register.html", form=form, current_user=current_user)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    else:
        flash("Please enter your email and password to login.")
    return render_template("login.html", form=form, current_user=current_user)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
