// =========================================================
// 🌐 BASE URL (ONLY ONCE ✅)
// =========================================================
const BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/api"
    : "https://student-management-system-api-cznx.onrender.com/api";


// =========================================================
// 🔐 AUTH HELPERS
// =========================================================
function getToken() {
  return localStorage.getItem("token");
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem("user"));
  } catch {
    return null;
  }
}

function getAuthHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + getToken()
  };
}


// =========================================================
// ⏱️ FETCH WITH TIMEOUT
// =========================================================
function fetchWithTimeout(url, options = {}, timeout = 10000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  return fetch(url, {
    ...options,
    signal: controller.signal
  }).finally(() => clearTimeout(timer));
}


// =========================================================
// 📌 RESPONSE HANDLER (FIXED)
// =========================================================
async function handleResponse(res) {
  const text = await res.text();

  console.log("RAW RESPONSE:", text);   // 🔥 DEBUG

  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error("Server not returning JSON → " + text);
  }

  if (!res.ok) {
    console.error("SERVER ERROR:", data); // 🔥 DEBUG
    throw new Error(data.message || data.error || "Server error");
  }

  return data;
}


// =========================================================
// 🔐 AUTH APIs
// =========================================================
export async function loginUser(data) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    const result = await handleResponse(res);

    if (result.status === "success") {
      localStorage.setItem("user", JSON.stringify(result.user));
      localStorage.setItem("token", result.token);
    }

    return result;

  } catch (error) {
    return { status: "error", message: error.message };
  }
}

export async function registerUser(data) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    return await handleResponse(res);

  } catch (error) {
    return { status: "error", message: error.message };
  }
}


// =========================================================
// 👨‍🎓 STUDENT APIs
// =========================================================
export async function getStudents() {
  const res = await fetchWithTimeout(`${BASE_URL}/students/`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}

export async function addStudentAPI(data) {
  console.log("ADDING STUDENT:", data); // 🔥 DEBUG

  const res = await fetchWithTimeout(`${BASE_URL}/students/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });

  return handleResponse(res);
}

export async function deleteStudentAPI(rollno) {
  const res = await fetchWithTimeout(`${BASE_URL}/students/${rollno}`, {
    method: "DELETE",
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}


// =========================================================
// 📅 ATTENDANCE APIs
// =========================================================
export async function markAttendanceAPI(rollno, date, status) {
  const user = getUser();
  if (!user) throw new Error("User not logged in");

  const res = await fetchWithTimeout(`${BASE_URL}/attendance/mark`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      rollno,
      date,
      status,
      teacher_id: user.identifier
    })
  });

  return handleResponse(res);
}

export async function getAttendanceStats(rollno) {
  const res = await fetchWithTimeout(`${BASE_URL}/attendance/stats/${rollno}`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}


// =========================================================
// 📊 MARKS APIs
// =========================================================
export async function addMarksAPI(rollno, subject, marks) {
  const user = getUser();
  if (!user) throw new Error("User not logged in");

  const res = await fetchWithTimeout(`${BASE_URL}/marks/update`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      rollno,
      subject,
      marks,
      teacher_id: user.identifier
    })
  });

  return handleResponse(res);
}

export async function getMarksStats(rollno) {
  const res = await fetchWithTimeout(`${BASE_URL}/marks/stats/${rollno}`, {
    headers: getAuthHeaders()
  });
  return handleResponse(res);
}


// =========================================================
// 🚪 LOGOUT
// =========================================================
export function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}