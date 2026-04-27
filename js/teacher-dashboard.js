// =========================================================
// 🔐 AUTH GUARD (SAFE)
// =========================================================
function logoutUser(msg) {
  alert(msg);
  localStorage.clear();
  window.location.href = "teacher-login.html";
}

function getToken() {
  return localStorage.getItem("token");
}

function isValidJWT(token) {
  return token && token.split(".").length === 3;
}

function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch {
    return null;
  }
}

const token = getToken();
if (!token) logoutUser("Session expired");

if (!isValidJWT(token)) logoutUser("Invalid token");

const payload = parseJwt(token);
if (!payload) logoutUser("Corrupted token");

if (payload.exp && payload.exp < Date.now() / 1000) {
  logoutUser("Session expired");
}

// ✅ FIXED USER STRUCTURE
const user = {
  identifier: payload.identifier,
  role: payload.role
};

localStorage.setItem("user", JSON.stringify(user));


// =========================================================
// 🌐 BASE URL (FIXED)
// =========================================================
const BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/api"
    : "https://student-management-system-api-cznx.onrender.com/api";


// =========================================================
// 🔐 HEADERS + FETCH WRAPPER
// =========================================================
function getAuthHeaders() {
  const token = getToken();   // ✅ dynamic

  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...getAuthHeaders()
    }
  });

  if (res.status === 401) {
    logoutUser("Session expired");
    throw new Error("Unauthorized");
  }

  let data = {};
  try {
    data = await res.json();
  } catch {}

  if (!res.ok) {
    throw new Error(data.message || data.error || "Request failed");
  }

  return data;
}


// =========================================================
// 📌 LOAD STUDENTS
// =========================================================
async function loadStudents() {
  try {
    const data = await fetchJSON(`${BASE_URL}/students`);
    const students = data.data || [];

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
  }
}


// =========================================================
// ➕ ADD STUDENT
// =========================================================
window.addStudent = async () => {
  const name = document.getElementById("name").value.trim();
  const roll = document.getElementById("roll").value.trim();

  if (!name || !roll) return alert("Fill all fields");

  try {
    await fetchJSON(`${BASE_URL}/students`, {
      method: "POST",
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
    await fetchJSON(`${BASE_URL}/students/${roll}`, {
      method: "DELETE"
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
    await fetchJSON(`${BASE_URL}/attendance/mark`, {
      method: "POST",
      body: JSON.stringify({
        rollno: roll,
        date,
        status,
        teacher_id: user.identifier   // ✅ FIXED
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
    await fetchJSON(`${BASE_URL}/marks/update`, {
      method: "POST",
      body: JSON.stringify({
        rollno: roll,
        subject: "default",
        marks: Number(marks),
        teacher_id: user.identifier   // ✅ FIXED
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
// 🚀 INIT
// =========================================================
document.addEventListener("DOMContentLoaded", loadStudents);