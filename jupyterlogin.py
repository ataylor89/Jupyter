from flask import Flask, request, jsonify, render_template
from hashlib import blake2b
import configparser
import sqlite3
import datetime

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('hashes.ini')
secret_key = bytes(config.get('Hashes', 'SECRET_KEY'), encoding='utf-8')
digest_size = int(config.get('Hashes', 'DIGEST_SIZE'))

@app.route("/register_view", methods=["GET"])
def register_view():
    return render_template('register.html')

@app.route("/register", methods=["POST"])
def register():
    print(request.json)
    username = request.json['username']
    password = request.json['password']
    h = blake2b(key=secret_key, digest_size=digest_size)
    h.update(bytes(password, encoding='utf-8'))
    passwordhash = h.hexdigest()
    ts = str(datetime.datetime.now())

    con = sqlite3.connect('jupyterlogin.db')
    cur = con.cursor()
    cur.execute("select * from users where username='%s'" % username)
    if (cur.fetchone() == None):
        query = "insert into users (username, password, token, create_ts, last_update_ts) values ('%s', '%s', '%s', '%s', '%s')" % (username, passwordhash, 'null', ts, ts)
        cur.execute(query)
        con.commit()
        print('Registered')
        return jsonify(status="okay")
    else:
        return jsonify(status="error", errorMessage="username already taken")

@app.route("/login", methods=["POST"])
def login():
    username = request.json['username']
    password = request.json['password']
    h = blake2b(key=secret_key, digest_size=digest_size)
    h.update(bytes(password, encoding='utf-8'))
    passwordhash = h.hexdigest()

    con = sqlite3.connect('jupyterlogin.db')
    cur = con.cursor()
    cur.execute("select * from users where username='%s' and password='%s'" % (username, passwordhash))
    row = cur.fetchone()
    if (row[0] == username and row[1] == passwordhash):
        print('Logged in')
        return jsonify(status="okay")
    else:
        print('Invalid login')
        return jsonify(status="error", errorMessage="invalid login")

@app.route("/")
def home():
    return render_template('index.html')

con = sqlite3.connect('jupyterlogin.db')
cur = con.cursor()
cur.execute("select * from users")
for row in cur.fetchall():
    print(row)
app.run(host='0.0.0.0')