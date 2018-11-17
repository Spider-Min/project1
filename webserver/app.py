from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DB_USER = "tm2977"
DB_PASSWORD = "574u6jh2"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def home():
    if session.get('UName'):
        cursor = g.conn.execute("SELECT event_name FROM Event")
        names = []
        for result in cursor:
            names.append(result['event_name'])  # can also be accessed using result[0]
        cursor.close()

        context = dict(data = names)
        context2 = dict(n = session['UName'])

        return render_template('home.html', **context, **context2)
    else:
        return login()
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    # else:
    #     return "Hello Boss!"


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/isLogin', methods=['POST'])
def do_admin_login():

    t = {"username": request.form['username']}
    cursor = g.conn.execute(text(
        """
            select count(*)
            from User_
            where user_name = :username
        """
    ),t)
    a = cursor.fetchone()
    if a[0]:
        session['UName'] = request.form['username']
        return home()
    else:
        return login()


    # else:
    #     print("No")

    # if request.form['password'] == 'password' and request.form['username'] == 'admin':
    #     session['logged_in'] = True
    # else:
    #     flash('wrong password!')

@app.route('/register',methods=['GET'])
def do_register():

    return render_template('register.html')

@app.route('/createUser',methods=['GET', 'POST'])
def do_createUser():
    t = {"user_name": request.form['username']}
    g.conn.execute(text(
        """
            insert into  User_(uid, user_name)
            values
            (102, :user_name)
        """
    ),t)

    cursor = g.conn.execute(""" 
    select *
    from User_
    ;""")
    names = []
    for result in cursor:
        names.append(result['user_name'])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=names)

    # print(request.form['username'])
    # print(request.form['password'])
    return render_template("result.html", **context)

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)