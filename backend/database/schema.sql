-- =========================================
-- 🔁 RESET
-- =========================================
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS marks CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS teachers CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- =========================================
-- 📌 USERS TABLE (FINAL FIXED)
-- =========================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,

    identifier VARCHAR(255) UNIQUE NOT NULL,   -- 🔥 FIXED
    email VARCHAR(255),
    name VARCHAR(255),

    password TEXT,                             -- nullable for Google
    google_id VARCHAR(255) UNIQUE,

    provider VARCHAR(50) DEFAULT 'local',      -- 🔥 IMPORTANT

    role VARCHAR(10) CHECK (role IN ('student','teacher')) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 📌 STUDENTS TABLE
-- =========================================
CREATE TABLE students (
    rollno VARCHAR(50) PRIMARY KEY,   -- 🔥 increased size
    user_id INT UNIQUE,
    name VARCHAR(255) NOT NULL CHECK (name <> ''),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =========================================
-- 📌 TEACHERS TABLE
-- =========================================
CREATE TABLE teachers (
    teacher_id VARCHAR(50) PRIMARY KEY,
    user_id INT UNIQUE,
    name VARCHAR(255) NOT NULL CHECK (name <> ''),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- =========================================
-- 📌 MARKS TABLE
-- =========================================
CREATE TABLE marks (
    id SERIAL PRIMARY KEY,
    rollno VARCHAR(50) NOT NULL,
    subject VARCHAR(100) NOT NULL CHECK (subject <> ''),
    marks INT CHECK (marks BETWEEN 0 AND 100),
    teacher_id VARCHAR(50),

    UNIQUE(rollno, subject),

    FOREIGN KEY (rollno)
        REFERENCES students(rollno)
        ON DELETE CASCADE,

    FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id)
        ON DELETE SET NULL
);

-- =========================================
-- 📌 ATTENDANCE TABLE
-- =========================================
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    rollno VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('present','absent')),
    teacher_id VARCHAR(50),

    UNIQUE(rollno, date),

    FOREIGN KEY (rollno)
        REFERENCES students(rollno)
        ON DELETE CASCADE,

    FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id)
        ON DELETE SET NULL
);

-- =========================================
-- 📌 INDEXES
-- =========================================
CREATE INDEX idx_users_identifier ON users(identifier);
CREATE INDEX idx_users_email ON users(email);

-- =========================================
-- 📌 FUNCTIONS
-- =========================================

-- ✅ ADD STUDENT
CREATE OR REPLACE FUNCTION add_student(
    p_roll VARCHAR,
    p_name VARCHAR,
    p_password TEXT
)
RETURNS VOID AS $$
DECLARE
    new_user_id INT;
BEGIN
    INSERT INTO users (identifier, name, password, role, provider)
    VALUES (p_roll, p_name, p_password, 'student', 'local')
    RETURNING id INTO new_user_id;

    INSERT INTO students (rollno, name, user_id)
    VALUES (p_roll, p_name, new_user_id);

EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Student already exists';
END;
$$ LANGUAGE plpgsql;

-- =========================================

-- ✅ ADD TEACHER
CREATE OR REPLACE FUNCTION add_teacher(
    p_id VARCHAR,
    p_name VARCHAR,
    p_password TEXT
)
RETURNS VOID AS $$
DECLARE
    new_user_id INT;
BEGIN
    INSERT INTO users (identifier, name, password, role, provider)
    VALUES (p_id, p_name, p_password, 'teacher', 'local')
    RETURNING id INTO new_user_id;

    INSERT INTO teachers (teacher_id, name, user_id)
    VALUES (p_id, p_name, new_user_id);

EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Teacher already exists';
END;
$$ LANGUAGE plpgsql;

-- =========================================

-- ✅ DELETE STUDENT
CREATE OR REPLACE FUNCTION delete_student(p_roll VARCHAR)
RETURNS VOID AS $$
BEGIN
    DELETE FROM students WHERE rollno = p_roll;
END;
$$ LANGUAGE plpgsql;

-- =========================================

-- ✅ UPSERT MARKS
CREATE OR REPLACE FUNCTION update_marks(
    p_roll VARCHAR,
    p_subject VARCHAR,
    p_marks INT,
    p_teacher VARCHAR
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO marks (rollno, subject, marks, teacher_id)
    VALUES (p_roll, p_subject, p_marks, p_teacher)
    ON CONFLICT (rollno, subject)
    DO UPDATE SET
        marks = EXCLUDED.marks,
        teacher_id = EXCLUDED.teacher_id;
END;
$$ LANGUAGE plpgsql;

-- =========================================

-- ✅ UPSERT ATTENDANCE
CREATE OR REPLACE FUNCTION mark_attendance(
    p_roll VARCHAR,
    p_date DATE,
    p_status VARCHAR,
    p_teacher VARCHAR
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO attendance (rollno, date, status, teacher_id)
    VALUES (p_roll, p_date, LOWER(p_status), p_teacher)
    ON CONFLICT (rollno, date)
    DO UPDATE SET
        status = LOWER(EXCLUDED.status),
        teacher_id = EXCLUDED.teacher_id;
END;
$$ LANGUAGE plpgsql;