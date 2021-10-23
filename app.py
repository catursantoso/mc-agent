from flask import Flask, render_template, url_for, redirect, session, request
import firebase_admin
from firebase_admin import credentials, firestore
from flask.helpers import flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
app.secret_key = 'makeitsecret'

def login_required(f):
  @wraps(f)
  def wrapper(*args , **kwargs):
    if 'user' in session:
      return f(*args, **kwargs)
    else:
      flash('Maaf anda belum login', 'danger')
      return redirect(url_for('login'))
  return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    data = {
      'username': request.form['username'],
      'password': request.form['password']
    }
    
    users = db.collection('users').where('username', '==', data['username']).stream()
    user = {}
    for us in users:
      user = us.to_dict()
    if user:
      if check_password_hash(user['password'], data['password']):
        session['user'] = user
        return redirect(url_for('dashboard'))
      else:
        flash('Sorry, your password is wrong !!', 'danger')
        return redirect(url_for('login'))
    else:
      flash('Your email is not registered yet, please register your email', 'danger')
      return redirect(url_for('login'))
  return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
  if request.method == 'POST':
    data = {
      'name': request.form['name'],
      'username': request.form['username'],
      'email': request.form['email'],
      'access': request.form['access'],
      'password': request.form['password']
    }
    
    users = db.collection('users').where('email', '==', data['email']).stream()
    user = {}
    for us in users:
      user=us.to_dict()
    if user:
      flash('Email already registered', 'danger')
      return redirect(url_for('register'))
    
    users = db.collection('users').where('username', '==', data['username']).stream()
    user = {}
    for us in users:
      user=us.to_dict()
    if user:
      flash('Username already used, please choose another username', 'danger')
      return redirect(url_for('register'))
    
    data['password'] = generate_password_hash(request.form['password'], 'sha256')
    db.collection('users').document().set(data)
    flash('Congratulations, your account has been registered', 'success')
    return redirect(url_for('login'))
  return render_template('register.html')

@app.route('/logout')
def logout():
  session.clear()
  return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
  return render_template('dashboard.html')

@app.route('/buttons')
@login_required
def buttons():
  return render_template('buttons.html')

@app.route('/cards')
@login_required
def cards():
  return render_template('cards.html')

@app.route('/error')
@login_required
def error():
  return render_template('404.html')




if __name__ == '__main__':
  app.run(debug=True)