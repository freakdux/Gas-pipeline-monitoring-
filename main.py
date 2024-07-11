from flask import Flask, render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired,Length,ValidationError
from flask_bcrypt import Bcrypt

import requests
#import matplotlib.pyplot as plt
import pandas as pd
import os

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

app=Flask(__name__)


bcrypt=Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SECRET_KEY']='rutendra'
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return client.query.get(int(user_id))

class client(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20), nullable=False,unique=True)
    password=db.Column(db.String(80), nullable=False)
    channel = db.Column(db.String(100), nullable=False, unique=True)

class RegisteForm(FlaskForm):
    username=StringField(validators=[InputRequired(), Length(min=4,max=20)],render_kw={"placeholder": "Username"})
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder": "Password"})
    channel=StringField(validators=[InputRequired(), Length(min=4,max=20)],render_kw={"placeholder": "channel"})

    submit=SubmitField("Register")

    def validate_username(self,username):
        existing_user_username=client.query.filter_by(
            username=username.data
        ).first()
        if existing_user_username:
            raise ValidationError("The Username already exists")

class Loginform(FlaskForm):
    username=StringField(validators=[InputRequired(), Length(min=4,max=20)],render_kw={"placeholder": "Username"})
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)],render_kw={"placeholder": "Password"})

    submit=SubmitField("Login")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login',methods=['GET','POST'])
def login():
    form=Loginform()
    if form.validate_on_submit():
        user=client.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))

    return render_template('login.html',form=form)

def fetch_data_and_plot(url, field_name):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()['feeds']

        if data:
            df = pd.DataFrame(data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            plt.figure(figsize=(4, 4))
            plt.plot(df['created_at'], df[field_name], marker='o')
            if int(field_name[-1]) % 2 == 0:
                plt.ylabel('Pressure')
            else:
                plt.ylabel('Temperature')
            
            plt.title(field_name)
            plt.xlabel('Time')  
            
            plt.grid(True)
            plt.tight_layout()

            os.makedirs('static', exist_ok=True)
            plot_path = os.path.join('static', f'plot_{field_name}.png')
            plt.savefig(plot_path)
            plt.close()

            return plot_path
            
        else:
            return None

    except Exception as e:
        return f"Error: {str(e)}"

def generate_plots(channel_id):
    urls = {
        1: f'https://api.thingspeak.com/channels/{channel_id}/fields/1.json?api_key=F3O7F8TWEEFRDEII&results=2',
        2: f'https://api.thingspeak.com/channels/{channel_id}/fields/2.json?api_key=F3O7F8TWEEFRDEII&results=2',
        3: f'https://api.thingspeak.com/channels/{channel_id}/fields/3.json?api_key=F3O7F8TWEEFRDEII&results=2',
        4: f'https://api.thingspeak.com/channels/{channel_id}/fields/4.json?api_key=F3O7F8TWEEFRDEII&results=2',
        5: f'https://api.thingspeak.com/channels/{channel_id}/fields/5.json?api_key=F3O7F8TWEEFRDEII&results=2',
        6: f'https://api.thingspeak.com/channels/{channel_id}/fields/6.json?api_key=F3O7F8TWEEFRDEII&results=2'
    }

    plot_paths = []
    for field_num, url in urls.items():
        plot_path = fetch_data_and_plot(url, f'field{field_num}')
        if plot_path:
            plot_paths.append(plot_path)
    
    return plot_paths

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    channel_id = current_user.channel
    plot_paths = generate_plots(channel_id)
    return render_template('dashboard.html', plot_paths=plot_paths)



@app.route('/logout',methods=["GET",'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisteForm()
    
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data)
        hashed_channel=bcrypt.generate_password_hash(form.channel.data)
        new_user=client(username=form.username.data,password=hashed_password,channel=hashed_channel)
        db.session.add(new_user)
        db.session.commit()
        print("user registered")
        return redirect(url_for('login'))
    return render_template('register.html',form=form)
if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
