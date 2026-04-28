const BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000/api"
    : "https://student-management-system-api-cznx.onrender.com/api";

async function forgotPassword() {
  const teacherId = document.getElementById("teacherId").value.trim();

  if (!teacherId) {
    return showError("Enter Teacher ID first");
  }

  const newPassword = prompt("Enter new password (min 6 chars, letter + number):");

  if (!newPassword || !/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/.test(newPassword)) {
    return showError("Password must contain letter + number (min 6)");
  }

  try {
    const res = await fetch(`${BASE_URL}/auth/reset-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        identifier: teacherId,
        new_password: newPassword,
        role: "teacher"
      })
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.message || "Reset failed");
    }

    alert("✅ Password reset successful");

  } catch (err) {
    showError(err.message);
  }
}

// ================= SAFE AUTH =================
function getUser() {
  try {
    return JSON.parse(localStorage.getItem("user"));
  } catch {
    return null;
  }
}

const user = getUser();
const token = localStorage.getItem("token");

// 🔒 STRICT CHECK
if (
  token &&
  typeof token === "string" &&
  token.length > 10 &&
  user &&
  (user.role === "teacher" || user.role === "student")
) {
  window.location.href =
    user.role === "teacher"
      ? "teacher-dashboard.html"
      : "student-dashboard.html";
}
const containerEl = document.querySelector(".container");
const checkboxEl = document.querySelector(
  '.form-container .form-row input[type="checkbox"]',
);
const teacherIdEl = document.getElementById("teacherId");

const passwordEl = document.querySelector(
  '.form-container .form-row input[name="password"]',
);

const submitBtn = document.getElementById("submitBtn");

document.getElementById("submitBtn").addEventListener("click", async () => {
  if (submitBtn.disabled) return; // ✅ prevent invalid click

  const identifier = document.getElementById("teacherId").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorMsg = document.getElementById("errorMsg");

  errorMsg.innerText = "";

  if (!identifier || !password) {
    errorMsg.innerText = "⚠️ Please fill all fields";
    return;
  }

  try {
    errorMsg.innerText = "⏳ Logging in...";

    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        identifier,
        password,
      }),
    });

    let data;

    try {
      data = await res.json();
    } catch {
      throw new Error("Invalid server response");
    }

    if (!res.ok) {
      throw new Error(data.message || "Login failed");
    }

    // ✅ SAVE SESSION
    localStorage.setItem("token", data.token);
    localStorage.setItem("user", JSON.stringify(data.user));

    errorMsg.innerText = "✅ Login successful";

    setTimeout(() => {
      window.location.href = "teacher-dashboard.html";
    }, 700);
  } catch (err) {
    console.error("LOGIN ERROR:", err);
    errorMsg.innerText = "❌ " + err.message;
  }
});

const sprayer = document.querySelector(".sprayer");
const sprayHandContainer = document.querySelector(".spray-hand-container");
const sprayLines = Array.from(document.querySelectorAll(".spray-line"));
const sprayBubbles = Array.from(document.querySelectorAll(".spray-bubble"));

const pushingHand = document.querySelector(".pushing-hand");
const sprayerHead = document.querySelector(".sprayer-head");
const gearsContainer = document.querySelector("svg .gears");
const gearConnector = document.querySelector(".gear-connector");

const pullSystemContainer = document.querySelector(".pull-system");

const checkboxPullLine = document.querySelector(".checkbox-pull-line");
const checkboxPullCircle = document.querySelector(".checkbox-pull-circle");
const btnPullLine = document.querySelector(".submit-btn-connector");
const btnHandlerCircle = document.querySelector(".submit-btn-circle");

const spiralContainer = document.querySelector(".spiral-container");
const weightBigContainer = document.querySelector(".weight-big-container");

const scalesContainer = document.querySelector(".scales-container");
const scalesLine = document.querySelector(".scales-moving-line");
const weightBig = document.querySelector(".weight-big");
const spiralPath = document.querySelector(".spiral-path");

const carContainer = document.querySelector(".car-container");
const car = document.querySelector(".car");
const carInclineWrapper = document.querySelector(".car-container g");
const timingChains = Array.from(document.querySelectorAll(".timing-chain"));
const reelsConnector = document.querySelector(".reels-connector");
const carWeightConnector = document.querySelector(".car-weight-connector");

const grabbingHand = document.querySelectorAll(".grabbing-hand");
const grabbingHandOpenFingers = Array.from(
  document.querySelectorAll(".grabbing-hand-finger-open"),
);
const grabbingHandClosedFingers = Array.from(
  document.querySelectorAll(".grabbing-hand-finger-closed"),
);
// ✅ Password animation timeline (fix missing error)
const passwordTl = gsap.timeline({ paused: true });

passwordTl.to(passwordEl, {
  duration: 0.3,
  borderColor: "#00ff88",
  boxShadow: "0 0 10px #00ff88",
});

// ✅ Disable submit initially
submitBtn.disabled = true;

layoutPreparation();
scaleToFit();
window.onresize = scaleToFit;

function scaleToFit() {
  const h = 800;

  if (window.innerHeight < h) {
    gsap.set(containerEl, {
      scale: window.innerHeight / h,
      transformOrigin: "50% 75%",
    });
  }
}

let sprayRepeatCounter = 0;
const state = {
  handClosed: false,
  sumbitBtnOnPlace: false,

  pullProgress: 0,
};
let rollnoValid = false;
let passwordValid = false;

const emailTl = createEmailTl();
const gearsTls = createGearsTimelines();
let pullTl = createPullingTimeline(state.handClosed, checkboxEl.checked);

checkboxEl.addEventListener("change", () => {
  pullTl.kill();

  pullTl = createPullingTimeline(state.handClosed, checkboxEl.checked);

  pullTl.progress(1);

  checkForm();
});

teacherIdEl.addEventListener("input", () => {
  rollnoValid = /^[a-zA-Z0-9]{3,}$/.test(teacherIdEl.value);
  if (rollnoValid) {
    if (!state.handClosed) {
      emailTl.play();
    }

    gsap.to(teacherIdEl, {
      borderColor: "#00ff88",
      boxShadow: "0 0 8px #00ff88",
      duration: 0.3,
    });

    gearsTls.forEach((tl) => {
      if (tl.paused()) {
        tl.play();
        gsap.fromTo(tl, { timeScale: 0 }, { timeScale: 1 });
      }
    });
  } else {
    gsap.to(teacherIdEl, {
      borderColor: "#ff4d4d",
      boxShadow: "0 0 8px #ff4d4d",
      duration: 0.3,
    });

    gearsTls.forEach((tl) => {
      if (!tl.paused()) {
        gsap.to(tl, {
          timeScale: 0,
          onComplete: () => tl.pause(),
        });
      }
    });
  }

  checkForm();
});
passwordEl.addEventListener("input", () => {
  // ✅ Strong password: letters + number, min 6
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;
  passwordValid = passwordRegex.test(passwordEl.value);

  if (passwordValid) {
    passwordTl.play(); // safe now
    passwordEl.classList.add("valid");
  } else {
    passwordTl.reverse();
    passwordEl.classList.remove("valid");
  }

  checkForm(); // ✅ important
});

function layoutPreparation() {
  gsap.set(pullSystemContainer, {
    x: 375,
    y: 646,
  });
  gsap.set(sprayHandContainer, {
    x: 700,
    y: 621,
  });
  gsap.set(sprayer, {
    x: -59.5,
    y: 53,
  });
  gsap.set(carContainer, {
    x: 190,
    y: 802,
  });
  gsap.set(scalesContainer, {
    x: 170,
    y: 710,
  });
  gsap.set(grabbingHand, {
    x: 297,
    y: 830,
  });
  gsap.set(grabbingHandClosedFingers, {
    opacity: 0,
  });
  gsap.set(spiralContainer, {
    x: 305,
    y: 435,
    svgOrigin: "14 14",
    scaleX: -1,
  });
  gsap.set(weightBigContainer, {
    x: 305,
    y: 435,
  });

  gsap.set([sprayLines, sprayBubbles], {
    opacity: 0,
  });
  gsap.set(timingChains[0], {
    attr: {
      "stroke-width": "5",
      "stroke-dasharray": "0 12",
    },
  });
  gsap.set(timingChains[1], {
    attr: {
      "stroke-width": "5",
      "stroke-dasharray": "0 12",
    },
  });
  gsap.set(checkboxPullLine, {
    attr: {
      y1: -105,
      y2: 44,
    },
  });
  gsap.set(submitBtn, {
    transformOrigin: "100% 0%",
    rotation: -90,
  });
  gsap.set(checkboxPullCircle, {
    y: 44,
  });
}

function updateSpiralPath(centerX, centerY, radius, coils, points, offset) {
  let path = "";
  let thetaMax = coils * 2 * Math.PI;
  const awayStep = radius / thetaMax;
  const chord = (2 * Math.PI) / points;
  thetaMax -= offset * points * chord;

  for (let theta = 0; theta <= thetaMax; theta += chord) {
    const away = awayStep * theta;
    const x = centerX + Math.cos(theta) * away;
    const y = centerY + Math.sin(theta) * away;

    if (theta === 0) {
      path += `M${x},${y}`;
    } else {
      const prevAway = awayStep * (theta - chord);
      const arcRadius = (away + prevAway) / 2;
      path += ` A${arcRadius},${arcRadius} 0 0,1 ${x},${y}`;
    }
  }

  const outerAngle = thetaMax + 0.5 * Math.PI;
  const outerLength = 50 + 25 * offset;
  const endPoint = [
    Math.cos(outerAngle) * outerLength,
    Math.sin(outerAngle) * outerLength,
  ];
  path += " l" + endPoint[0] + "," + endPoint[1];

  gsap.set(spiralPath, {
    attr: {
      d: path,
    },
  });
  gsap.set(weightBig, {
    x: -47 + 3 * offset,
    y: 12 + outerLength,
  });
}

function createEmailTl() {
  const spiralTurnsNumber = 8;
  const spiralProgress = { v: 0 };
  const hammerTimeStart = 1.85;
  const fingersDelay = 0.5;
  const fingersTimeDelta = 0.03;
  const tl = gsap
    .timeline({
      paused: true,
      defaults: {
        ease: "none",
        duration: 2,
      },
      onUpdate: () => {
        updateSpiralPath(
          14,
          14,
          45,
          17,
          200,
          spiralTurnsNumber * spiralProgress.v,
        );
      },
    })
    .to(
      spiralProgress,
      {
        v: 1,
      },
      0,
    )
    .to(
      spiralContainer,
      {
        rotation: -spiralTurnsNumber * 360,
      },
      0,
    )

    .fromTo(
      scalesLine,
      {
        rotation: -20,
        svgOrigin: "92 20",
      },
      {
        duration: 0.15,
        rotation: -1,
        svgOrigin: "92 20",
      },
      hammerTimeStart,
    )

    .fromTo(
      timingChains[0],
      {
        attr: {
          "stroke-dashoffset": 2,
        },
      },
      {
        duration: 0.15,
        attr: {
          "stroke-dashoffset": 20,
        },
      },
      hammerTimeStart,
    )
    .fromTo(
      timingChains[1],
      {
        attr: {
          "stroke-dashoffset": 24,
        },
      },
      {
        duration: 0.15,
        attr: {
          "stroke-dashoffset": 6,
        },
      },
      hammerTimeStart,
    )
    .to(
      reelsConnector,
      {
        duration: 0.15,
        y: 18,
      },
      hammerTimeStart,
    )
    .to(
      carWeightConnector,
      {
        duration: 0.15,
        y: -18,
      },
      hammerTimeStart,
    )
    .to(
      carInclineWrapper,
      {
        duration: 0.15,
        rotation: 6,
        svgOrigin: "120 93",
      },
      hammerTimeStart,
    )
    .fromTo(
      car,
      {
        x: -50,
      },
      {
        duration: 0.6,
        x: 95,
        ease: "power2.in",
      },
      hammerTimeStart,
    );
  for (let i = 0; i < 5; i++) {
    tl.set(
      grabbingHandOpenFingers[i],
      {
        opacity: 0,
      },
      hammerTimeStart + fingersDelay + fingersTimeDelta * (i + 1),
    ).set(
      grabbingHandClosedFingers[i],
      {
        opacity: 1,
      },
      hammerTimeStart + fingersDelay + fingersTimeDelta * (i + 1),
    );
  }
  tl.fromTo(
    state,
    {
      handClosed: false,
    },
    {
      duration: 0.01,
      handClosed: true,
    },
    ">",
  ).to(
    grabbingHand,
    {
      duration: fingersTimeDelta * 5,
      x: "+=20",
    },
    hammerTimeStart + fingersDelay,
  );

  tl.progress(0.001);

  return tl;
}

function createGearsTimelines() {
  const tls = [];

  const params = {
    baseSize: 15,
    pitch: 11,
    teethCurve: 0.6,
    startPos: { x: 634, y: 389 },
    speed: 0.2,
  };
  const data = [
    {
      angle: 0,
      teethNumber: 10,
      hasHole: true,
    },
    {
      angle: -0.5,
      teethNumber: 32,
      hasHole: true,
    },
    {
      angle: 1.65,
      teethNumber: 12,
      hasHole: false,
    },
  ];

  const handleRadius = 14;

  const gears = [];
  data.forEach((d, dIdx) => {
    const radius = (d.teethNumber * params.baseSize) / (2 * Math.PI);
    let x, y, startAngle;

    if (dIdx === 0) {
      startAngle = 0;
      x = params.startPos.x;
      y = params.startPos.y;
    } else {
      const parent = gears[dIdx - 1];

      const size = parent.teethNumber / d.teethNumber;

      x = parent.center.x + Math.cos(d.angle) * (parent.radius + radius);
      y = parent.center.y + Math.sin(d.angle) * (parent.radius + radius);

      startAngle = (1 + size) * d.angle - size * parent.angle;
    }

    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    gearsContainer.appendChild(group);
    group.appendChild(path);

    const gear = {
      idx: dIdx,
      center: { x, y },
      radius,
      angle: startAngle,
      teethNumber: d.teethNumber,
      hasHole: d.hasHole,
      toothAngle: (2 * Math.PI) / d.teethNumber,
      toothCurveAngle: params.teethCurve / d.teethNumber,
      group,
    };

    const rOut = gear.radius + 0.25 * params.pitch;
    const rIn = rOut - 0.75 * params.pitch;
    let pathD =
      "M" +
      (gear.center.x +
        Math.cos(gear.angle - gear.toothAngle + gear.toothCurveAngle) * rOut) +
      ", " +
      (gear.center.y +
        Math.sin(gear.angle - gear.toothAngle + gear.toothCurveAngle) * rOut) +
      " ";
    for (
      let a = gear.angle;
      a < gear.angle + 2 * Math.PI - 0.5 * gear.toothAngle;
      a += gear.toothAngle
    ) {
      const pa = a - 0.5 * gear.toothAngle;
      pathD +=
        "L" +
        (gear.center.x + Math.cos(pa - gear.toothCurveAngle) * rOut) +
        ", " +
        (gear.center.y + Math.sin(pa - gear.toothCurveAngle) * rOut) +
        " ";
      pathD +=
        "L" +
        (gear.center.x + Math.cos(pa) * rIn) +
        ", " +
        (gear.center.y + Math.sin(pa) * rIn) +
        " ";
      pathD +=
        "L" +
        (gear.center.x + Math.cos(a) * rIn) +
        ", " +
        (gear.center.y + Math.sin(a) * rIn) +
        " ";
      pathD +=
        "L" +
        (gear.center.x + Math.cos(a + gear.toothCurveAngle) * rOut) +
        ", " +
        (gear.center.y + Math.sin(a + gear.toothCurveAngle) * rOut) +
        " ";
    }

    if (gear.hasHole) {
      const holeRadius = 0.5 * rIn;
      pathD += "M" + (gear.center.x - holeRadius) + ", " + gear.center.y + " ";
      pathD += `A ${holeRadius} ${holeRadius} 1 1 0 ${gear.center.x + holeRadius} ${gear.center.y}`;
      pathD += `A ${holeRadius} ${holeRadius} 1 1 0 ${gear.center.x - holeRadius} ${gear.center.y}`;
    }

    if (dIdx === 0) {
      const circle = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "circle",
      );
      gsap.set(circle, {
        attr: {
          cx: gear.center.x,
          cy: gear.center.y,
          r: 5,
          fill: "#000000",
        },
      });
      gearsContainer.appendChild(circle);
      gsap.set(path, {
        attr: {
          fill: "#000000",
          "fill-opacity": 0.25,
        },
      });
    } else if (dIdx === data.length - 1) {
      gsap.set(path, {
        attr: {
          fill: "#000000",
          "fill-opacity": 0.25,
        },
      });
      const circle = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "circle",
      );
      gsap.set(circle, {
        attr: {
          cx: gear.center.x + handleRadius,
          cy: gear.center.y,
          r: 5,
          fill: "#000000",
        },
      });
      gear.group.appendChild(circle);
    }

    path.setAttribute("d", pathD);

    const tl = gsap
      .timeline({
        repeat: -1,
        paused: true,
      })
      .to(group, {
        duration: params.speed * gear.teethNumber,
        rotation: 360 * (gear.idx % 2 ? -1 : 1),
        svgOrigin: gear.center.x + " " + gear.center.y,
        ease: "none",
      });

    if (dIdx === data.length - 1) {
      tl.eventCallback("onUpdate", () => {
        const angle = tl.progress() * 2 * Math.PI;
        const deltaY = Math.sin(angle) * handleRadius;
        gsap.set(pushingHand, {
          y: deltaY,
        });
        if (deltaY > 8) {
          const d = Math.max(0, deltaY - 8);
          gsap.set(sprayerHead, {
            y: d,
          });

          let sprayProgress = Math.max(0, tl.progress() - 0.1);
          sprayProgress *= 1 / 0.2;

          let bubblesOpacity = sprayProgress > 1 ? 0 : sprayProgress;
          bubblesOpacity *= 1 - Math.pow(bubblesOpacity, 8);

          gsap.set(sprayLines, {
            attr: {
              "stroke-dashoffset": 70 * sprayProgress,
            },
            opacity: Math.pow(bubblesOpacity, 2),
          });
          sprayBubbles.forEach((b, bIdx) => {
            gsap.set(b, {
              x: 25 * (1 - sprayProgress) * (1 + 0.1 * bIdx),
              scale: 0.5 + 1.4 * Math.pow(sprayProgress, 2),
              transformOrigin: "center center",
              opacity: bubblesOpacity,
            });
          });
        }

        gsap.set(gearConnector, {
          attr: {
            x1: gear.center.x + handleRadius * Math.cos(angle),
            y1: gear.center.y + handleRadius * Math.sin(angle),
            x2: 700 + 18,
            y2: 646 - 100 + deltaY,
          },
        });
      });

      tl.eventCallback("onRepeat", () => {
        if (!state.sumbitBtnOnPlace) {
          sprayRepeatCounter++;
        }
      });
    }

    tl.progress(0.6);
    tls.push(tl);
    gears.push(gear);
  });

  return tls;
}

function createPullingTimeline(isFixed, BtnPulled) {
  let tl = gsap.timeline({
    // paused: true,
    defaults: {
      ease: "power1.inOut",
      duration: 1,
    },
    onUpdate: animatePullingLine,
  });

  if (isFixed && BtnPulled) {
    tl.to(
      state,
      {
        pullProgress: 1,
      },
      0,
    )
      .to(
        submitBtn,
        {
          rotation: 0,
        },
        0,
      )
      .to(
        state,
        {
          duration: 0.1,
          sumbitBtnOnPlace: 1,
        },
        0.9,
      )
      .to(
        checkboxPullLine,
        {
          attr: { y2: 44 - 130 },
        },
        0,
      )
      .to(
        checkboxPullCircle,
        {
          y: 44 - 130,
        },
        0,
      );
  } else if (!isFixed && BtnPulled) {
    tl.to(
      state,
      {
        pullProgress: 1,
      },
      0,
    )
      .to(
        checkboxPullLine,
        {
          attr: { y2: 44 - 130 },
        },
        0,
      )
      .to(
        checkboxPullCircle,
        {
          y: 44 - 130,
        },
        0,
      );
  } else if (isFixed && !BtnPulled) {
    tl.to(
      state,
      {
        pullProgress: 0,
      },
      0,
    )
      .to(
        submitBtn,
        {
          rotation: -90,
        },
        0,
      )
      .to(
        state,
        {
          duration: 0.1,
          sumbitBtnOnPlace: 0,
        },
        0,
      )
      .to(
        checkboxPullLine,
        {
          attr: { y2: 44 },
        },
        0,
      )
      .to(
        checkboxPullCircle,
        {
          y: 44,
        },
        0,
      );
  } else if (!isFixed && !BtnPulled) {
    tl.to(
      state,
      {
        pullProgress: 0,
      },
      0,
    )
      .to(
        checkboxPullLine,
        {
          attr: { y2: 44 },
        },
        0,
      )
      .to(
        checkboxPullCircle,
        {
          y: 44,
        },
        0,
      );
  }

  function animatePullingLine() {
    const buttonOriginPoint = [260, -76];
    const btnWidth = 270;

    const deg = ((gsap.getProperty(submitBtn, "rotation") - 4) * Math.PI) / 180;

    const btnEnd = [
      buttonOriginPoint[0] - (btnWidth - 20) * Math.cos(deg),
      buttonOriginPoint[1] - (btnWidth - 20) * Math.sin(deg),
    ];
    gsap.set(btnHandlerCircle, {
      attr: {
        cx: btnEnd[0],
        cy: btnEnd[1],
      },
    });

    const handle = 7;
    const r = 10;

    let btnPullLinePath =
      "M" +
      (-r - handle) +
      "," +
      (250 - (isFixed ? 0 : state.pullProgress * 300));
    btnPullLinePath += "h" + 2 * handle;
    btnPullLinePath += "h" + -handle;
    btnPullLinePath += " V" + (44 - state.pullProgress * 130);
    const slideAngle =
      0.3 * Math.PI * (1 - (isFixed ? 1 : 0.5) * state.pullProgress);
    const dx = r * Math.cos(slideAngle);
    const dy = -r * Math.sin(slideAngle);
    btnPullLinePath += "a" + r + ", " + r + " 0 0 1 " + (r + dx) + " " + dy;
    btnPullLinePath += " L" + btnEnd[0] + "," + btnEnd[1];

    gsap.set(btnPullLine, {
      attr: {
        d: btnPullLinePath,
      },
      strokeWidth: 3,
    });
  }

  return tl;
}

function checkForm() {
  const isValid = rollnoValid && passwordValid && checkboxEl.checked;

  submitBtn.disabled = !isValid;

  gsap.killTweensOf(submitBtn);

  gsap.to(submitBtn, {
    opacity: isValid ? 1 : 0.3,
    pointerEvents: isValid ? "auto" : "none",
    color: isValid ? "#000" : "transparent",
    duration: 0.3,
  });
}
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("forgotBtn");

  if (!btn) {
    console.error("❌ forgotBtn not found in DOM");
    return;
  }

  btn.addEventListener("click", forgotPassword);
});