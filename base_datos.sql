CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    urgent BOOLEAN NOT NULL DEFAULT FALSE,
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
	localization VARCHAR(255) NOT NULL,
	exact_date DATE NOT NULL,
	start_time TIME NOT NULL,
	end_time TIME NOT NULL
);
