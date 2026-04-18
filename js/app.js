// ================= BASE URL =================
const BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/api"
    : "https://student-management-backend-if04.onrender.com/api";


// ================= AUTH CHECK =================
const user = JSON.parse(localStorage.getItem("user"));

if (!user && window.location.pathname.includes("dashboard.html")) {
  window.location.href = "index.html";
}


// ================= COMMON =================
async function handleResponse(res) {
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || data.message);
  return data;
}


// ================= LOGIN =================
async function login(event) {
  event.preventDefault();

  const rollno = document.getElementById("rollno").value.trim();
  const password = document.getElementById("password").value.trim();

  try {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rollno, password })
    });

    const data = await handleResponse(res);

    localStorage.setItem("user", JSON.stringify(data.user)); // ✅ FIXED
    window.location.href = "dashboard.html";

  } catch (err) {
    alert(err.message);
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
  const rollno = document.getElementById("roll").value.trim();

  if (!name || !rollno) return alert("Fill all fields");

  const res = await fetch(`${BASE_URL}/students/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, rollno })
  });

  await handleResponse(res);

  clearInputs();
  loadStudents();
}


// ================= LOAD STUDENTS =================
async function loadStudents() {
  const data = await getStudents();
  const list = document.getElementById("list");

  list.innerHTML = "";

  data.forEach((s) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${s.name}</td>
      <td>${s.rollno}</td>

      <td>
        <input type="checkbox"
        onchange="markAttendance('${s.rollno}')">
      </td>

      <td>
        <input type="number" value="0"
        onchange="updateMarks('${s.rollno}', this.value)">
      </td>

      <td>
        <button onclick="deleteStudent('${s.rollno}')">Delete</button>
      </td>
    `;

    list.appendChild(row);
  });
}


// ================= DELETE =================
async function deleteStudent(rollno) {
  await fetch(`${BASE_URL}/students/${rollno}`, {
    method: "DELETE"
  });

  loadStudents();
}


// ================= ATTENDANCE =================
async function markAttendance(rollno) {
  const today = new Date().toISOString().split("T")[0];

  await fetch(`${BASE_URL}/attendance/mark`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      rollno,
      date: today,
      status: "present"
    })
  });
}


// ================= MARKS =================
async function updateMarks(rollno, marks) {
  await fetch(`${BASE_URL}/marks/update`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      rollno,
      subject: "Math", // default subject
      marks: Number(marks)
    })
  });
}


// ================= DASHBOARD =================
async function loadDashboardStats() {
  const students = await getStudents();

  document.getElementById("total").innerText = students.length;

  if (students.length > 0) {
    const rollno = students[0].rollno;

    const att = await fetch(`${BASE_URL}/attendance/stats/${rollno}`)
      .then(handleResponse);

    document.getElementById("att").innerText = att.percentage + "%";

    const marks = await fetch(`${BASE_URL}/marks/stats/${rollno}`)
      .then(handleResponse);

    document.getElementById("marks").innerText = marks.average;
    document.getElementById("top").innerText = marks.highest;
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