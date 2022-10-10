from datetime import datetime
from os import getenv

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

import service
from model import Message, MThread, Topic

# from wtforms

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = getenv("TRACK_MODIFICATIONS")
app.secret_key = getenv("SECRET_KEY")

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class LoginUser(UserMixin):
    def __init__(self, id):
        self.id = id
        self.username = None
        self.is_admin = None
        self.last_login = None


@login_manager.user_loader
def load_user(user_id):
    dbuser = service.find_user_by_id(int(user_id))
    if dbuser:
        login_user = LoginUser(dbuser['id'])
        login_user.username = dbuser['username']
        login_user.is_admin = dbuser['is_admin']
        login_user.last_login = dbuser['last_login']
        return login_user
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        user = service.find_user_by_username(user_name)

        if user != None:
            if check_password_hash(user['password'], password):
                login_user(LoginUser(user['id']))
                service.update_last_login(user.id, datetime.now())
                return redirect(url_for('topic'))
            else:
                flash("Virheellinen salasana!")
                return redirect(url_for('login'))
        else:
            flash(f"Käyttäjää {user_name} ei löydy!")
            return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template("login.html")


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Sinut on uloskirjattu palvelusta!")
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        username = request.form['username']
        if len(username) < 1:
            flash("Käyttäjätunnus ei voi olla tyhjä!")
            return render_template("register.html")

        pass1 = request.form['password']
        if len(pass1) < 1:
            flash("Salasana ei voi olla tyhjä!")
            return render_template("register.html")

        pass2 = request.form['password2']
        if len(pass2) < 1:
            flash("Salasana ei voi olla tyhjä!")
            return render_template("register.html")

        if pass1 != pass2:
            flash("Salasanat eivät täsmää!", category="error")
            return render_template("register.html")

        admin = False
        if 'isadmin' in request.form:
            admin = True

        user = service.find_user_by_username(username)

        if (user):
            flash(f"Käyttäjätunnus {username} on jo käytössä!")
            return render_template("register.html")

        if None == service.register(username, generate_password_hash(pass1), admin):
            flash("Rekisteröinti epäonnistui!")
            return render_template("register.html")
        else:
            flash(f"Käyttäjä {username} lisätty onnistuneesti!")

    return render_template('login.html')


@app.route("/topic", methods=['GET', 'POST'])
@login_required
def topic():
    filtered_topics = []

    if request.method == "GET":
        all_topics = service.get_all_topics()
        restricted_topics = service.get_restricted_topics_and_users()

        # Filter restricted topics
        filtered_topics = filter(lambda t: not t.restricted_access or current_user.is_admin or t.restricted_access and (
            current_user.id, t.id) in restricted_topics, all_topics)

    elif request.method == 'POST':
        restricted = False
        if 'restricted' in request.form:
            restricted = True

        service.add_topic(Topic(topic_name=request.form['topic'],
                                restricted_access=restricted, created="", created_by=current_user.id, updated=""))
        all_topics = service.get_all_topics()
        restricted_topics = service.get_restricted_topics_and_users()
        # Filter restricted topics
        filtered_topics = filter(lambda t: not t.restricted_access or current_user.is_admin or t.restricted_access and (
            current_user.id, t.id) in restricted_topics, all_topics)

        return render_template("topics.html", topics=list(filtered_topics))

    return render_template("topics.html", topics=list(filtered_topics))


@app.route("/thread/<int:topic>")
@login_required
def thread(topic):
    t = service.get_topic_by_id(topic)

    if t == None:
        return redirect(url_for('topic'))

    threads = service.get_threads_by_topic(topic)
    print(threads)

    return render_template("threads.html", topic_id=topic, topic_name=t.topic_name, threads=threads)


@app.route("/thread", methods=['POST'])
@login_required
def new_thread():
    topic_id = request.form['topic_id']
    thread_title = request.form['thread']
    content = request.form['message']

    if len(thread_title) < 1:
        flash("Viestiketjun otsikko ei voi olla tyhjä!")
        return redirect(url_for('thread', topic=topic_id))

    if len(content) < 1:
        flash("Viesti ei voi olla tyhjä!")
        return redirect(url_for('thread', topic=topic_id))

    thread = MThread(
        topic_id=topic_id, title=thread_title, created="", created_by=current_user.id, updated="")

    thread_id = service.add_new_thread(thread)

    message = Message(thread_id=thread_id, content=content,
                      created="", created_by=current_user.id, updated="")

    service.add_message(message)

    return redirect(url_for('thread', topic=topic_id))


@app.route("/message/<int:thread_id>/<int:topic_id>")
@login_required
def message(thread_id, topic_id):
    messages = service.get_messages_by_thread_id(thread_id)
    return render_template("messages.html", messages=messages, thread_id=thread_id, topic_id=topic_id)


@app.route("/message", methods=['POST'])
@login_required
def new_message():
    thread_id = request.form['thread_id']
    content = request.form['message']
    topic_id = request.form['topic_id']

    if len(content) < 1:
        flash("Viesti ei voi olla tyhjä!")
        return redirect(url_for('message', thread_id=thread_id, topic_id=topic_id))

    message = Message(thread_id=thread_id, content=content,
                      created="", created_by=current_user.id, updated="")
    service.add_message(message)

    return redirect(url_for('message', thread_id=thread_id, topic_id=topic_id))


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    users = []
    restricted_topics = []
    users = service.find_all_users()
    restricted_topics = service.get_restricted_topics()

    if request.method == "GET":
        return render_template("admin.html", users=users, restricted_topics=restricted_topics)
    elif request.method == "POST":
        user_id = request.form['user']
        topic_id = request.form['topic']
        user = service.get_restricted_topic_user(user_id, topic_id)

        if user:
            flash("Käyttäjällä on jo oikeus aihealueelle!")
            return redirect(url_for('admin', users=users, restricted_topics=restricted_topics))
        else:
            if service.add_user_access_to_restricted_topic(user_id, topic_id):
                flash(f"Käyttäjälle lisätty oikeus aihealueelle!")
            else:
                flash("Käyttäjän lisääminen aihealueen käytttäjäksi epäonnistui!")
                return redirect(url_for('admin', users=users, restricted_topics=restricted_topics))
    return render_template("admin.html", users=users, restricted_topics=restricted_topics)


if __name__ == "__main__":
    app.run(debug=True)
