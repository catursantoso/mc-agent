from flask import Flask, render_template, url_for, redirect, session, request
import firebase_admin
from firebase_admin import credentials, firestore
from flask.helpers import flash
from flask.templating import render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
app.secret_key = 'makeitsecret'

# fungsi untuk login required
def login_required(f):
  @wraps(f)
  def wrapper(*args , **kwargs):
    if 'user' in session:
      return f(*args, **kwargs)
    else:
      flash('Maaf anda belum login', 'danger')
      return redirect(url_for('login'))
  return wrapper

# fungsi untuk admin required
def admin_required(f):
  @wraps(f)
  def wrapper(*args , **kwargs):
    if 'user' in session:
      if session['user']['access'] == 'admin':
        return f(*args, **kwargs)
      else:
        flash('Maaf anda bukan admin', 'danger')
        return redirect(url_for('dashboard'))
    else:
      flash('Maaf anda belum login', 'danger')
      return redirect(url_for('login'))
  return wrapper

# login
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

# register
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

# logout
@app.route('/logout')
def logout():
  session.clear()
  return render_template('login.html')

# dashboard
@app.route('/dashboard')
@login_required
def dashboard():
  return render_template('dashboard.html')

# index
@app.route('/')
def index():
  return render_template('index.html')

# agent
@app.route('/agent')
@login_required
@admin_required
def agent():
  agent = db.collection("users").stream()
  ag = []
  for agt in agent:
    a = agt.to_dict()
    a["id"] = agt.id
    ag.append(a)
  return render_template('agent.html', data=ag)

# ubah agent
@app.route('/agent/ubah/<uid>', methods = ['GET', 'POST'])
def ubah_agent(uid):
  if request.method == 'POST':
    data = {
      'name': request.form['name'],
      'username': request.form['username'],
      'access': request.form['access']
    }
    db.collection('users').document(uid).set(data, merge = True)
    flash('Selamat! data anda berhasil di ubah', 'primary')
    return redirect(url_for('agent'))
  user = db.collection('users').document(uid).get().to_dict()
  user['id'] = uid
  return render_template('ubah_agent.html', user=user)

# hapus data agent
@app.route('/agent/hapus/<uid>')
def hapus_agent(uid):
  db.collection('users').document(uid).delete()
  flash('Data agent berhasil di hapus', 'danger')
  return redirect(url_for('agent'))

@app.route('/buttons')
@login_required
@admin_required
def buttons():
  return render_template('buttons.html')

@app.route('/cards')
@login_required
@admin_required
def cards():
  return render_template('cards.html')

@app.route('/error')
@login_required
@admin_required
def error():
  return render_template('404.html')




if __name__ == '__main__':
  app.run(debug=True)