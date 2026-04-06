-- =========================================
-- 📌 USERS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rollno VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- =========================================
-- 📌 STUDENTS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rollno VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- =========================================
-- 📌 ATTENDANCE TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    total_classes INT DEFAULT 0,
    attended_classes INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =========================================
-- 📌 MARKS TABLE
-- =========================================
CREATE TABLE IF NOT EXISTS marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    subject VARCHAR(50) DEFAULT 'General',
    marks INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- =========================================
-- 📌 INDEXES (Performance Boost 🚀)
-- =========================================
CREATE INDEX idx_students_rollno ON students(rollno);
CREATE INDEX idx_users_rollno ON users(rollno);


-- =========================================
-- 📌 VIEW (IMPORTANT FOR FRONTEND 🔥)
-- =========================================
-- This combines all data for dashboard
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
-- 📌 STORED PROCEDURE: ADD STUDENT
-- =========================================
DELIMITER $$

CREATE PROCEDURE add_student(IN p_roll VARCHAR(20), IN p_name VARCHAR(100))
BEGIN
    INSERT INTO students (rollno, name)
    VALUES (p_roll, p_name);
END$$

DELIMITER ;


-- =========================================
-- 📌 STORED PROCEDURE: MARK ATTENDANCE
-- =========================================
DELIMITER $$

CREATE PROCEDURE mark_attendance(IN p_student_id INT)
BEGIN
    INSERT INTO attendance (student_id, total_classes, attended_classes)
    VALUES (p_student_id, 1, 1)
    ON DUPLICATE KEY UPDATE
        total_classes = total_classes + 1,
        attended_classes = attended_classes + 1;
END$$

DELIMITER ;


-- =========================================
-- 📌 STORED PROCEDURE: UPDATE MARKS
-- =========================================
DELIMITER $$

CREATE PROCEDURE update_marks(IN p_student_id INT, IN p_marks INT)
BEGIN
    INSERT INTO marks (student_id, subject, marks)
    VALUES (p_student_id, 'General', p_marks)
    ON DUPLICATE KEY UPDATE
        marks = p_marks;
END$$

DELIMITER ;


-- =========================================
-- 📌 STORED PROCEDURE: DELETE STUDENT
-- =========================================
DELIMITER $$

CREATE PROCEDURE delete_student(IN p_id INT)
BEGIN
    DELETE FROM students WHERE id = p_id;
END$$

DELIMITER ;


-- =========================================
-- 📌 STATS QUERIES (FOR DASHBOARD)
-- =========================================

-- Attendance %
SELECT 
    IFNULL(
        ROUND(SUM(attended_classes) / SUM(total_classes) * 100),
        0
    ) AS attendance_percentage
FROM attendance;


-- Marks Stats
SELECT 
    IFNULL(AVG(marks), 0) AS avg_marks,
    IFNULL(MAX(marks), 0) AS top_score
FROM marks;