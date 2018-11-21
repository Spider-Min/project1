from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, make_response, url_for
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import flask_login
import logging
from flask_login import LoginManager
import flask_logger

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DB_USER = "tm2977"
DB_PASSWORD = "574u6jh2"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

engine = create_engine(DATABASEURI)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'please login!'
login_manager.session_protection = 'strong'
logger = logging.getLogger(__name__)



# Here we create a test table and insert some values in it
# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
class User(flask_login.UserMixin):
    pass
    # def __init__(self, id, active=True):
    #     self.id = id
    #     self.active = active

@login_manager.user_loader
def load_user(user_id):
    cursor = g.conn.execute("SELECT user_name FROM User_")
    uids = []
    for result in cursor:
        uids.append(result['user_name'])
    if user_id not in uids:
        return
    user = User()
    user.id = user_id
    return user

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

@app.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def home():
    # if session.get('UName'):

    cursor = g.conn.execute("SELECT event_name, likes, event_date, tag FROM Event")
    names = []
    likes = []
    event_dates = []
    tags = []
    for result in cursor:
        names.append(result['event_name'])  # can also be accessed using result[0]
        likes.append(result['likes'])
        event_dates.append(result['event_date'])
        tags.append(result['tag'])
    cursor.close()

    cursor = g.conn.execute("SELECT count(*) FROM Event")
    a = cursor.fetchone()
    count = a[0]

    count_dic = dict(count = count)
    names_dic = dict(names = names)
    user_id_dic = dict(n = flask_login.current_user.id)
    likes_dic = dict(likes=likes)
    event_dates_dic = dict(event_dates=event_dates)
    tags_dic = dict(tags=tags)
    return render_template('home.html', **names_dic, **user_id_dic, **likes_dic, **event_dates_dic, **tags_dic, **count_dic)
    # return render_template('home.html', **datas_dic)
    # else:
    #     return login()
    # if not session.get('logged_in'):
    #     return render_template('login.html')
    # else:
    #     return "Hello Boss!"


# @app.route('/login')
# def login():
#     return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
        if request.method == 'POST':
            logger.debug("login post method")
            t = {"username": request.form['username'], "password" : request.form['password']}


            cursor = g.conn.execute(text(
                """
                    select count(*)
                    from User_
                    where user_name = :username and password = :password
                """
            ),t)
            a = cursor.fetchone()
            if a[0]:
                user = User()
                user.id = request.form["username"]
                flask_login.login_user(user)
                # resp = make_response(render_template('index.html', name=request.form["username"]))
                # resp.set_cookie('username', request.form["username"])
                session['UName'] = request.form['username']
                session['password'] = request.form['password']
                return home()
            else:
                return render_template('login.html')

        return render_template('login.html')


    # else:
    #     print("No")

    # if request.form['password'] == 'password' and request.form['username'] == 'admin':
    #     session['logged_in'] = True
    # else:
    #     flash('wrong password!')

@app.route('/logout')
@flask_login.login_required
def logout():
    logger.debug("logout page")
    flask_login.logout_user()
    return render_template('login.html')


@app.route('/register',methods=['GET'])
def do_register():
    return render_template('register.html')

@app.route('/post',methods=['GET'])
@flask_login.login_required
def post():
    return render_template('post.html')

@app.route('/do_post',methods=['GET', 'POST'])
def do_post():
    t1 = {"event_name": request.form['eventname'],"event_date" : request.form['eventdate'], "description" : request.form['description'], "tag": request.form['tag']}
    cursor = g.conn.execute(text(
        """
            insert into  Event(event_name, event_date, description,tag)
            values
            (:event_name, :event_date, :description, :tag)
        """
    ),t1)

    cursor = g.conn.execute(
    """
    select max(eid) from Event
    
    """)


    event = cursor.fetchone()
    eid = event[0]

    t2 = {"eid": eid, "location": request.form['location']}
    g.conn.execute(text(
        """
            insert into  Take_Places(eid, address)
            values
            (:eid, :location)
        """
    ),t2)
    return home()



@app.route('/createUser',methods=['GET', 'POST'])
def do_createUser():
    t = {"user_name": request.form['username'],"password" : request.form['password']}
    g.conn.execute(text(
        """
            insert into  User_(user_name, password)
            values
            (:user_name, :password)
        """
    ),t)

    # cursor = g.conn.execute("""
    # select *
    # from User_
    # ;""")
    # names = []
    # for result in cursor:
    #     names.append(result['user_name'])  # can also be accessed using result[0]
    # cursor.close()
    # context = dict(data=names)

    # print(request.form['username'])
    # print(request.form['password'])
    return render_template("login.html")

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)