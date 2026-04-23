// =========================================================
// 🔐 AUTH GUARD (FULL)
// =========================================================
const token = localStorage.getItem("token");

if (!token) logoutUser("Session expired");

function isValidJWT(token) {
  return token.split(".").length === 3;
}

if (!isValidJWT(token)) logoutUser("Invalid token");

function parseJwt(token) {
  try {
    const base64 = token.split('.')[1]
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

const payload = parseJwt(token);
if (!payload) logoutUser("Corrupted token");

const currentTime = Date.now() / 1000;
if (!payload.exp || payload.exp < currentTime) {
  logoutUser("Session expired");
}

// ✅ SAFE USER OBJECT
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
// 📌 LOAD STUDENTS
// =========================================================
async function loadStudents() {
  try {
    const res = await fetch(`${BASE_URL}/api/students`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) logoutUser("Session expired");

    const data = await res.json();
    const students = data.data || data || [];

    let html = "";

    students.forEach(s => {
      let grade = "C";
      if (s.avg_marks > 90) grade = "A";
      else if (s.avg_marks > 70) grade = "B";

      html += `
      <tr>
        <td>${s.rollno}</td>
        <td>${s.name}</td>
        <td>${s.avg_marks || 0}</td>
        <td class="${grade === "A" ? "gradeA" : grade === "B" ? "gradeB" : "gradeC"}">${grade}</td>
        <td><button onclick="deleteStudent('${s.rollno}')">Delete</button></td>
      </tr>`;
    });

    document.querySelector("#table tbody").innerHTML = html;

  } catch (err) {
    console.error(err);
    logoutUser("Session expired");
  }
}


// =========================================================
// ➕ ADD STUDENT (FIXED BUG)
// =========================================================
window.addStudent = async () => {
  const nameInput = document.getElementById("name");
  const rollInput = document.getElementById("roll");

  const name = nameInput.value.trim();
  const roll = rollInput.value.trim();

  if (!name || !roll) return alert("Fill all fields");

  try {
    await fetch(`${BASE_URL}/api/students`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ name, rollno: roll })
    });

    loadStudents();
  } catch {
    alert("Error adding student");
  }
};


// =========================================================
// ❌ DELETE STUDENT
// =========================================================
window.deleteStudent = async (roll) => {
  try {
    await fetch(`${BASE_URL}/api/students/${roll}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });

    loadStudents();
  } catch {
    alert("Delete failed");
  }
};


// =========================================================
// 📅 ATTENDANCE
// =========================================================
window.markAttendance = async () => {
  const roll = document.getElementById("rollAtt").value;
  const date = document.getElementById("date").value;
  const status = document.getElementById("status").value;

  try {
    await fetch(`${BASE_URL}/api/attendance/mark`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        rollno: roll,
        date,
        status,
        teacher_id: user.id   // ✅ FIXED
      })
    });

    alert("Attendance marked");
  } catch {
    alert("Error marking attendance");
  }
};


// =========================================================
// 📊 MARKS
// =========================================================
window.addMarks = async () => {
  const roll = document.getElementById("rollMarks").value;
  const marks = document.getElementById("marks").value;

  try {
    await fetch(`${BASE_URL}/api/marks/update`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        rollno: roll,
        subject: "default",
        marks,
        teacher_id: user.id   // ✅ FIXED
      })
    });

    alert("Marks updated");
  } catch {
    alert("Error updating marks");
  }
};


// =========================================================
// 🔍 SEARCH
// =========================================================
window.filterStudents = () => {
  const input = document.getElementById("search").value.toLowerCase();

  document.querySelectorAll("#table tbody tr").forEach(row => {
    row.style.display =
      row.innerText.toLowerCase().includes(input) ? "" : "none";
  });
};


// =========================================================
// 🚪 LOGOUT
// =========================================================
function logoutUser(msg) {
  alert(msg);
  localStorage.clear();
  window.location.href = "teacher-login.html";
}


// =========================================================
// 🚀 INIT
// =========================================================
document.addEventListener("DOMContentLoaded", loadStudents);