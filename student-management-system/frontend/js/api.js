// ================= BASE URL =================

// 🔴 LOCAL (for development)
// const BASE_URL = "http://127.0.0.1:5000";

// 🟢 PRODUCTION (Render)
const BASE_URL = "https://your-backend-name.onrender.com";


// ================= COMMON FETCH HANDLER =================
async function handleResponse(res) {
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
    }
    return res.json();
}


// ================= AUTH =================

// 🔐 LOGIN
async function loginUser(data) {
    try {
        const res = await fetch(`${BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Login Error:", error);
        return { error: "Server error" };
    }
}


// 🆕 REGISTER
async function registerUser(data) {
    try {
        const res = await fetch(`${BASE_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Register Error:", error);
        return { error: "Server error" };
    }
}


// ================= STUDENTS =================

// 📥 GET ALL STUDENTS
async function getStudents() {
    try {
        const res = await fetch(`${BASE_URL}/students/`);
        return await handleResponse(res);

    } catch (error) {
        console.error("Fetch Students Error:", error);
        return [];
    }
}


// ➕ ADD STUDENT
async function addStudentAPI(data) {
    try {
        const res = await fetch(`${BASE_URL}/students/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Add Student Error:", error);
        return null;
    }
}


// ✏️ UPDATE STUDENT
async function updateStudentAPI(id, data) {
    try {
        const res = await fetch(`${BASE_URL}/students/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Update Error:", error);
        return null;
    }
}


// ❌ DELETE STUDENT
async function deleteStudentAPI(id) {
    try {
        const res = await fetch(`${BASE_URL}/students/${id}`, {
            method: "DELETE"
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Delete Error:", error);
    }
}


// ================= ATTENDANCE =================

// ✅ MARK ATTENDANCE
async function markAttendanceAPI(data) {
    try {
        const res = await fetch(`${BASE_URL}/attendance/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Attendance Error:", error);
    }
}


// 📊 GET ATTENDANCE STATS
async function getAttendanceStats() {
    try {
        const res = await fetch(`${BASE_URL}/attendance/stats`);
        return await handleResponse(res);

    } catch (error) {
        console.error("Attendance Stats Error:", error);
        return { attendance_percentage: 0 };
    }
}


// ================= MARKS =================

// 📝 ADD MARKS
async function addMarksAPI(data) {
    try {
        const res = await fetch(`${BASE_URL}/marks/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        return await handleResponse(res);

    } catch (error) {
        console.error("Marks Error:", error);
    }
}


// 📈 GET MARKS STATS
async function getMarksStats() {
    try {
        const res = await fetch(`${BASE_URL}/marks/stats`);
        return await handleResponse(res);

    } catch (error) {
        console.error("Marks Stats Error:", error);
        return { avg_marks: 0, top_score: 0 };
    }
}