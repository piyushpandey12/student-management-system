// =========================================================
// 🌐 BASE URL (AUTO SWITCH)
// =========================================================
const BASE_URL =
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:5000"
        : import.meta.env.VITE_API_URL;


// =========================================================
// 📌 DEFAULT HEADERS
// =========================================================
const defaultHeaders = {
    "Content-Type": "application/json"
};


// =========================================================
// ⏱️ FETCH WITH TIMEOUT
// =========================================================
function fetchWithTimeout(url, options = {}, timeout = 8000) {
    return Promise.race([
        fetch(url, options),
        new Promise((_, reject) =>
            setTimeout(() => reject(new Error("Request timeout")), timeout)
        )
    ]);
}


// =========================================================
// 📌 COMMON RESPONSE HANDLER
// =========================================================
async function handleResponse(res) {
    let data;

    try {
        data = await res.json();
    } catch {
        throw new Error("Invalid server response");
    }

    if (!res.ok) {
        throw new Error(data.error || data.message || "Request failed");
    }

    return data;
}


// =========================================================
// 🔐 AUTH APIs
// =========================================================

// LOGIN
export async function loginUser(data) {
    try {
        const res = await fetchWithTimeout(`${BASE_URL}/auth/login`, {
            method: "POST",
            headers: defaultHeaders,
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
        const res = await fetchWithTimeout(`${BASE_URL}/auth/register`, {
            method: "POST",
            headers: defaultHeaders,
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
        const res = await fetchWithTimeout(`${BASE_URL}/students/`);
        return await handleResponse(res);

    } catch (error) {
        console.error("Fetch Students Error:", error.message);
        return [];
    }
}


// ADD STUDENT
export async function addStudentAPI(data) {
    try {
        const res = await fetchWithTimeout(`${BASE_URL}/students/`, {
            method: "POST",
            headers: defaultHeaders,
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
        const res = await fetchWithTimeout(`${BASE_URL}/students/${id}`, {
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
        const res = await fetchWithTimeout(`${BASE_URL}/attendance/`, {
            method: "POST",
            headers: defaultHeaders,
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
        const res = await fetchWithTimeout(`${BASE_URL}/attendance/stats`);
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
        const res = await fetchWithTimeout(`${BASE_URL}/marks/`, {
            method: "POST",
            headers: defaultHeaders,
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
        const res = await fetchWithTimeout(`${BASE_URL}/marks/stats`);
        return await handleResponse(res);

    } catch (error) {
        console.error("Marks Stats Error:", error.message);
        return {
            avg_marks: 0,
            top_score: 0
        };
    }
}