import {
  getStudents,
  addStudentAPI,
  deleteStudentAPI,
  markAttendanceAPI,
  addMarksAPI
} from "./api.js";

// AUTH
const user = JSON.parse(localStorage.getItem("user"));

if (!localStorage.getItem("token") || !user) {
  window.location.href = "teacher-login.html";
}

// LOAD STUDENTS
async function loadStudents() {
  try {
    const data = await getStudents();
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
    alert("Session expired");
    localStorage.clear();
    window.location.href = "teacher-login.html";
  }
}

// ADD STUDENT
window.addStudent = async () => {
  const name = name.value.trim();
  const roll = document.getElementById("roll").value.trim();

  if (!name || !roll) return alert("Fill all fields");

  await addStudentAPI({ name, rollno: roll });
  loadStudents();
};

// DELETE
window.deleteStudent = async (roll) => {
  await deleteStudentAPI(roll);
  loadStudents();
};

// ATTENDANCE
window.markAttendance = async () => {
  const roll = rollAtt.value;
  const date = date.value;
  const status = status.value;

  await markAttendanceAPI(roll, date, status);
  alert("Attendance marked");
};

// MARKS
window.addMarks = async () => {
  const roll = rollMarks.value;
  const marks = document.getElementById("marks").value;

  await addMarksAPI(roll, "default", marks);
  alert("Marks updated");
};

// SEARCH
window.filterStudents = () => {
  const input = document.getElementById("search").value.toLowerCase();

  document.querySelectorAll("#table tbody tr").forEach(row => {
    row.style.display =
      row.innerText.toLowerCase().includes(input) ? "" : "none";
  });
};

// INIT
loadStudents();