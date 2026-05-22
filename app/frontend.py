from __future__ import annotations

import json
from html import escape
from typing import Any

from .framework import Router, HTTPException
from .store import lesson_summary


router = Router()


def _page_shell(title: str, body: str, script: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f1e8;
      --bg-soft: #ece2d5;
      --card: rgba(255, 255, 255, 0.82);
      --card-border: rgba(47, 34, 20, 0.1);
      --text: #20150f;
      --muted: #6a5a4c;
      --accent: #d96f32;
      --accent-strong: #a84f1f;
      --accent-soft: rgba(217, 111, 50, 0.15);
      --success: #2d8a5d;
      --warning: #b86e12;
      --shadow: 0 22px 60px rgba(53, 31, 13, 0.14);
      --radius: 24px;
    }}

    * {{ box-sizing: border-box; }}

    html {{ scroll-behavior: smooth; }}

    body {{
      margin: 0;
      font-family: "Aptos", "Segoe UI", "Trebuchet MS", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(217, 111, 50, 0.22), transparent 34%),
        radial-gradient(circle at top right, rgba(95, 137, 201, 0.16), transparent 28%),
        linear-gradient(180deg, var(--bg), #f9f7f3 38%, #f2ece3 100%);
      min-height: 100vh;
    }}

    a {{ color: inherit; text-decoration: none; }}

    .shell {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }}

    .topbar {{
      display: flex;
      gap: 18px;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 26px;
    }}

    .brand {{ display: flex; flex-direction: column; gap: 6px; }}

    .brand strong {{
      font-size: 1.15rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}

    .brand span {{ color: var(--muted); max-width: 60ch; }}

    .nav {{ display: flex; gap: 10px; flex-wrap: wrap; }}

    .nav a {{
      padding: 10px 14px;
      border: 1px solid var(--card-border);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.6);
      transition: transform 0.18s ease, background 0.18s ease;
    }}

    .nav a:hover {{ transform: translateY(-1px); background: white; }}

    .hero, .card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
    }}

    .hero {{ padding: 28px; margin-bottom: 22px; }}
    .hero h1 {{ margin: 0 0 10px; font-size: clamp(2rem, 4vw, 3.6rem); line-height: 1.02; }}
    .hero p {{ margin: 0; color: var(--muted); font-size: 1.02rem; max-width: 66ch; }}

    .grid {{ display: grid; gap: 18px; }}
    .grid.dashboard {{ grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
    .grid.lesson {{ grid-template-columns: minmax(0, 1.45fr) minmax(280px, 0.85fr); align-items: start; }}
    @media (max-width: 980px) {{ .grid.lesson {{ grid-template-columns: 1fr; }} }}

    .card {{ padding: 22px; }}
    .card h2, .card h3 {{ margin: 0 0 12px; }}
    .card p {{ color: var(--muted); line-height: 1.55; }}

    .stat {{ display: grid; gap: 6px; }}
    .stat strong {{ font-size: 2rem; line-height: 1; }}
    .stat span {{ color: var(--muted); }}

    .meter {{
      width: 100%;
      height: 12px;
      border-radius: 999px;
      background: rgba(32, 21, 15, 0.08);
      overflow: hidden;
      margin-top: 10px;
    }}

    .meter > div {{
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--accent), #f39a54);
      width: 0%;
      transition: width 0.3s ease;
    }}

    .pill-row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }}

    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent-strong);
      font-weight: 600;
    }}

    .badge-row {{ display: flex; flex-wrap: wrap; gap: 10px; }}

    .badge {{
      padding: 10px 14px;
      border-radius: 16px;
      background: rgba(45, 138, 93, 0.12);
      color: #205b3e;
      border: 1px solid rgba(45, 138, 93, 0.18);
    }}

    .muted {{ color: var(--muted); }}

    .plan-grid {{
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      margin-top: 18px;
    }}

    .plan {{ padding: 20px; border-radius: 20px; border: 1px solid var(--card-border); background: rgba(255, 255, 255, 0.78); }}
    .plan strong {{ font-size: 1.15rem; }}
    .plan .price {{ font-size: 2rem; font-weight: 800; margin: 12px 0; }}

    button, .button {{
      appearance: none;
      border: none;
      border-radius: 14px;
      padding: 12px 16px;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.18s ease, filter 0.18s ease, background 0.18s ease;
    }}

    button:hover, .button:hover {{ transform: translateY(-1px); }}
    button:disabled {{ cursor: not-allowed; opacity: 0.65; transform: none; }}

    .button.primary, button.primary {{ background: var(--accent); color: white; }}
    .button.secondary, button.secondary {{ background: rgba(32, 21, 15, 0.08); color: var(--text); }}
    .button.ghost, button.ghost {{ background: transparent; color: var(--accent-strong); border: 1px solid rgba(168, 79, 31, 0.24); }}

    .outline {{ display: grid; gap: 14px; }}
    .section {{
      padding: 18px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid var(--card-border);
    }}

    .lesson-list {{ display: grid; gap: 12px; margin-top: 14px; }}
    .lesson-item {{
      display: flex;
      gap: 12px;
      justify-content: space-between;
      align-items: center;
      padding: 14px 16px;
      border-radius: 16px;
      background: white;
      border: 1px solid rgba(32, 21, 15, 0.08);
    }}

    .lesson-meta {{ display: grid; gap: 4px; }}
    .lesson-meta strong {{ font-size: 1rem; }}

    .lock {{ color: var(--warning); font-weight: 700; }}
    .success {{ color: var(--success); font-weight: 700; }}

    .video {{ width: 100%; border-radius: 22px; overflow: hidden; background: #100b08; border: 1px solid rgba(32, 21, 15, 0.14); }}
    video {{ width: 100%; display: block; aspect-ratio: 16 / 9; background: #100b08; }}

    .stack {{ display: grid; gap: 16px; }}

    .quiz {{ display: grid; gap: 14px; }}
    .question {{
      padding: 16px;
      border-radius: 18px;
      background: rgba(246, 241, 232, 0.78);
      border: 1px solid rgba(32, 21, 15, 0.08);
    }}

    .question h4 {{ margin: 0 0 10px; }}
    .question label {{ display: flex; gap: 10px; align-items: center; margin: 8px 0; }}

    .toast {{
      position: fixed;
      right: 18px;
      bottom: 18px;
      min-width: 280px;
      max-width: min(360px, calc(100vw - 36px));
      padding: 14px 16px;
      border-radius: 16px;
      background: #1e1712;
      color: white;
      box-shadow: var(--shadow);
      opacity: 0;
      transform: translateY(12px);
      pointer-events: none;
      transition: opacity 0.2s ease, transform 0.2s ease;
    }}

    .toast.show {{ opacity: 1; transform: translateY(0); }}

    .overlay {{
      position: fixed;
      inset: 0;
      z-index: 20;
      display: grid;
      place-items: center;
      padding: 24px;
      background: rgba(19, 11, 7, 0.74);
      backdrop-filter: blur(10px);
    }}

    .overlay[hidden] {{ display: none; }}

    .overlay-card {{
      width: min(620px, 100%);
      padding: 28px;
      border-radius: 28px;
      background: rgba(255, 246, 238, 0.98);
      box-shadow: 0 28px 80px rgba(0, 0, 0, 0.32);
      border: 1px solid rgba(255, 255, 255, 0.24);
      text-align: center;
    }}

    .overlay-card h2 {{ margin-top: 0; }}

    .countdown {{
      display: grid;
      gap: 6px;
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(217, 111, 50, 0.12);
      border: 1px solid rgba(217, 111, 50, 0.18);
      margin-bottom: 16px;
    }}

    .countdown strong {{ font-size: 1.5rem; }}
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <strong>Nano Lab Academy</strong>
        <span>Freemium course flow, lessons, quizzes, assignments, and progress tracking.</span>
      </div>
      <nav class="nav">
        <a href="/dashboard">Dashboard</a>
        <a href="/courses">Courses</a>
        <a href="/stage-2">Stage 2</a>
        <a href="/stage-3">Stage 3</a>
      </nav>
    </header>
    {body}
  </div>
  <div id="toast" class="toast"></div>
  <script>
    const toast = document.getElementById("toast");
    function showToast(message) {{
      if (!toast) return;
      toast.textContent = message;
      toast.classList.add("show");
      clearTimeout(window.__toastTimer);
      window.__toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
    }}
    async function fetchJSON(url, options = {{}}) {{
      const response = await fetch(url, {{
        headers: {{ "Content-Type": "application/json", ...(options.headers || {{}}) }},
        ...options,
      }});
      const data = await response.json();
      if (!response.ok) {{
        throw new Error(data.detail || "Request failed");
      }}
      return data;
    }}
    async function postJSON(url, payload) {{
      return fetchJSON(url, {{ method: "POST", body: JSON.stringify(payload || {{}}) }});
    }}
    {script}
  </script>
</body>
</html>"""


@router.get("/dashboard")
def dashboard_page() -> str:
    body = """
    <main class="stack">
      <section class="hero">
        <h1>Your progress, plans, and rewards in one view.</h1>
        <p>The dashboard loads enrollment and gamification data from the live API so it always reflects your current learning state.</p>
      </section>
      <section class="card countdown">
        <span>Stage 1 deadline</span>
        <strong id="stage-countdown">Loading...</strong>
        <span class="muted" id="stage-countdown-detail">Checking availability</span>
      </section>
      <section id="dashboard-root" class="stack"></section>
    </main>
    <div id="stage-lock-overlay" class="overlay" hidden>
      <div class="overlay-card">
        <h2>Stage 1 expired, pay to continue</h2>
        <p>Stage 1 access has ended. Unlock the remaining stages to keep moving through the academy.</p>
        <button class="primary" id="pay-stage-unlock">Pay to continue</button>
      </div>
    </div>
    """
    script = """
    const root = document.getElementById("dashboard-root");
    const overlay = document.getElementById("stage-lock-overlay");
    const countdown = document.getElementById("stage-countdown");
    const countdownDetail = document.getElementById("stage-countdown-detail");
    const payStageUnlock = document.getElementById("pay-stage-unlock");
    const plans = [
      { id: "free", name: "Free", price: "$0", description: "Access the starter track and unlock the upgrade flow later." },
      { id: "pro", name: "Pro", price: "$29", description: "Unlock all lessons and keep the full outline available." },
    ];

    function formatCountdown(totalSeconds) {
      const safeSeconds = Math.max(0, Math.floor(totalSeconds));
      const days = Math.floor(safeSeconds / 86400);
      const hours = Math.floor((safeSeconds % 86400) / 3600);
      const minutes = Math.floor((safeSeconds % 3600) / 60);
      const seconds = safeSeconds % 60;
      return `${days}d ${hours.toString().padStart(2, "0")}h ${minutes.toString().padStart(2, "0")}m ${seconds.toString().padStart(2, "0")}s`;
    }

    function updateCountdown(deadlineIso) {
      const deadline = new Date(deadlineIso);
      const tick = () => {
        const remaining = Math.max(0, Math.floor((deadline.getTime() - Date.now()) / 1000));
        countdown.textContent = formatCountdown(remaining);
        countdownDetail.textContent = remaining > 0 ? "Stage 1 is active" : "Stage 1 has expired";
      };
      tick();
      window.clearInterval(window.__stageCountdownTimer);
      window.__stageCountdownTimer = window.setInterval(tick, 1000);
    }

    function setStageLock(isLocked) {
      overlay.hidden = !isLocked;
    }

    payStageUnlock.addEventListener("click", () => {
      window.location.href = "/payments/create-checkout?type=stage_unlock";
    });

    function renderPlanSelection() {
      root.innerHTML = `
        <article class="card">
          <h2>Choose a plan</h2>
          <p>You are not enrolled yet. Pick a plan to unlock the course experience.</p>
          <div class="plan-grid">
            ${plans.map((plan) => `
              <div class="plan">
                <strong>${plan.name}</strong>
                <div class="price">${plan.price}</div>
                <p>${plan.description}</p>
                <button class="primary" data-plan="${plan.id}">Enroll</button>
              </div>
            `).join("")}
          </div>
        </article>
      `;
      root.querySelectorAll("button[data-plan]").forEach((button) => {
        button.addEventListener("click", async () => {
          button.disabled = true;
          try {
            await postJSON("/enrollments/enroll", { plan_tier: button.dataset.plan, user_id: "me" });
            showToast("Enrollment updated");
            await loadDashboard();
          } catch (error) {
            showToast(error.message);
          } finally {
            button.disabled = false;
          }
        });
      });
    }

    function renderProgress(enrollment, gamification) {
      const stageProgress = gamification.stage_progress;
      const stageItems = stageProgress && stageProgress.stages ? stageProgress.stages : [];
      const badges = gamification.badges || [];
      root.innerHTML = `
        <div class="grid dashboard">
          <article class="card stat">
            <span>XP</span>
            <strong>${gamification.xp ?? 0}</strong>
            <span>Reward points earned</span>
          </article>
          <article class="card stat">
            <span>Streak</span>
            <strong>${gamification.streak ?? 0}</strong>
            <span>Lessons completed in sequence</span>
          </article>
          <article class="card stat">
            <span>Plan</span>
            <strong>${enrollment.plan_tier ?? "free"}</strong>
            <span>${enrollment.course?.title || "Nano Lab Academy"}</span>
          </article>
          <article class="card stat">
            <span>Course progress</span>
            <strong>${Math.round(stageProgress?.progress || 0)}%</strong>
            <span>${stageProgress?.completed_lessons || 0} of ${stageProgress?.total_lessons || 0} lessons</span>
            <div class="meter"><div style="width:${stageProgress?.progress || 0}%"></div></div>
          </article>
        </div>
        <article class="card">
          <h2>Stage progress</h2>
          <div class="stack">
            ${stageItems.map((stage) => `
              <div>
                <div class="pill-row">
                  <span class="pill">${stage.title}</span>
                  <span class="muted">${stage.completed_lessons}/${stage.total_lessons} lessons</span>
                </div>
                <div class="meter"><div style="width:${stage.progress}%"></div></div>
              </div>
            `).join("")}
          </div>
        </article>
        <article class="card">
          <h2>Badges</h2>
          <div class="badge-row">
            ${badges.length ? badges.map((badge) => `<span class="badge">${badge}</span>`).join("") : "<span class='muted'>No badges yet. Finish a lesson or quiz to earn one.</span>"}
          </div>
        </article>
      `;
    }

    async function loadDashboard() {
      try {
        const enrollment = await fetchJSON("/enrollments/my?user_id=me");
        const gamification = await fetchJSON("/gamification/status?user_id=me");
        updateCountdown(gamification.stage1_deadline);
        setStageLock(Boolean(gamification.stage1_locked));
        if (!enrollment.enrolled) {
          renderPlanSelection();
          return;
        }
        renderProgress(enrollment, gamification);
      } catch (error) {
        root.innerHTML = `<article class="card"><h2>Dashboard unavailable</h2><p>${error.message}</p></article>`;
      }
    }

    loadDashboard();
    """
    return _page_shell("Dashboard - Nano Lab Academy", body, script)


@router.get("/courses")
def courses_page() -> str:
    body = """
    <main class="stack">
      <section class="hero">
        <h1>Course outline</h1>
        <p>Open lessons, upgrade locked items, and move through the stage tree as you progress.</p>
      </section>
      <section id="courses-root" class="stack"></section>
    </main>
    """
    script = """
    const root = document.getElementById("courses-root");

    function upgradeButton() {
      return `<button class="secondary" data-upgrade>Upgrade</button>`;
    }

    function renderLesson(lesson) {
      const lessonLink = `<a class="button primary" href="/lessons/${lesson.id}">Open lesson</a>`;
      const lockedBadge = lesson.locked ? `<span class="lock">Locked for free plan</span>` : `<span class="success">Available</span>`;
      const action = lesson.locked ? upgradeButton() : lessonLink;
      return `
        <div class="lesson-item">
          <div class="lesson-meta">
            <strong>${lesson.title}</strong>
            <span class="muted">${lesson.description}</span>
            ${lockedBadge}
          </div>
          <div class="pill-row">
            ${action}
          </div>
        </div>
      `;
    }

    function renderOutline(course) {
      root.innerHTML = `
        <article class="card">
          <h2>${course.title}</h2>
          <p>${course.description}</p>
          <div class="outline">
            ${course.outline.map((section) => `
              <section class="section">
                <h3>${section.title}</h3>
                <p>${section.description || ""}</p>
                <div class="lesson-list">
                  ${section.children.map(renderLesson).join("")}
                </div>
              </section>
            `).join("")}
          </div>
        </article>
      `;
      root.querySelectorAll("button[data-upgrade]").forEach((button) => {
        button.addEventListener("click", async () => {
          button.disabled = true;
          try {
            await postJSON("/enrollments/enroll", { plan_tier: "pro", user_id: "me" });
            showToast("Upgrade applied");
            await loadCourses();
          } catch (error) {
            showToast(error.message);
          } finally {
            button.disabled = false;
          }
        });
      });
    }

    async function loadCourses() {
      try {
        const enrollment = await fetchJSON("/enrollments/my?user_id=me");
        if (!enrollment.enrolled) {
          root.innerHTML = `
            <article class="card">
              <h2>You are not enrolled yet</h2>
              <p>Pick a plan on the dashboard to unlock the course outline.</p>
              <a class="button primary" href="/dashboard">Go to dashboard</a>
            </article>
          `;
          return;
        }
        renderOutline(enrollment.course);
      } catch (error) {
        root.innerHTML = `<article class="card"><h2>Course outline unavailable</h2><p>${error.message}</p></article>`;
      }
    }

    loadCourses();
    """
    return _page_shell("Courses - Nano Lab Academy", body, script)


@router.get("/lessons/{lesson_id}")
def lesson_page(lesson_id: int) -> str:
    lesson = lesson_summary(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson_json = json.dumps(lesson)
    quiz_link = f"/quizzes/{lesson['quiz_id']}" if lesson["quiz_id"] else ""
    assignment_link = f"/assignments/{lesson['assignment_id']}" if lesson["assignment_id"] else ""
    body = f"""
    <main class="grid lesson">
      <section class="stack">
        <article class="hero">
          <h1>{escape(lesson['title'])}</h1>
          <p>{escape(lesson['description'])}</p>
          {'<p class="lock">This lesson is locked on the free plan.</p>' if lesson['locked'] else ''}
        </article>
        <article class="card stack">
          <div class="video">
            <video controls playsinline src="{escape(lesson['video_url'])}"></video>
          </div>
          <div class="pill-row">
            <button class="primary" id="download-notes">Download notes</button>
            <button class="secondary" id="mark-complete">Mark complete</button>
            {f'<a class="button ghost" href="{escape(quiz_link)}">Open quiz</a>' if quiz_link else ''}
            {f'<a class="button ghost" href="{escape(assignment_link)}">Open assignment</a>' if assignment_link else ''}
          </div>
          <div id="lesson-status" class="muted"></div>
        </article>
        <article class="card">
          <h2>Quiz</h2>
          <div id="quiz-root"></div>
        </article>
      </section>
      <aside class="stack">
        <article class="card">
          <h2>Lesson details</h2>
          <p>{escape(lesson['notes'])}</p>
          <p class="muted">XP reward: {lesson['xp_reward']}</p>
        </article>
        <article class="card">
          <h2>Related work</h2>
          <p class="muted">Use the links above to jump to the quiz or assignment associated with this lesson.</p>
        </article>
      </aside>
    </main>
    <script type="application/json" id="lesson-data">{lesson_json}</script>
    """
    script = """
    const lesson = JSON.parse(document.getElementById("lesson-data").textContent);
    const status = document.getElementById("lesson-status");
    const quizRoot = document.getElementById("quiz-root");
    const notesButton = document.getElementById("download-notes");
    const completeButton = document.getElementById("mark-complete");

    function setStatus(message) {
      status.textContent = message;
    }

    async function downloadNotes() {
      const response = await fetchJSON("/download-notes", {
        method: "POST",
        body: JSON.stringify({ lesson_id: lesson.id, user_id: "me" }),
      });
      const blob = new Blob([response.content], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = response.filename || `lesson-${lesson.id}-notes.txt`;
      anchor.click();
      URL.revokeObjectURL(url);
      showToast("Notes download started");
    }

    async function markComplete() {
      const response = await postJSON(`/lessons/${lesson.id}/complete`, { user_id: "me" });
      setStatus(`Completed lesson ${lesson.id}. XP: ${response.gamification.xp}, streak: ${response.gamification.streak}`);
      showToast("Lesson completed");
    }

    notesButton.addEventListener("click", async () => {
      notesButton.disabled = true;
      try {
        await downloadNotes();
      } catch (error) {
        showToast(error.message);
      } finally {
        notesButton.disabled = false;
      }
    });

    completeButton.addEventListener("click", async () => {
      completeButton.disabled = true;
      try {
        await markComplete();
      } catch (error) {
        showToast(error.message);
      } finally {
        completeButton.disabled = false;
      }
    });

    async function loadQuiz() {
      if (!lesson.quiz_id) {
        quizRoot.innerHTML = `<p class="muted">This lesson does not have a quiz.</p>`;
        return;
      }
      const quiz = await fetchJSON(`/quizzes/${lesson.quiz_id}`);
      quizRoot.innerHTML = `
        <form class="quiz" id="quiz-form">
          <div>
            <h3>${quiz.title}</h3>
            <p>${quiz.description || "Answer the questions and submit your attempt."}</p>
          </div>
          ${quiz.questions.map((question) => {
            const options = question.options && question.options.length ? question.options : ["True", "False"];
            return `
              <section class="question">
                <h4>${question.prompt}</h4>
                ${options.map((option) => `
                  <label>
                    <input type="radio" name="question-${question.id}" value="${option}">
                    <span>${option}</span>
                  </label>
                `).join("")}
              </section>
            `;
          }).join("")}
          <button class="primary" type="submit">Submit answers</button>
          <div id="quiz-result" class="muted"></div>
        </form>
      `;

      document.getElementById("quiz-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const answers = quiz.questions.map((question) => {
          const selected = document.querySelector(`input[name="question-${question.id}"]:checked`);
          return { question_id: question.id, answer: selected ? selected.value : null };
        });
        const result = await postJSON(`/quizzes/${lesson.quiz_id}/attempt`, { user_id: "me", answers });
        document.getElementById("quiz-result").textContent = `Score ${result.score}%, XP ${result.xp_awarded}, passed: ${result.passed ? "yes" : "no"}`;
        showToast("Quiz submitted");
      });
    }

    loadQuiz().catch((error) => {
      quizRoot.innerHTML = `<p class="muted">${error.message}</p>`;
    });
    """
    return _page_shell(f"Lesson {lesson_id} - Nano Lab Academy", body, script)


@router.get("/payments/create-checkout")
def create_checkout(type: str = "stage_unlock") -> str:
    body = f"""
    <main class="stack">
      <section class="hero">
        <h1>Checkout</h1>
        <p>This is a lightweight checkout landing page for the {escape(type)} flow.</p>
      </section>
      <article class="card">
        <h2>Stage unlock checkout</h2>
        <p>Payment processing is stubbed in this workspace. Use this screen to confirm the unlock intent and return to the dashboard.</p>
        <div class="pill-row">
          <a class="button primary" href="/dashboard">Return to dashboard</a>
          <a class="button secondary" href="/stage-2">Open stage 2</a>
        </div>
      </article>
    </main>
    """
    return _page_shell("Checkout - Nano Lab Academy", body)


@router.get("/stage-2")
def stage_two_page() -> str:
    body = """
    <main class="stack">
      <section class="hero">
        <h1>Stage 2</h1>
        <p>Select a lab partner, track your tasks, and review supervisor ratings.</p>
      </section>
      <section id="stage2-root" class="stack"></section>
    </main>
    """
    script = """
    const root = document.getElementById("stage2-root");

    function renderStageTwo(data) {
      root.innerHTML = `
        <div class="grid dashboard">
          <article class="card">
            <h2>Lab partners</h2>
            <form id="partner-form" class="stack">
              ${data.lab_partners.map((partner) => `
                <label class="lesson-item" style="justify-content:flex-start; cursor:pointer;">
                  <input type="radio" name="partner_id" value="${partner.id}" ${partner === data.lab_partners[0] ? "checked" : ""}>
                  <div class="lesson-meta">
                    <strong>${partner.name}</strong>
                    <span class="muted">${partner.skill}</span>
                    <span class="muted">Availability: ${partner.availability}</span>
                  </div>
                </label>
              `).join("")}
              <button class="primary" type="submit">Save partner</button>
              <div id="partner-result" class="muted"></div>
            </form>
          </article>
          <article class="card">
            <h2>Tasks</h2>
            <div class="stack">
              ${data.tasks.map((task) => `
                <div class="lesson-item">
                  <div class="lesson-meta">
                    <strong>${task.title}</strong>
                    <span class="muted">Status: ${task.status}</span>
                  </div>
                  <button class="secondary" type="button">Open</button>
                </div>
              `).join("")}
            </div>
          </article>
        </div>
        <article class="card">
          <h2>Supervisor ratings</h2>
          <div class="lesson-list">
            ${data.supervisor_ratings.map((rating) => `
              <div class="lesson-item">
                <div class="lesson-meta">
                  <strong>${rating.name}</strong>
                  <span class="muted">${rating.note}</span>
                </div>
                <span class="pill">${rating.rating.toFixed(1)} / 5</span>
              </div>
            `).join("")}
          </div>
        </article>
      `;

      document.getElementById("partner-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const selected = document.querySelector('input[name="partner_id"]:checked');
        const result = document.getElementById("partner-result");
        try {
          const response = await postJSON("/stage-2/select-partner", { partner_id: selected ? selected.value : null });
          result.textContent = `Selected ${response.partner_name || "partner"}`;
          showToast("Lab partner saved");
        } catch (error) {
          result.textContent = error.message;
        }
      });
    }

    fetchJSON("/stage-2/data")
      .then(renderStageTwo)
      .catch((error) => {
        root.innerHTML = `<article class="card"><h2>Stage 2 unavailable</h2><p>${error.message}</p></article>`;
      });
    """
    return _page_shell("Stage 2 - Nano Lab Academy", body, script)


@router.get("/stage-3")
def stage_three_page() -> str:
    body = """
    <main class="stack">
      <section class="hero">
        <h1>Stage 3</h1>
        <p>Explore the job board and submit applications directly from the page.</p>
      </section>
      <section id="stage3-root" class="stack"></section>
    </main>
    """
    script = """
    const root = document.getElementById("stage3-root");

    function renderApplications(applications) {
      if (!applications.length) {
        return `<p class="muted">No applications submitted yet.</p>`;
      }
      return `
        <div class="lesson-list">
          ${applications.map((application) => `
            <div class="lesson-item">
              <div class="lesson-meta">
                <strong>${application.name || "Anonymous applicant"}</strong>
                <span class="muted">${application.email || "No email provided"}</span>
              </div>
              <span class="pill">Applied to ${application.job_id}</span>
            </div>
          `).join("")}
        </div>
      `;
    }

    function renderStageThree(data) {
      root.innerHTML = `
        <div class="grid dashboard">
          <article class="card">
            <h2>Job board</h2>
            <div class="lesson-list">
              ${data.jobs.map((job) => `
                <div class="lesson-item">
                  <div class="lesson-meta">
                    <strong>${job.title}</strong>
                    <span class="muted">${job.location} · ${job.type}</span>
                    <span class="muted">${job.salary}</span>
                  </div>
                  <span class="pill">Open</span>
                </div>
              `).join("")}
            </div>
          </article>
          <article class="card">
            <h2>Application form</h2>
            <form id="application-form" class="stack">
              <label class="stack">
                <span class="muted">Job</span>
                <select name="job_id" style="padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(32,21,15,0.14);">
                  ${data.jobs.map((job) => `<option value="${job.id}">${job.title}</option>`).join("")}
                </select>
              </label>
              <label class="stack">
                <span class="muted">Name</span>
                <input name="name" placeholder="Your name" style="padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(32,21,15,0.14);">
              </label>
              <label class="stack">
                <span class="muted">Email</span>
                <input name="email" type="email" placeholder="you@example.com" style="padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(32,21,15,0.14);">
              </label>
              <label class="stack">
                <span class="muted">Cover letter</span>
                <textarea name="cover_letter" rows="5" placeholder="Tell the hiring team why you fit the role" style="padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(32,21,15,0.14);"></textarea>
              </label>
              <button class="primary" type="submit">Submit application</button>
              <div id="application-result" class="muted"></div>
            </form>
          </article>
        </div>
        <article class="card">
          <h2>Applications submitted</h2>
          <div id="application-list">${renderApplications(data.applications)}</div>
        </article>
      `;

      document.getElementById("application-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.currentTarget;
        const payload = {
          job_id: form.job_id.value,
          name: form.name.value,
          email: form.email.value,
          cover_letter: form.cover_letter.value,
        };
        const result = document.getElementById("application-result");
        try {
          const response = await postJSON("/stage-3/apply", payload);
          result.textContent = `Application submitted for ${response.application.job_id}`;
          document.getElementById("application-list").innerHTML = renderApplications(response.applications);
          showToast("Application submitted");
          form.reset();
        } catch (error) {
          result.textContent = error.message;
        }
      });
    }

    fetchJSON("/stage-3/data")
      .then(renderStageThree)
      .catch((error) => {
        root.innerHTML = `<article class="card"><h2>Stage 3 unavailable</h2><p>${error.message}</p></article>`;
      });
    """
    return _page_shell("Stage 3 - Nano Lab Academy", body, script)
