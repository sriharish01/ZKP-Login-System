from flask import Flask, render_template, request, redirect, url_for, session
import re
import os
import grpc

import login_pb2
import login_pb2_grpc

import Crypto.Util.number
import random
import hashlib

app = Flask(__name__)

app.secret_key = os.urandom(24)

def authenticate_user(username, password):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = login_pb2_grpc.LoginStub(channel)
        bits = 32
        x = sum(ord(c) << i*8 for i, c in enumerate(password))
        p = Crypto.Util.number.getPrime(
            bits, randfunc=Crypto.Random.get_random_bytes)
        g = Crypto.Util.number.getPrime(
            bits, randfunc=Crypto.Random.get_random_bytes)
        while p == g:
            g = Crypto.Util.number.getPrime(
                bits, randfunc=Crypto.Random.get_random_bytes)

        print(x, p, g)
        r = random.getrandbits(bits) 
        c = pow(g, r, p)
        cipher = pow(g, ((x+r)%(p-1)), p)

        print(r, c, cipher)
        response = stub.Authenticate(login_pb2.LoginRequest(
            username=username, p=p, g=g, c=c, cipher=cipher))

        return response

@app.route('/') 
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha512(password.encode()).hexdigest()

        response = authenticate_user(username, password_hash)
        if response.response:
            session['loggedin'] = True
            session['id'] = response.id
            session['username'] = username

            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg) 
        else:   
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg = msg) 


@app.route('/logout') 
def logout(): 
    session.pop('loggedin', None) 
    session.pop('id', None) 
    session.pop('username', None) 
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = login_pb2_grpc.LoginStub(channel)
        
                response = stub.Register(login_pb2.RegisterRequest(
                username=username, password=hashlib.sha512(password.encode()).hexdigest(), email=email))
            
            if response.status == login_pb2.RegisterResponse.Status.SUCCESS:
                msg = 'You have successfully registered!'
            elif response.status == login_pb2.RegisterResponse.Status.ALREADY_EXISTS:
                msg = 'Username already exists!'
            else:
                msg = 'Unkown Error Occurred'

    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)

@app.route('/pythonlogin/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])

    return redirect(url_for('login'))    





if __name__ =='__main__':
	app.run(Debug=True)
