// =========================================================
// 🌐 BASE URL
// =========================================================
const BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/api"
    : "https://student-management-backend-if04.onrender.com/api";


// =========================================================
// 📌 DEFAULT HEADERS
// =========================================================
const defaultHeaders = {
  "Content-Type": "application/json"
};


// =========================================================
// ⏱️ FETCH WITH TIMEOUT
// =========================================================
function fetchWithTimeout(url, options = {}, timeout = 8000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  return fetch(url, {
    ...options,
    signal: controller.signal
  }).finally(() => clearTimeout(timer));
}


// =========================================================
// 📌 RESPONSE HANDLER
// =========================================================
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


// =========================================================
// 🔐 AUTH APIs
// =========================================================

// LOGIN
export async function loginUser(data) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: defaultHeaders,
      body: JSON.stringify(data)
    });

    const result = await handleResponse(res);

    if (result.status === "success") {
      localStorage.setItem("user", JSON.stringify(result.user)); // ✅ FIXED
    }

    return result;

  } catch (error) {
    return { status: "error", message: error.message };
  }
}


// REGISTER
export async function registerUser(data) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: defaultHeaders,
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
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/students/`);
    return await handleResponse(res);
  } catch {
    return [];
  }
}

export async function addStudentAPI(data) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/students/`, {
      method: "POST",
      headers: defaultHeaders,
      body: JSON.stringify(data)
    });

    return await handleResponse(res);
  } catch {
    return null;
  }
}

export async function deleteStudentAPI(rollno) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/students/${rollno}`, {
      method: "DELETE"
    });

    return await handleResponse(res);
  } catch {
    return null;
  }
}


// =========================================================
// 📅 ATTENDANCE APIs (FIXED)
// =========================================================

export async function markAttendanceAPI(rollno, date, status) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/attendance/mark`, {
      method: "POST",
      headers: defaultHeaders,
      body: JSON.stringify({ rollno, date, status })
    });

    return await handleResponse(res);
  } catch {
    return null;
  }
}

export async function getAttendanceStats(rollno) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/attendance/stats/${rollno}`);
    return await handleResponse(res);
  } catch {
    return { percentage: 0 };
  }
}


// =========================================================
// 📊 MARKS APIs (FIXED)
// =========================================================

export async function addMarksAPI(rollno, subject, marks) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/marks/update`, {
      method: "POST",
      headers: defaultHeaders,
      body: JSON.stringify({ rollno, subject, marks })
    });

    return await handleResponse(res);
  } catch {
    return null;
  }
}

export async function getMarksStats(rollno) {
  try {
    const res = await fetchWithTimeout(`${BASE_URL}/marks/stats/${rollno}`);
    return await handleResponse(res);
  } catch {
    return {
      average: 0,
      highest: 0
    };
  }
}


// =========================================================
// 🚪 LOGOUT
// =========================================================
export function logout() {
  localStorage.removeItem("user");
  window.location.href = "index.html";
}