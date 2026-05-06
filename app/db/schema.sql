DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS shifts;
DROP TABLE IF EXISTS shift_history;
DROP TABLE IF EXISTS shift_requests;

CREATE TABLE IF NOT EXISTS users (
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Admin', 'User')),
    rating_points INTEGER DEFAULT 70,
    mobile_number TEXT UNIQUE,
    post_code TEXT,
    profile_picture TEXT default 'default_profile.png',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shifts (
    shiftId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    date TEXT NOT NULL DEFAULT (DATE('now')),
    title TEXT NOT NULL,
    job_description TEXT,
    company_name TEXT NOT NULL,
    start_datetime TEXT NOT NULL,
    end_datetime TEXT NOT NULL,
    city TEXT NOT NULL,
    post_code TEXT NOT NULL,
    hourly_rate REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Open', 'Accepted', 'Completed', 'Cancelled','Expired')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES users(userId)
);

CREATE TABLE IF NOT EXISTS shift_history (
    historyId INTEGER PRIMARY KEY AUTOINCREMENT,
    shiftId INTEGER NOT NULL,
    userId INTEGER NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('Created', 'Updated', 'Deleted','Accepted','Completed','Cancelled',"Withdrawn")),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shiftId) REFERENCES shifts(shiftId),
    FOREIGN KEY (userId) REFERENCES users(userId)
);

create table if not exists shift_requests (
    requestId INTEGER PRIMARY KEY AUTOINCREMENT,
    shiftId INTEGER NOT NULL,
    requesterId INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Pending', 'Accepted', 'Rejected', 'Withdrawn','Cancelled')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shiftId) REFERENCES shifts(shiftId),
    FOREIGN KEY (requesterId) REFERENCES users(userId)
);