-- =========================================
-- 📌 USERS TABLE (WITH ROLE)
-- =========================================
CREATE TABLE IF NOT EXISTS users (
    rollno VARCHAR(20) PRIMARY KEY,
    password TEXT NOT NULL,
    role VARCHAR(10) DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 📌 STUDENTS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS students (
    rollno VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 📌 SUBJECT-WISE MARKS
-- =========================================
CREATE TABLE IF NOT EXISTS marks (
    id SERIAL PRIMARY KEY,
    rollno VARCHAR(20),
    subject VARCHAR(50),
    marks INT DEFAULT 0,

    UNIQUE(rollno, subject),

    FOREIGN KEY (rollno)
    REFERENCES students(rollno)
    ON DELETE CASCADE
);

-- =========================================
-- 📌 DATE-WISE ATTENDANCE
-- =========================================
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    rollno VARCHAR(20),
    date DATE,
    status VARCHAR(10) CHECK (status IN ('present','absent')),

    UNIQUE(rollno, date),

    FOREIGN KEY (rollno)
    REFERENCES students(rollno)
    ON DELETE CASCADE
);

-- =========================================
-- 📌 INDEXES (FAST QUERIES)
-- =========================================
CREATE INDEX IF NOT EXISTS idx_students_rollno ON students(rollno);
CREATE INDEX IF NOT EXISTS idx_users_rollno ON users(rollno);

-- =========================================
-- 📌 VIEW (FOR DASHBOARD)
-- =========================================
CREATE OR REPLACE VIEW student_dashboard AS
SELECT 
    s.rollno,
    s.name,
    COALESCE(AVG(m.marks), 0) AS avg_marks,

    COUNT(a.id) FILTER (WHERE a.status = 'present') AS present_days,
    COUNT(a.id) AS total_days,

    CASE 
        WHEN COUNT(a.id) = 0 THEN 0
        ELSE ROUND(
            (COUNT(a.id) FILTER (WHERE a.status = 'present') * 100.0) 
            / COUNT(a.id), 2
        )
    END AS attendance_percent

FROM students s
LEFT JOIN marks m ON s.rollno = m.rollno
LEFT JOIN attendance a ON s.rollno = a.rollno
GROUP BY s.rollno, s.name;

-- =========================================
-- 📌 FUNCTIONS (OPTIONAL BUT CLEAN)
-- =========================================

-- ADD STUDENT
CREATE OR REPLACE FUNCTION add_student(p_roll VARCHAR, p_name VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO students (rollno, name)
    VALUES (p_roll, p_name);

    INSERT INTO users (rollno, password, role)
    VALUES (p_roll, 'default123', 'student');
END;
$$ LANGUAGE plpgsql;

-- DELETE STUDENT (CASCADE WILL HANDLE REST)
CREATE OR REPLACE FUNCTION delete_student(p_roll VARCHAR)
RETURNS VOID AS $$
BEGIN
    DELETE FROM students WHERE rollno = p_roll;
END;
$$ LANGUAGE plpgsql;

-- MARK ATTENDANCE
CREATE OR REPLACE FUNCTION mark_attendance(
    p_roll VARCHAR,
    p_date DATE,
    p_status VARCHAR
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO attendance (rollno, date, status)
    VALUES (p_roll, p_date, p_status)
    ON CONFLICT (rollno, date)
    DO UPDATE SET status = EXCLUDED.status;
END;
$$ LANGUAGE plpgsql;

-- UPDATE MARKS
CREATE OR REPLACE FUNCTION update_marks(
    p_roll VARCHAR,
    p_subject VARCHAR,
    p_marks INT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO marks (rollno, subject, marks)
    VALUES (p_roll, p_subject, p_marks)
    ON CONFLICT (rollno, subject)
    DO UPDATE SET marks = EXCLUDED.marks;
END;
$$ LANGUAGE plpgsql;