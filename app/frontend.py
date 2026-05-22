from __future__ import annotations

import json
from html import escape
from typing import Any

from .framework import Router, HTTPException
from .store import gamification_status, get_lesson, lesson_summary


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
      <section id="dashboard-root" class="stack"></section>
    </main>
    """
    script = """
    const root = document.getElementById("dashboard-root");
    const plans = [
      { id: "free", name: "Free", price: "$0", description: "Access the starter track and unlock the upgrade flow later." },
      { id: "pro", name: "Pro", price: "$29", description: "Unlock all lessons and keep the full outline available." },
    ];

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
