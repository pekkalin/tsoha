from collections import namedtuple
from threading import Thread

Topic = namedtuple(
    "Topic", "topic_name restricted_access created created_by updated")

Thread = namedtuple("Thread", "topic_id title created created_by updated")
