-- =========================================
-- 📌 USERS TABLE (UNIFIED LOGIN)
-- =========================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(100) UNIQUE NOT NULL,   -- rollno / teacherId / email
    password TEXT,                             -- NULL for Google users
    role VARCHAR(10) CHECK (role IN ('student','teacher')) NOT NULL,
    email VARCHAR(100) UNIQUE,
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
-- 📌 TEACHERS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 📌 MARKS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS marks (
    id SERIAL PRIMARY KEY,
    rollno VARCHAR(20),
    subject VARCHAR(50),
    marks INT DEFAULT 0,
    teacher_id VARCHAR(20),

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
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
    rollno VARCHAR(20),
    date DATE,
    status VARCHAR(10) CHECK (status IN ('present','absent')),
    teacher_id VARCHAR(20),

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
CREATE INDEX IF NOT EXISTS idx_students_rollno ON students(rollno);
CREATE INDEX IF NOT EXISTS idx_users_identifier ON users(identifier);

-- =========================================
-- 📌 VIEW (DASHBOARD)
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
-- 📌 FUNCTIONS
-- =========================================

-- ✅ ADD STUDENT
CREATE OR REPLACE FUNCTION add_student(p_roll VARCHAR, p_name VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO students (rollno, name)
    VALUES (p_roll, p_name);

    INSERT INTO users (identifier, password, role)
    VALUES (p_roll, NULL, 'student');  -- use backend hashing instead
END;
$$ LANGUAGE plpgsql;


-- ✅ ADD TEACHER
CREATE OR REPLACE FUNCTION add_teacher(p_id VARCHAR, p_name VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO teachers (teacher_id, name)
    VALUES (p_id, p_name);

    INSERT INTO users (identifier, password, role)
    VALUES (p_id, NULL, 'teacher');
END;
$$ LANGUAGE plpgsql;


-- ✅ DELETE STUDENT
CREATE OR REPLACE FUNCTION delete_student(p_roll VARCHAR)
RETURNS VOID AS $$
BEGIN
    DELETE FROM students WHERE rollno = p_roll;
END;
$$ LANGUAGE plpgsql;


-- ✅ MARK ATTENDANCE
CREATE OR REPLACE FUNCTION mark_attendance(
    p_roll VARCHAR,
    p_date DATE,
    p_status VARCHAR,
    p_teacher VARCHAR
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO attendance (rollno, date, status, teacher_id)
    VALUES (p_roll, p_date, p_status, p_teacher)
    ON CONFLICT (rollno, date)
    DO UPDATE SET 
        status = EXCLUDED.status,
        teacher_id = EXCLUDED.teacher_id;
END;
$$ LANGUAGE plpgsql;


-- ✅ UPDATE MARKS
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