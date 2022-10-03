import re
from datetime import datetime
from re import T
from xmlrpc.client import Boolean

from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from model import Thread, Topic

SQL_REGISTER = "INSERT INTO users (username, password, is_admin) VALUES (:username, :password, :is_admin)"
SQL_GET_USER_BY_USERNAME = "SELECT username FROM  users WHERE username=:username"
SQL_GET_ALL_TOPICS = "SELECT id, topic_name, restricted_access, created, created_by, updated FROM topics"
SQL_INSERT_TOPIC = "INSERT INTO topics (topic_name, restricted_access, created_by) VALUES (:topic_name, :restricted_access, :created_by)"
SQL_GET_THREADS_BY_TOPIC = "SELECT id, topic_id, title, created, created_by, updated FROM threads WHERE topic_id=:topic_id"
SQL_ADD_NEW_THREAD = " INSERT INTO threads (topic_id, title, created_by) VALUES (:topic_id, :title, :created_by)"


def register(username, password, is_admin) -> Boolean:
    hash_value = generate_password_hash(password)
    registered: Boolean = True

    try:
        db.session.execute(SQL_REGISTER, {
                           "username": username, "password": hash_value, "is_admin": is_admin})
    except Exception as e:
        db.session.close()
        registered = False
    else:
        db.session.commit()

    return registered


def find_user_by_username(username: str):
    try:
        return db.session.execute(SQL_GET_USER_BY_USERNAME, {"username": username}).fetchone()
    except Exception as e:
        db.session.close()


def get_all_topics():
    try:
        return db.session.execute(SQL_GET_ALL_TOPICS).fetchall()
    except Exception as e:
        db.session.close()


def add_topic(topic: Topic):
    topic_added: Boolean = True

    try:
        db.session.execute(SQL_INSERT_TOPIC, {
                           "topic_name": topic.topic_name,
                           "restricted_access": topic.restricted_access,
                           "created_by": topic.created_by})
    except Exception as e:
        db.session.close()
        topic_added = False
    else:
        db.session.commit()

    return topic_added


def get_threads_by_topic(topic_id: int):
    try:
        return db.session.execute(SQL_GET_THREADS_BY_TOPIC, {"topic_id": topic_id}).fetchall()
    except Exception as e:
        print(e)
        db.session.close()


def add_new_thread(thread: Thread):
    thread_added: Boolean = True

    try:
        db.session.execute(SQL_ADD_NEW_THREAD, {
                           "topic_id": thread.topic_id, "title": thread.title, "created_by": thread.created_by})
    except Exception as e:
        db.session.close()
        thread_added = False
    else:
        db.session.commit()

    return thread_added
