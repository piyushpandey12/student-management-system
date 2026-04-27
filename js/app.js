// ================= BASE URL =================
const BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/api"
    : "https://student-management-system-api-cznx.onrender.com/api";


// ================= AUTH =================
function getUser() {
  try {
    return JSON.parse(localStorage.getItem("user"));
  } catch {
    return null;
  }
}

// 🔐 PROTECT DASHBOARD
if (
  (!localStorage.getItem("token") || !getUser()) &&
  window.location.pathname.includes("dashboard")
) {
  window.location.href = "index.html";
}


// ================= COMMON =================
async function handleResponse(res) {
  let data = {};
  try {
    data = await res.json();
  } catch {}

  // 🔥 HANDLE TOKEN EXPIRY
  if (res.status === 401) {
    alert("Session expired. Please login again.");
    logout();
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    throw new Error(data.message || data.error || "Something went wrong");
  }

  return data;
}

function getHeaders() {
  const token = localStorage.getItem("token");

  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}


// ================= LOGIN =================
async function login(event) {
  event.preventDefault();

  const rollno = document.getElementById("rollno").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!rollno || !password) {
    return alert("⚠️ Enter all fields");
  }

  try {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },

      // ✅ FIXED
      body: JSON.stringify({
        identifier: rollno,
        password
      })
    });

    const data = await handleResponse(res);

    // ✅ SAVE AUTH
    localStorage.setItem("user", JSON.stringify(data.user));
    localStorage.setItem("token", data.token);

    // ✅ REDIRECT
    if (data.user.role === "teacher") {
      window.location.href = "teacher-dashboard.html";
    } else {
      window.location.href = "student-dashboard.html";
    }

  } catch (err) {
    alert("❌ " + err.message);
  }
}


// ================= GET STUDENTS =================
async function getStudents() {
  const res = await fetch(`${BASE_URL}/students`, {
    headers: getHeaders()
  });
  return handleResponse(res);
}


// ================= ADD STUDENT =================
async function addStudent() {
  const name = document.getElementById("name").value.trim();
  const rollno = document.getElementById("roll").value.trim().toLowerCase();

  if (!name || !rollno) {
    return alert("⚠️ Fill all fields");
  }

  try {
    const res = await fetch(`${BASE_URL}/students`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ name, rollno })
    });

    await handleResponse(res);

    alert("✅ Student added");
    clearInputs();
    loadStudents();

  } catch (err) {
    alert("❌ " + err.message);
  }
}


// ================= LOAD STUDENTS =================
async function loadStudents() {
  try {
    const data = await getStudents();
    const list = document.getElementById("list");

    list.innerHTML = "";

    data.data?.forEach((s) => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${s.name}</td>
        <td>${s.rollno}</td>

        <td>
          <input type="checkbox"
          onchange="markAttendance('${s.rollno}')">
        </td>

        <td>
          <input type="number" value="${s.marks || 0}"
          onchange="updateMarks('${s.rollno}', this.value)">
        </td>

        <td>
          <button onclick="deleteStudent('${s.rollno}')">Delete</button>
        </td>
      `;

      list.appendChild(row);
    });

  } catch (err) {
    alert("❌ Failed to load students");
  }
}


// ================= DELETE =================
async function deleteStudent(rollno) {
  if (!confirm("Delete this student?")) return;

  try {
    await fetch(`${BASE_URL}/students/${rollno}`, {
      method: "DELETE",
      headers: getHeaders()
    });

    alert("✅ Deleted");
    loadStudents();

  } catch {
    alert("⚠️ Server error");
  }
}


// ================= ATTENDANCE =================
async function markAttendance(rollno) {
  const today = new Date().toISOString().split("T")[0];
  const user = getUser();

  try {
    await fetch(`${BASE_URL}/attendance/mark`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        rollno,
        date: today,
        status: "present",
        teacher_id: user?.identifier   // ✅ FIXED
      })
    });

    alert("✅ Attendance marked");

  } catch {
    alert("⚠️ Error marking attendance");
  }
}


// ================= MARKS =================
async function updateMarks(rollno, marks) {
  const user = getUser();

  try {
    await fetch(`${BASE_URL}/marks/update`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        rollno,
        subject: "Math",
        marks: Number(marks),
        teacher_id: user?.identifier   // ✅ FIXED
      })
    });

  } catch {
    alert("⚠️ Error updating marks");
  }
}


// ================= DASHBOARD =================
async function loadDashboardStats() {
  try {
    const studentsRes = await fetch(`${BASE_URL}/students`, {
      headers: getHeaders()
    });

    const studentsData = await handleResponse(studentsRes);
    const students = studentsData.data || [];

    document.getElementById("total").innerText = students.length;

    if (students.length > 0) {
      const rollno = students[0].rollno;

      const att = await fetch(`${BASE_URL}/attendance/stats/${rollno}`, {
        headers: getHeaders()
      }).then(handleResponse);

      document.getElementById("att").innerText =
        (att.percent || 0) + "%";

      const marks = await fetch(`${BASE_URL}/marks/stats/${rollno}`, {
        headers: getHeaders()
      }).then(handleResponse);

      document.getElementById("marks").innerText =
        marks.average || 0;

      document.getElementById("top").innerText =
        marks.highest || 0;
    }

  } catch {
    console.error("Dashboard load failed");
  }
}


// ================= LOGOUT =================
function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}


// ================= UTIL =================
function clearInputs() {
  document.getElementById("name").value = "";
  document.getElementById("roll").value = "";
}


// ================= AUTO LOAD =================
window.onload = () => {
  if (window.location.pathname.includes("dashboard")) {
    loadStudents();
    loadDashboardStats();
  }
};