// ================= BASE URL =================
const BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/api"
    : "https://student-management-backend-if04.onrender.com/api";


// ================= AUTH CHECK =================
const user = localStorage.getItem("user");

if (!user && window.location.pathname.includes("dashboard.html")) {
    window.location.href = "index.html";
}


// ================= COMMON =================
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

        localStorage.setItem("user", JSON.stringify(data.student));
        window.location.href = "dashboard.html";

    } catch (err) {
        alert(err.message || "Invalid credentials ❌");
    }
}


// ================= GET STUDENTS =================
async function getStudents() {
    const res = await fetch(`${BASE_URL}/students/`);
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

    try {
        const res = await fetch(`${BASE_URL}/students/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                rollno: roll
            })
        });

        await handleResponse(res);

        clearInputs();
        loadStudents();
        loadDashboardStats();

    } catch (err) {
        alert(err.message || "Failed to add student");
    }
}


// ================= LOAD STUDENTS =================
async function loadStudents() {
    try {
        const data = await getStudents();
        const list = document.getElementById("list");

        if (!list) return;

        list.innerHTML = "";

        data.forEach((s) => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${s.name}</td>
                <td>${s.rollno}</td>

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

    } catch (err) {
        console.error("Load Students Error:", err.message);
    }
}


// ================= DELETE =================
async function deleteStudent(id) {
    try {
        const res = await fetch(`${BASE_URL}/students/${id}`, {
            method: "DELETE"
        });

        await handleResponse(res);

        loadStudents();
        loadDashboardStats();

    } catch (err) {
        alert(err.message || "Delete failed");
    }
}


// ================= DASHBOARD =================
async function loadDashboardStats() {
    try {
        const students = await getStudents();
        document.getElementById("total").innerText = students.length;

        const att = await fetch(`${BASE_URL}/attendance/stats`)
            .then(handleResponse);

        document.getElementById("att").innerText =
            (att.attendance_percentage || 0) + "%";

        const marks = await fetch(`${BASE_URL}/marks/stats`)
            .then(handleResponse);

        document.getElementById("marks").innerText = marks.avg_marks || 0;
        document.getElementById("top").innerText = marks.top_score || 0;

    } catch (err) {
        console.error(err);
    }
}


// ================= ATTENDANCE =================
async function markAttendance(id) {
    try {
        const res = await fetch(`${BASE_URL}/attendance/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id: id,
                total: 1,
                attended: 1
            })
        });

        await handleResponse(res);

        loadDashboardStats();

    } catch (err) {
        console.error("Attendance Error:", err.message);
    }
}


// ================= MARKS =================
async function updateMarks(id, marks) {
    try {
        const res = await fetch(`${BASE_URL}/marks/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                student_id: id,
                marks: Number(marks)
            })
        });

        await handleResponse(res);

        loadDashboardStats();

    } catch (err) {
        console.error("Marks Error:", err.message);
    }
}


// ================= LOGOUT =================
function logout() {
    localStorage.removeItem("user");
    window.location.href = "index.html";
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