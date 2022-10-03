import re
from datetime import datetime
from xmlrpc.client import Boolean

from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from model import Message, MThread, Topic

SQL_REGISTER = "INSERT INTO users (username, password, is_admin) VALUES (:username, :password, :is_admin) RETURNING id"
SQL_GET_USER_BY_USERNAME = "SELECT username FROM  users WHERE username=:username"
SQL_GET_TOPIC_BY_ID = "SELECT id, topic_name, restricted_access, created, created_by, updated FROM topics WHERE id=:id"
SQL_GET_ALL_TOPICS = "SELECT id, topic_name, restricted_access, created, created_by, updated FROM topics"
SQL_INSERT_TOPIC = "INSERT INTO topics (topic_name, restricted_access, created_by) VALUES (:topic_name, :restricted_access, :created_by) RETURNING id"
SQL_GET_THREADS_BY_TOPIC = "SELECT id, topic_id, title, created, created_by, updated FROM threads WHERE topic_id=:topic_id"
SQL_ADD_NEW_THREAD = "INSERT INTO threads (topic_id, title, created_by) VALUES (:topic_id, :title, :created_by) RETURNING id"
SQL_ADD_NEW_MESSAGE = "INSERT INTO messages (thread_id, content, created_by) VALUES (:thread_id, :content, :created_by) RETURNING id"
SQL_GET_MESSAGES_BY_THREAD_ID = "SELECT id, thread_id, content, created, created_by, updated  FROM messages WHERE thread_id=:thread_id"


def register(username, password, is_admin):
    hash_value = generate_password_hash(password)
    user_id: int = None

    try:
        user_id = db.session.execute(SQL_REGISTER, {
            "username": username, "password": hash_value, "is_admin": is_admin}).fetchone()[0]
    except Exception as e:
        db.session.close()
    else:
        db.session.commit()

    return user_id


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


def get_topic_by_id(id):
    try:
        return db.session.execute(SQL_GET_TOPIC_BY_ID, {"id": id}).fetchone()
    except Exception as e:
        db.session.close()


def add_topic(topic: Topic):
    topic_id: int = None

    try:
        topic_id = db.session.execute(SQL_INSERT_TOPIC, {
            "topic_name": topic.topic_name,
            "restricted_access": topic.restricted_access,
            "created_by": topic.created_by})
    except Exception as e:
        db.session.close()
    else:
        db.session.commit()

    return topic_id


def get_threads_by_topic(topic_id: int):
    try:
        return db.session.execute(SQL_GET_THREADS_BY_TOPIC, {"topic_id": topic_id}).fetchall()
    except Exception as e:
        db.session.close()


def add_new_thread(thread: MThread) -> int:
    thread_id: int = None

    try:
        thread_id = db.session.execute(SQL_ADD_NEW_THREAD, {
            "topic_id": thread.topic_id, "title": thread.title, "created_by": thread.created_by}).fetchone()[0]
    except Exception as e:
        print(e)
        db.session.close()
    else:
        db.session.commit()

    return thread_id


def add_message(message: Message) -> int:
    message_id: int = None

    try:
        message_id = db.session.execute(SQL_ADD_NEW_MESSAGE, {
            "thread_id": message.thread_id, "content": message.content, "created_by": message.created_by}).fetchone()[0]
    except Exception as e:
        db.session.close()
    else:
        db.session.commit()

    return message_id


def get_messages_by_thread_id(thread_id):
    try:
        return db.session.execute(SQL_GET_MESSAGES_BY_THREAD_ID, {"thread_id": thread_id})
    except Exception as e:
        db.session.close()
