// =========================================================
// 🔐 AUTH GUARD
// =========================================================
const token = localStorage.getItem("token");

if (!token) {
    logoutUser("Session expired. Please login again.");
}

function isValidJWT(token) {
    return token.split(".").length === 3;
}

if (!isValidJWT(token)) {
    logoutUser("Invalid token. Please login again.");
}

function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch {
        return null;
    }
}

const payload = parseJwt(token);

if (!payload) {
    logoutUser("Corrupted token. Please login again.");
}

const currentTime = Date.now() / 1000;

if (!payload.exp || payload.exp < currentTime) {
    logoutUser("Session expired. Please login again.");
}

// ✅ Save user safely
const user = {
    id: payload.identifier,
    role: payload.role
};

localStorage.setItem("user", JSON.stringify(user));


// =========================================================
// 🌐 BASE URL
// =========================================================
const BASE_URL =
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:5000"
        : "https://student-management-system-api-cznx.onrender.com";


// =========================================================
// 🔐 AUTH HEADER
// =========================================================
function getAuthHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}


// =========================================================
// 📌 LOAD STUDENTS (MAIN DATA)
// =========================================================
async function loadStudents() {
    const container = document.getElementById("studentsList");

    try {
        container.innerHTML = "⏳ Loading...";

        const res = await fetch(`${BASE_URL}/api/students`, {
            headers: getAuthHeaders()
        });

        if (res.status === 401) {
            logoutUser("Session expired");
            return;
        }

        const data = await res.json();

        if (!Array.isArray(data)) {
            throw new Error("Invalid data format");
        }

        if (data.length === 0) {
            container.innerHTML = "No students found.";
            return;
        }

        container.innerHTML = data.map(student => `
            <div class="student-card">
                <p><strong>Roll No:</strong> ${student.rollno}</p>
                <p><strong>Name:</strong> ${student.name}</p>
            </div>
        `).join("");

    } catch (err) {
        console.error(err);
        container.innerHTML = "❌ Failed to load students";
    }
}


// =========================================================
// 📅 LOAD ATTENDANCE
// =========================================================
async function loadAttendance() {
    try {
        const res = await fetch(`${BASE_URL}/api/attendance/stats/${user.id}`, {
            headers: getAuthHeaders()
        });

        if (res.status === 401) {
            logoutUser("Session expired");
            return;
        }

        const data = await res.json();

        document.getElementById("attendance").innerText =
            `Present: ${data.present || 0}, Absent: ${data.absent || 0}`;

    } catch (err) {
        console.error(err);
    }
}


// =========================================================
// 📊 LOAD MARKS
// =========================================================
async function loadMarks() {
    try {
        const res = await fetch(`${BASE_URL}/api/marks/stats/${user.id}`, {
            headers: getAuthHeaders()
        });

        if (res.status === 401) {
            logoutUser("Session expired");
            return;
        }

        const data = await res.json();

        document.getElementById("marks").innerText =
            JSON.stringify(data, null, 2);

    } catch (err) {
        console.error(err);
    }
}


// =========================================================
// 🚪 LOGOUT
// =========================================================
function logoutUser(message) {
    alert(message);
    localStorage.clear();
    window.location.href = "login.html";
}


// =========================================================
// 🚀 INIT
// =========================================================
document.addEventListener("DOMContentLoaded", () => {
    loadStudents();
    loadAttendance();
    loadMarks();
});