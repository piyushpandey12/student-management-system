// ================= BASE URL =================
const BASE_URL =
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:5000"
        : "https://student-management-system-jg5j.onrender.com";


// ================= COMMON =================
async function handleResponse(res) {
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Request failed");
    }
    return res.json();
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
        const res = await fetch(`${BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rollno, password })
        });

        const data = await handleResponse(res);

        if (data.status === "success") {
            localStorage.setItem("user", JSON.stringify(data.student));
            window.location.href = "dashboard.html";
        } else {
            alert("Invalid credentials");
        }

    } catch {
        alert("Server error");
    }
}


// ================= GET STUDENTS =================
async function getStudents() {
    const res = await fetch(`${BASE_URL}/students`);
    return handleResponse(res);
}


// ================= ADD STUDENT =================
async function addStudent() {
    const name = document.getElementById("name").value.trim();
    const roll = document.getElementById("roll").value.trim();

    if (!name || !roll) {
        alert("Fill all fields");
        return;
    }

    await fetch(`${BASE_URL}/students`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, roll })
    });

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

    data.forEach((s) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${s.name}</td>
            <td>${s.roll}</td>

            <td>
                <input type="checkbox"
                onchange="markAttendance(${s.id})">
            </td>

            <td>
                <input type="number" value="${s.marks || 0}"
                onchange="updateMarks(${s.id}, this.value)">
            </td>

            <td>
                <button onclick="deleteStudent(${s.id})">Delete</button>
            </td>
        `;

        list.appendChild(row);
    });
}


// ================= DELETE =================
async function deleteStudent(id) {
    await fetch(`${BASE_URL}/students/${id}`, {
        method: "DELETE"
    });

    loadStudents();
    loadDashboardStats();
}


// ================= DASHBOARD =================
async function loadDashboardStats() {
    try {
        const students = await getStudents();
        document.getElementById("total").innerText = students.length;

        const att = await fetch(`${BASE_URL}/attendance/stats`).then(r => r.json());
        document.getElementById("att").innerText =
            (att.attendance_percentage || 0) + "%";

        const marks = await fetch(`${BASE_URL}/marks/stats`).then(r => r.json());
        document.getElementById("marks").innerText = marks.avg_marks || 0;
        document.getElementById("top").innerText = marks.top_score || 0;

    } catch (err) {
        console.error(err);
    }
}


// ================= ATTENDANCE =================
async function markAttendance(id) {
    await fetch(`${BASE_URL}/attendance`, {
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
    await fetch(`${BASE_URL}/marks`, {
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
}


// ================= AUTO LOAD =================
window.onload = () => {
    if (window.location.pathname.includes("dashboard.html")) {
        loadStudents();
        loadDashboardStats();
    }
};