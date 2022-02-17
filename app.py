from flask import Flask,render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager,login_user,UserMixin,logout_user,login_required

web = Flask(__name__)

web.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'

#Additional database is created using bind key
web.config['SQLALCHEMY_BINDS'] = {
    'registar': 'sqlite:///registar.db'}

web.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
web.config['SECRET_KEY'] = "Your_secret_string"
db = SQLAlchemy(web)

login_manager = LoginManager()
login_manager.init_app(web)

# database for notes
# nullable is not working so control through html by ending input tag with required
class notes(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

    name = db.Column(db.String(80), nullable=False,unique=True)
    title = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text(), nullable=True)


# # Database for join or registar
# #UserMixin provides all the necessary functions required so that we need not have to import them individually.
class registar(UserMixin,db.Model):
    __bind_key__ = 'registar'
    id=db.Column(db.Integer, primary_key=True)
    date_joined = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    fullname = db.Column(db.String(50),  nullable=False)
    email = db.Column(db.Text(50),nullable=True,unique=True)
    username = db.Column(db.String(20), nullable=False,unique=True)
    phone_number = db.Column(db.Integer,nullable=False,unique=True)
    password = db.Column(db.Text(),nullable=False,unique=True)


# # warning - don't change database variables names after creating database.
@web.route("/addnotes" , methods = ['POST','GET'])
# @login_required
def addnotes():
    if request.method == 'POST':
        print("post")
        # Fetch data from the form
        names = request.form.get('Name')
        titles = request.form.get('Title')
        contents = request.form.get('Content')
        print(names,titles,contents)

        # Add fetched data in the database
        note = notes(name=names,title=titles,content=contents)
        db.session.add(note)
        db.session.commit()
        return redirect("/notes")

    return render_template('addnotes.html')

@web.route("/join",methods=['POST','GET'])
def join():
    if request.method == 'POST':
        print("post")
        # Fetch data from the form
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        print(fullname,username,phone_number)

        # Add fetched data in the database
        secret = registar(fullname=fullname,username=username,email=email,phone_number=phone_number,password=password)
        db.session.add(secret)
        db.session.commit()
        return redirect('/')

    return render_template('join.html')

@login_manager.user_loader
def load_user(user_id):
    return registar.query.get(int(user_id))

@web.route("/", methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email= request.form.get('identity')
        phone_number = request.form.get('identity')
        passwords = request.form.get('password')
        print(email,phone_number,passwords)

        login1 = registar.query.filter_by(email=email).first()
        login2 = registar.query.filter_by(phone_number=phone_number).first()

        if email and passwords == login1.password and login1.email:
            print(email,passwords,"and",login1.password,login1.email)
            login_user(login1)
            print("successfully login1")
            return redirect('/addnotes')

        ##This is not working dont know why
        elif phone_number and passwords == login2.password and login2.phone_number:
            print(phone_number,passwords,"and",login2.password,login2.phone_number)
            login_user(login2)
            print("successfully login2")
            return redirect('/addnotes')

        else: 
            print("Can't login")
            return redirect('/')

    
    return render_template('login.html')

@web.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')

@web.route("/notes")
def display_notes():
    # retrive data from database and store it in data and then pass data to html
    data = notes.query.all()
    return render_template('notes.html',data=data)


@web.route("/delete/<int:sno>")
def delete(sno):
    ## retrive data from database whose sno is mentioned and store the first result IF MULTIPLE RESULT is present
    ## having same sno. 
    delete = notes.query.filter_by(sno=sno).first()
    # delete = notes.query.filter_by(sno=1).first()
    print(delete.sno)
    db.session.delete(delete)
    db.session.commit()
    return redirect('/notes')


@web.route("/update/<int:sno>" ,methods = ['GET','POST'])
def update(sno):
    ## get new data filled in form in update page
    name = request.form.get('Name')
    title = request.form.get('Title')
    content = request.form.get('Content')
    print(name,title,content)

    # retrive data from database to replace old data with new data from form
    update_data = notes.query.filter_by(sno=sno).first()
    if request.method == 'POST':
        update_data.name = name
        update_data.title= title
        update_data.content = content
        db.session.commit()    
        return redirect('/notes')
    else:
        print("Can't update your note")

    return render_template('update.html',data=update_data)

@web.route("/home")
def home():
    return render_template('home.html')


if __name__ == "__main__":
    web.run(debug=True,port=8000)