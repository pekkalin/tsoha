/** import script by running:
    psql -f <schema_file> -p <port> -U <user>
    for example: 
    psql -f schema.sql -p 5432 -U peksi 
**/

DROP DATABASE IF EXISTS tsoha;
CREATE DATABASE tsoha;
\c tsoha;

CREATE TABLE users (
    id serial PRIMARY KEY,
    username VARCHAR (50) UNIQUE NOT NULL,
    password VARCHAR (150) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP NULL
    );


CREATE TABLE topics (
    id serial PRIMARY KEY,
    topic_name VARCHAR (100),
    restricted_access BOOLEAN,
    created TIMESTAMP DEFAULT NOW(),
    created_by INT REFERENCES users(id),
    updated TIMESTAMP NULL
);

CREATE TABLE restricted_topic_users (
    user_id INT NOT NULL REFERENCES users(id),
    topic_id INT NOT NULL REFERENCES topics(id),
    grant_date TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, topic_id)
);

CREATE TABLE threads (
    id serial PRIMARY KEY,
    topic_id INT REFERENCES topics(id),
    title VARCHAR (255),
    created TIMESTAMP DEFAULT NOW(),
    created_by INT REFERENCES users(id),
    updated TIMESTAMP NULL
);

CREATE TABLE messages (
    id serial PRIMARY KEY,
    thread_id INT REFERENCES threads(id),
    content VARCHAR (500),
    created TIMESTAMP DEFAULT NOW(),
    created_by INT REFERENCES users(id),
    updated TIMESTAMP NULL
);

/**SELECT DISTINCT topics.id, topics.topic_name, topics.restricted_access, topics.created, topics.created_by, topics.updated, (SELECT COUNT(*) FROM THREADS WHERE topic_id=topics.id) as thread_count, (SELECT COUNT (*) FROM messages, threads WHERE threads.topic_id=topics.id AND messages.thread_id = threads.id) as message_count, (SELECT MAX(created) FROM messages) as latest_msg FROM topics, threads, messages; **/


