from datetime import datetime

from app import db
from model import Message, MThread, Topic

SQL_REGISTER = "INSERT INTO users (username, password, is_admin) VALUES (:username, :password, :is_admin) RETURNING id"
SQL_GET_USER_BY_USERNAME = "SELECT id, username, password FROM users WHERE username=:username"
SQL_GET_USER_BY_ID = "SELECT id, username, is_admin, last_login FROM users WHERE id=:id"
SQL_UPDATE_LAST_LOGIN = "UPDATE users SET last_login=:last_login WHERE id=:id"
SQL_GET_TOPIC_BY_ID = "SELECT id, topic_name, restricted_access, created, created_by, updated FROM topics WHERE id=:id"
SQL_INSERT_TOPIC = "INSERT INTO topics (topic_name, restricted_access, created_by) VALUES (:topic_name, :restricted_access, :created_by) RETURNING id"
SQL_ADD_NEW_THREAD = "INSERT INTO threads (topic_id, title, created_by) VALUES (:topic_id, :title, :created_by) RETURNING id"
SQL_ADD_NEW_MESSAGE = "INSERT INTO messages (thread_id, content, created_by) VALUES (:thread_id, :content, :created_by) RETURNING id"
SQL_GET_MESSAGES_BY_THREAD_ID = "SELECT id, thread_id, content, created, created_by, updated  FROM messages WHERE thread_id=:thread_id"

SQL_GET_TOPIC_PAGE_DATA = """SELECT DISTINCT topics.id, topics.topic_name, topics.restricted_access, topics.created, topics.created_by, topics.updated,
                                (SELECT COUNT(*) FROM threads WHERE threads.topic_id = topics.id) as thread_count,
                                (SELECT COUNT (*) FROM messages, threads WHERE threads.topic_id = topics.id AND messages.thread_id = threads.id) as message_count,
                                (SELECT MAX(messages.created) FROM messages, threads WHERE messages.thread_id = threads.id AND threads.topic_id = topics.id) as latest_msg
                                FROM topics"""

SQL_GET_RESTRICTED_TOPIC_USERS = "SELECT user_id, topic_id FROM restricted_topic_users"
SQL_GET_RESTRICTED_TOPIC_USER = "SELECT user_id, topic_id FROM restricted_topic_users WHERE user_id=:user_id AND topic_id=:topic_id"
SQL_GET_RESTRICTED_TOPICS = "SELECT id, topic_name FROM topics where restricted_access = TRUE"
SQL_INSERT_USER_TO_RESTRICTED_TOPIC = "INSERT INTO restricted_topic_users (user_id, topic_id) VALUES (:user_id, :topic_id)"

SQL_GET_THREADS_PAGE_DATA = """SELECT threads.id, threads.topic_id, threads.title, threads.created, threads.created_by, threads.updated,
                                (SELECT COUNT(*) FROM messages WHERE threads.topic_id=:topic_id AND messages.thread_id = threads.id) as thread_count,
                                (SELECT MAX(messages.created) FROM messages WHERE messages.thread_id = threads.id) as latest_msg
                                FROM threads WHERE threads.topic_id=:topic_id """

SQL_GET_ALL_USERS = """SELECT id, username FROM users WHERE is_admin = False"""


def register(username, password, is_admin):
    user_id: int = None

    try:
        user_id = db.session.execute(SQL_REGISTER, {
            "username": username, "password": password, "is_admin": is_admin}).fetchone()[0]
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


def find_all_users():
    try:
        return db.session.execute(SQL_GET_ALL_USERS).fetchall()
    except Exception as e:
        db.session.close()


def find_user_by_id(id: int):
    try:
        return db.session.execute(SQL_GET_USER_BY_ID, {"id": id}).fetchone()
    except Exception as e:
        db.session.close()


def update_last_login(id, date_and_time):
    update_succeed: bool = True
    try:
        db.session.execute(SQL_UPDATE_LAST_LOGIN, {
                           "last_login": date_and_time, "id": id})
    except Exception as e:
        update_succeed = False
        db.session.close()
    else:
        db.session.commit()

    return update_succeed


def get_all_topics():
    try:
        return db.session.execute(SQL_GET_TOPIC_PAGE_DATA).fetchall()
    except Exception as e:
        db.session.close()


def get_topic_by_id(id):
    try:
        return db.session.execute(SQL_GET_TOPIC_BY_ID, {"id": id}).fetchone()
    except Exception as e:
        db.session.close()


def get_restricted_topics_and_users():
    try:
        return db.session.execute(SQL_GET_RESTRICTED_TOPIC_USERS).fetchall()
    except Exception as e:
        db.session.close()


def get_restricted_topic_user(user_id: int, topic_id: int):
    try:
        return db.session.execute(SQL_GET_RESTRICTED_TOPIC_USER, {"user_id": user_id, "topic_id": topic_id}).first() is not None
    except Exception as e:
        db.session.close()


def get_restricted_topics():
    try:
        return db.session.execute(SQL_GET_RESTRICTED_TOPICS).fetchall()
    except Exception as e:
        print(e)
        db.session.close()


def add_user_access_to_restricted_topic(user_id: int, topic_id: int):
    succeed: bool = True
    try:
        db.session.execute(SQL_INSERT_USER_TO_RESTRICTED_TOPIC, {
                           "user_id": user_id, "topic_id": topic_id})
    except Exception as e:
        print(e)
        db.session.close()
        succeed = False
    else:
        db.session.commit()

    return succeed


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
        return db.session.execute(SQL_GET_THREADS_PAGE_DATA, {"topic_id": topic_id}).fetchall()
    except Exception as e:
        print(e)
        db.session.close()


def add_new_thread(thread: MThread):
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


def add_message(message: Message):
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
