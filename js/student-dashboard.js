// =========================================================
// 🔐 AUTH GUARD
// =========================================================
function logoutUser(message) {
  alert(message);
  localStorage.clear();
  window.location.href = "login.html";
}

function getToken() {
  return localStorage.getItem("token");
}

function isValidJWT(token) {
  return token && token.split(".").length === 3;
}

// Base64URL-safe decode
function parseJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map(c => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(json);
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

// normalized user object
const user = {
  identifier: payload.identifier,
  role: payload.role
};
localStorage.setItem("user", JSON.stringify(user));


// =========================================================
// 🌐 BASE URL (UNIFIED)
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
  const t = getToken();
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${t}`
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
// 📊 CHART INSTANCES
// =========================================================
let attendanceChart, marksChart;


// =========================================================
// 📌 LOAD STUDENTS (LIST)
// =========================================================
async function loadStudents() {
  const container = document.getElementById("studentsList");

  try {
    container.innerHTML = "⏳ Loading...";

    const data = await fetchJSON(`${BASE_URL}/students`);
    const students = data.data || [];

    if (students.length === 0) {
      container.innerHTML = "No students found.";
      return;
    }

    container.innerHTML = students.map(s => `
      <div class="student-card">
        <p><strong>Roll No:</strong> ${s.rollno}</p>
        <p><strong>Name:</strong> ${s.name}</p>
      </div>
    `).join("");

  } catch (err) {
    console.error(err);
    container.innerHTML = "❌ Failed to load students";
  }
}


// =========================================================
// 📊 DASHBOARD STATS + CHARTS
// =========================================================
async function loadDashboardStats() {
  try {
    const data = await fetchJSON(`${BASE_URL}/students`);
    const students = data.data || [];

    document.getElementById("total").innerText = students.length;

    if (students.length === 0) return;

    const rollno = students[0].rollno;

    // ===== ATTENDANCE =====
    const att = await fetchJSON(`${BASE_URL}/attendance/stats/${rollno}`);
    const present = att.present || 0;
    const absent = att.absent || 0;
    const percent = att.percent || 0;

    document.getElementById("att").innerText = percent + "%";

    // ===== MARKS =====
    const marks = await fetchJSON(`${BASE_URL}/marks/stats/${rollno}`);

    document.getElementById("marks").innerText = marks.average || 0;
    document.getElementById("top").innerText = marks.highest || 0;

    // ===== ATTENDANCE CHART =====
    const attCtx = document.getElementById("attendanceChart");
    if (attendanceChart) attendanceChart.destroy();

    attendanceChart = new Chart(attCtx, {
      type: "doughnut",
      data: {
        labels: ["Present", "Absent"],
        datasets: [{
          data: [present, absent]
        }]
      }
    });

    // ===== MARKS CHART =====
    const marksCtx = document.getElementById("marksChart");
    if (marksChart) marksChart.destroy();

    marksChart = new Chart(marksCtx, {
      type: "bar",
      data: {
        labels: ["Average", "Highest"],
        datasets: [{
          data: [marks.average || 0, marks.highest || 0]
        }]
      }
    });

  } catch (err) {
    console.error("Dashboard error:", err);
  }
}


// =========================================================
// 📅 OPTIONAL DETAIL SECTIONS
// =========================================================
async function loadAttendance() {
  try {
    const data = await fetchJSON(`${BASE_URL}/attendance/stats/${user.identifier}`);

    document.getElementById("attendance").innerText =
      `Present: ${data.present || 0}, Absent: ${data.absent || 0}`;

  } catch (err) {
    console.error(err);
  }
}

async function loadMarks() {
  try {
    const data = await fetchJSON(`${BASE_URL}/marks/stats/${user.identifier}`);

    document.getElementById("marksDetail").innerText =
      `Average: ${data.average || 0}, Highest: ${data.highest || 0}`;

  } catch (err) {
    console.error(err);
  }
}


// =========================================================
// 🚀 INIT
// =========================================================
document.addEventListener("DOMContentLoaded", () => {
  loadStudents();
  loadDashboardStats();
  loadAttendance();
  loadMarks();
});