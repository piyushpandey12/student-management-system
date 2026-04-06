// =========================================================
// 🌐 BASE URL (AUTO SWITCH)
// =========================================================
const BASE_URL =
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:5000"
        : "https://student-management-system-jg5j.onrender.com";


// =========================================================
// 📌 COMMON FETCH HANDLER (SAFE)
// =========================================================
async function handleResponse(res) {
    if (!res.ok) {
        try {
            const error = await res.json();
            throw new Error(error.error || error.message || "Request failed");
        } catch {
            throw new Error("Server error");
        }
    }
    return res.json();
}


// =========================================================
// 🔐 AUTH APIs
// =========================================================

// LOGIN
export async function loginUser(data) {
    try {
        const res = await fetch(`${BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Login Error:", error.message);
        return { status: "error", message: error.message };
    }
}


// REGISTER
export async function registerUser(data) {
    try {
        const res = await fetch(`${BASE_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Register Error:", error.message);
        return { status: "error", message: error.message };
    }
}


// =========================================================
// 👨‍🎓 STUDENT APIs
// =========================================================

// GET ALL STUDENTS
export async function getStudents() {
    try {
        const res = await fetch(`${BASE_URL}/students/`);
        return await handleResponse(res);

    } catch (error) {
        console.error("Fetch Students Error:", error.message);
        return [];
    }
}


// ADD STUDENT
export async function addStudentAPI(data) {
    try {
        const res = await fetch(`${BASE_URL}/students/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Add Student Error:", error.message);
        return null;
    }
}


// DELETE STUDENT
export async function deleteStudentAPI(id) {
    try {
        const res = await fetch(`${BASE_URL}/students/${id}`, {
            method: "DELETE"
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Delete Error:", error.message);
        return null;
    }
}


// =========================================================
// 📅 ATTENDANCE APIs
// =========================================================

// MARK ATTENDANCE
export async function markAttendanceAPI(student_id) {
    try {
        const res = await fetch(`${BASE_URL}/attendance/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id,
                total: 1,
                attended: 1
            })
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Attendance Error:", error.message);
        return null;
    }
}


// GET ATTENDANCE STATS
export async function getAttendanceStats() {
    try {
        const res = await fetch(`${BASE_URL}/attendance/stats`);
        return await handleResponse(res);

    } catch (error) {
        console.error("Attendance Stats Error:", error.message);
        return { attendance_percentage: 0 };
    }
}


// =========================================================
// 📊 MARKS APIs
// =========================================================

// ADD / UPDATE MARKS
export async function addMarksAPI(student_id, marks) {
    try {
        const res = await fetch(`${BASE_URL}/marks/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id,
                marks
            })
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Marks Error:", error.message);
        return null;
    }
}


// GET MARKS STATS
export async function getMarksStats() {
    try {
        const res = await fetch(`${BASE_URL}/marks/stats`);
        return await handleResponse(res);

    } catch (error) {
        console.error("Marks Stats Error:", error.message);
        return {
            avg_marks: 0,
            top_score: 0
        };
    }
}