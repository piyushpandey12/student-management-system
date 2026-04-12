-- =========================================
-- 📌 USERS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    rollno VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 📌 STUDENTS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    rollno VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- 📌 ATTENDANCE TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS attendance (
    student_id INT PRIMARY KEY,
    total_classes INT DEFAULT 0,
    attended_classes INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- =========================================
-- 📌 MARKS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS marks (
    student_id INT PRIMARY KEY,
    subject VARCHAR(50) DEFAULT 'General',
    marks INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- =========================================
-- 📌 INDEXES
-- =========================================
CREATE INDEX IF NOT EXISTS idx_students_rollno ON students(rollno);
CREATE INDEX IF NOT EXISTS idx_users_rollno ON users(rollno);

-- =========================================
-- 📌 VIEW (FOR FRONTEND)
-- =========================================
CREATE OR REPLACE VIEW student_dashboard AS
SELECT 
    s.id,
    s.name,
    s.rollno AS roll,
    COALESCE(m.marks, 0) AS marks,
    CASE 
        WHEN a.attended_classes > 0 THEN TRUE
        ELSE FALSE
    END AS attendance
FROM students s
LEFT JOIN marks m ON s.id = m.student_id
LEFT JOIN attendance a ON s.id = a.student_id;

-- =========================================
-- 📌 FUNCTIONS (POSTGRESQL)
-- =========================================

-- ADD STUDENT
CREATE OR REPLACE FUNCTION add_student(p_roll VARCHAR, p_name VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO students (rollno, name)
    VALUES (p_roll, p_name);
END;
$$ LANGUAGE plpgsql;

-- MARK ATTENDANCE
CREATE OR REPLACE FUNCTION mark_attendance(p_student_id INT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO attendance (student_id, total_classes, attended_classes)
    VALUES (p_student_id, 1, 1)
    ON CONFLICT (student_id)
    DO UPDATE SET
        total_classes = attendance.total_classes + 1,
        attended_classes = attendance.attended_classes + 1;
END;
$$ LANGUAGE plpgsql;

-- UPDATE MARKS
CREATE OR REPLACE FUNCTION update_marks(p_student_id INT, p_marks INT)
RETURNS VOID AS $$
BEGIN
    INSERT INTO marks (student_id, subject, marks)
    VALUES (p_student_id, 'General', p_marks)
    ON CONFLICT (student_id)
    DO UPDATE SET marks = EXCLUDED.marks;
END;
$$ LANGUAGE plpgsql;

-- DELETE STUDENT
CREATE OR REPLACE FUNCTION delete_student(p_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM students WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;