// ================= BASE URL =================

// 🔴 LOCAL
// const BASE_URL = "http://127.0.0.1:5000";

// 🟢 PRODUCTION (Render)
const BASE_URL = "https://your-backend-name.onrender.com";


// ================= COMMON FETCH =================
async function handleResponse(res) {
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
    }
    return res.json();
}


// ================= AUTH =================
async function loginUser(data) {
    const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return handleResponse(res);
}


// ================= STUDENT APIs =================
async function getStudents() {
    const res = await fetch(`${BASE_URL}/students/`);
    return handleResponse(res);
}

async function addStudentAPI(data) {
    const res = await fetch(`${BASE_URL}/students/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return handleResponse(res);
}

async function deleteStudentAPI(id) {
    const res = await fetch(`${BASE_URL}/students/${id}`, {
        method: "DELETE"
    });
    return handleResponse(res);
}


// ================= LOGIN =================
async function login(event) {
    event.preventDefault();

    const roll_no = document.getElementById("rollno").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!roll_no || !password) {
        alert("Enter Roll No & Password");
        return;
    }

    try {
        const res = await loginUser({ roll_no, password });

        if (res.message === "Login successful") {
            localStorage.setItem("user", JSON.stringify(res.user));
            window.location.href = "dashboard.html";
        } else {
            alert("Invalid credentials");
        }

    } catch (err) {
        alert("Server error");
    }
}


// ================= ADD STUDENT =================
async function addStudent() {
    const name = document.getElementById("name").value.trim();
    const roll_no = document.getElementById("roll").value.trim();
    const email = document.getElementById("email")?.value || "";

    if (!name || !roll_no) {
        alert("Fill all fields");
        return;
    }

    await addStudentAPI({ name, roll_no, email });

    clearInputs();
    loadStudents();
    loadDashboardStats(); // 🔥 refresh
}


// ================= LOAD STUDENTS =================
async function loadStudents() {
    const data = await getStudents();

    const list = document.getElementById("list");
    if (!list) return;

    list.innerHTML = "";

    data.forEach(s => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${s.name}</td>
            <td>${s.roll_no}</td>

            <td>
                <button onclick="markAttendance(${s.id})">
                    Present
                </button>
            </td>

            <td>
                <input type="number"
                onchange="updateMarks(${s.id}, this.value)">
            </td>

            <td>
                <button onclick="deleteStudent(${s.id})">
                    Delete
                </button>
            </td>
        `;

        list.appendChild(row);
    });
}


// ================= DASHBOARD =================
async function loadDashboardStats() {
    try {
        const students = await getStudents();

        document.getElementById("totalStudents").innerText =
            students.length;

        // attendance
        const attRes = await fetch(`${BASE_URL}/attendance/stats`);
        const att = await attRes.json();

        document.getElementById("attendance").innerText =
            (att.attendance_percentage || 0) + "%";

        // marks
        const marksRes = await fetch(`${BASE_URL}/marks/stats`);
        const marks = await marksRes.json();

        document.getElementById("avgMarks").innerText =
            marks.avg_marks || 0;

        document.getElementById("topScore").innerText =
            marks.top_score || 0;

    } catch (err) {
        console.error("Dashboard error", err);
    }
}


// ================= ATTENDANCE =================
async function markAttendance(id) {
    await fetch(`${BASE_URL}/attendance/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            student_id: id,
            total_classes: 1,
            attended_classes: 1
        })
    });

    loadDashboardStats(); // 🔥 update
}


// ================= MARKS =================
async function updateMarks(id, marks) {
    await fetch(`${BASE_URL}/marks/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            student_id: id,
            subject: "General",
            marks: Number(marks)
        })
    });

    loadDashboardStats(); // 🔥 update
}


// ================= DELETE =================
async function deleteStudent(id) {
    if (!confirm("Delete this student?")) return;

    await deleteStudentAPI(id);

    loadStudents();
    loadDashboardStats(); // 🔥 update
}


// ================= UTIL =================
function clearInputs() {
    document.getElementById("name").value = "";
    document.getElementById("roll").value = "";
    if (document.getElementById("email"))
        document.getElementById("email").value = "";
}


// ================= AUTO LOAD =================
window.onload = () => {
    if (window.location.pathname.includes("dashboard.html")) {
        loadStudents();
        loadDashboardStats(); // ✅ IMPORTANT
    }
};