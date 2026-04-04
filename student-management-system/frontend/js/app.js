// ================= BASE URL =================
const BASE_URL =
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:5000"
        : "https://student-management-system.onrender.com";


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


// ================= LOGIN =================
async function login(event) {
    event.preventDefault();

    const rollno = document.getElementById("rollno").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!rollno || !password) {
        alert("Enter Roll No & Password");
        return;
    }

    try {
        const res = await loginUser({ rollno, password });

        if (res.status === "success") {
            localStorage.setItem("user", JSON.stringify(res.student));
            window.location.href = "dashboard.html";
        } else {
            alert("Invalid credentials");
        }

    } catch (err) {
        alert("Server error");
    }
}


// ================= STUDENTS =================
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


// ================= ADD STUDENT =================
async function addStudent() {
    const name = document.getElementById("name").value.trim();
    const rollno = document.getElementById("roll").value.trim();
    const email = document.getElementById("email")?.value || "";

    if (!name || !rollno) {
        alert("Fill all fields");
        return;
    }

    await addStudentAPI({ name, rollno, email });

    clearInputs();
    loadStudents();
    loadDashboardStats();
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
            <td>${s.rollno}</td>

            <td>
                <button onclick="markAttendance(${s.id})">Present</button>
            </td>

            <td>
                <input type="number"
                onchange="updateMarks(${s.id}, this.value)">
            </td>
        `;

        list.appendChild(row);
    });
}


// ================= DASHBOARD =================
async function loadDashboardStats() {
    try {
        const students = await getStudents();
        document.getElementById("totalStudents").innerText = students.length;

        const att = await fetch(`${BASE_URL}/attendance/stats`).then(r => r.json());
        document.getElementById("attendance").innerText =
            (att.attendance_percentage || 0) + "%";

        const marks = await fetch(`${BASE_URL}/marks/stats`).then(r => r.json());
        document.getElementById("avgMarks").innerText = marks.avg_marks || 0;
        document.getElementById("topScore").innerText = marks.top_score || 0;

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
            total: 1,
            attended: 1
        })
    });

    loadDashboardStats();
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

    loadDashboardStats();
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
        loadDashboardStats();
    }
};