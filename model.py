from collections import namedtuple
from threading import Thread

Topic = namedtuple(
    "Topic", "topic_name restricted_access created created_by updated")

MThread = namedtuple(
    "MThread", "topic_id title created created_by updated")

Message = namedtuple(
    "Message", "thread_id content created created_by updated")
