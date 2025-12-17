-- Created a schemas.sql file so it can be copy-pasted into pgAdmin4 on demand.

-- If tables needs to be dropped, this is the order to drop them:

-- DROP TABLE IF EXISTS player_answers;
-- DROP TABLE IF EXISTS session_players;
-- DROP TABLE IF EXISTS sessions;
-- DROP TABLE IF EXISTS answer_options;
-- DROP TABLE IF EXISTS questions;
-- DROP TABLE IF EXISTS quizzes;
-- DROP TABLE IF EXISTS users;


-- USERS
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,                -- e.g. 'teacher', 'player', 'admin'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- QUIZZES
CREATE TABLE quizzes (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    visibility VARCHAR(20),                   -- e.g. 'public', 'private'
    creator_id BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- QUESTIONS
CREATE TABLE questions (
    id BIGSERIAL PRIMARY KEY,
    quiz_id BIGINT NOT NULL REFERENCES quizzes(id),
    question_text TEXT NOT NULL,
    question_type VARCHAR(20),                -- e.g. 'multiple_choice', 'true_false'
    time_limit_seconds INT,                   -- e.g. 30
    points INT,                               -- e.g. 1000
    sort_order INT                            -- which order in the quiz
);

-- ANSWER OPTIONS
CREATE TABLE answer_options (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL REFERENCES questions(id),
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INT
);

-- SESSIONS (live games)
CREATE TABLE sessions (
    id BIGSERIAL PRIMARY KEY,
    quiz_id BIGINT NOT NULL REFERENCES quizzes(id),
    host_id BIGINT NOT NULL REFERENCES users(id),
    join_code VARCHAR(10) UNIQUE NOT NULL,    -- PIN players use to join
    status VARCHAR(20) NOT NULL DEFAULT 'waiting', -- waiting, in_progress, finished
    started_at TIMESTAMPTZ DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);

-- SESSION PLAYERS
CREATE TABLE session_players (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT NOT NULL REFERENCES sessions(id),
    user_id BIGINT REFERENCES users(id),      -- NULL = anonymous player
    nickname VARCHAR(50) NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    score INT NOT NULL DEFAULT 0,
    UNIQUE (session_id, nickname)             -- same nickname only once per session
);

-- PLAYER ANSWERS
CREATE TABLE player_answers (
    id BIGSERIAL PRIMARY KEY,
    session_player_id BIGINT NOT NULL REFERENCES session_players(id),
    question_id BIGINT NOT NULL REFERENCES questions(id),
    answer_option_id BIGINT NOT NULL REFERENCES answer_options(id),
    answered TIMESTAMPTZ DEFAULT NOW(),
    is_correct BOOLEAN,
    points_awarded INT
);



-- Creating a test query:

INSERT INTO users (username, email, password_hash, role)
VALUES ('teacher1', 'teacher1@example.com', 'hashed_pw', 'teacher');

SELECT * FROM users;