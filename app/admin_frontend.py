from __future__ import annotations

import json
from html import escape
from typing import Any

from .auth import require_admin
from .framework import HTTPException, Request, Router
from .store import (
    assignments,
    courses,
    enrollments,
    get_assignment,
    get_quiz,
    lessons,
    quizzes,
    stage1_state,
    stage2_lab_partners,
    stage2_state,
    stage3_applications,
    stage3_jobs,
    stage3_state,
    submissions,
    user_xp,
)


router = Router(prefix="/admin")


def _admin_gate(request: Request) -> str | None:
  try:
    require_admin(request)
  except HTTPException:
    return _forbidden_page(), 403, "text/html; charset=utf-8"
  return None


def _forbidden_page() -> str:
    return _admin_shell(
        "Admin access required",
        """
        <main class="admin-main">
          <section class="card hero-card">
            <h1>Admin access required</h1>
            <p>This route is protected by JWT role checks. Send a token with an admin role in the Authorization header or auth_token cookie.</p>
          </section>
        </main>
        """,
    )


def _admin_shell(title: str, body: str, script: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #0e1218;
      --panel: rgba(18, 25, 34, 0.92);
      --panel-soft: rgba(27, 36, 48, 0.84);
      --surface: rgba(255, 255, 255, 0.06);
      --text: #ecf2f8;
      --muted: #93a4b7;
      --accent: #86efac;
      --accent-strong: #5eead4;
      --border: rgba(255, 255, 255, 0.08);
      --shadow: 0 28px 70px rgba(0, 0, 0, 0.32);
      --radius: 22px;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Segoe UI", "Aptos", sans-serif; color: var(--text); background: radial-gradient(circle at top left, rgba(94,234,212,0.16), transparent 22%), linear-gradient(180deg, #0b1016 0%, #111722 100%); min-height: 100vh; }}
    a {{ color: inherit; text-decoration: none; }}
    .admin-shell {{ display: grid; grid-template-columns: 300px minmax(0, 1fr); min-height: 100vh; }}
    .sidebar {{ padding: 24px; border-right: 1px solid var(--border); background: rgba(6, 10, 15, 0.82); position: sticky; top: 0; align-self: start; height: 100vh; overflow: auto; }}
    .brand {{ display: grid; gap: 6px; margin-bottom: 24px; }}
    .brand strong {{ font-size: 1.1rem; letter-spacing: 0.08em; text-transform: uppercase; }}
    .brand span {{ color: var(--muted); line-height: 1.45; }}
    .nav {{ display: grid; gap: 10px; }}
    .nav a {{ padding: 12px 14px; border-radius: 14px; background: rgba(255,255,255,0.04); border: 1px solid transparent; }}
    .nav a:hover {{ border-color: rgba(255,255,255,0.12); background: rgba(255,255,255,0.08); }}
    .nav a.active {{ background: rgba(134,239,172,0.14); border-color: rgba(134,239,172,0.24); color: var(--accent); }}
    .sidebar-card {{ margin-top: 22px; padding: 16px; border-radius: 18px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); }}
    .content {{ padding: 28px; }}
    .topbar {{ display: flex; justify-content: space-between; gap: 18px; align-items: center; margin-bottom: 22px; }}
    .topbar h1 {{ margin: 0; font-size: clamp(1.6rem, 3vw, 2.4rem); }}
    .topbar p {{ margin: 6px 0 0; color: var(--muted); }}
    .grid {{ display: grid; gap: 16px; }}
    .grid.stats {{ grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin-bottom: 18px; }}
    .grid.two {{ grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }}
    .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 20px; }}
    .card h2, .card h3 {{ margin: 0 0 12px; }}
    .card p {{ color: var(--muted); line-height: 1.55; }}
    .stat strong {{ display: block; font-size: 2rem; margin-bottom: 4px; }}
    .muted {{ color: var(--muted); }}
    .pill-row {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .pill {{ padding: 8px 12px; border-radius: 999px; background: rgba(134,239,172,0.12); color: var(--accent); border: 1px solid rgba(134,239,172,0.2); font-weight: 700; }}
    .list {{ display: grid; gap: 12px; }}
    .row {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 14px 16px; border-radius: 16px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); }}
    .row strong {{ display: block; }}
    .row small {{ color: var(--muted); }}
    .tree {{ display: grid; gap: 14px; }}
    .section {{ padding: 16px; border-radius: 18px; background: var(--panel-soft); border: 1px solid var(--border); }}
    .lesson-list {{ display: grid; gap: 10px; margin-top: 12px; }}
    .lesson-item {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 12px 14px; border-radius: 14px; background: rgba(255,255,255,0.04); border: 1px solid var(--border); }}
    .handle {{ cursor: grab; color: var(--accent-strong); font-size: 1.2rem; user-select: none; }}
    .toolbar {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }}
    button, .button {{ appearance: none; border: none; border-radius: 14px; padding: 11px 15px; font-weight: 700; cursor: pointer; color: #081018; background: var(--accent); }}
    .secondary {{ background: rgba(255,255,255,0.08); color: var(--text); border: 1px solid var(--border); }}
    .ghost {{ background: transparent; color: var(--accent-strong); border: 1px dashed rgba(94,234,212,0.26); }}
    .form-grid {{ display: grid; gap: 12px; }}
    input, textarea, select {{ width: 100%; border-radius: 14px; border: 1px solid var(--border); background: rgba(255,255,255,0.04); color: var(--text); padding: 12px 14px; }}
    textarea {{ min-height: 120px; resize: vertical; }}
    .table {{ width: 100%; border-collapse: collapse; }}
    .table th, .table td {{ text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }}
    .split {{ display: grid; gap: 14px; grid-template-columns: minmax(0, 1fr) 320px; }}
    @media (max-width: 1060px) {{ .admin-shell {{ grid-template-columns: 1fr; }} .sidebar {{ position: static; height: auto; }} .split {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="admin-shell">
    <aside class="sidebar">
      <div class="brand">
        <strong>Admin Console</strong>
        <span>Separate layout for protected management routes.</span>
      </div>
      <nav class="nav">
        <a href="/admin">Dashboard</a>
        <a href="/admin/courses">Courses</a>
        <a href="/admin/quizzes">Quizzes</a>
        <a href="/admin/users">Users</a>
        <a href="/admin/lab-partners">Lab partners</a>
        <a href="/admin/jobs">Jobs</a>
        <a href="/admin/payments">Payments</a>
      </nav>
      <div class="sidebar-card">
        <div class="muted">Protection</div>
        <strong>JWT admin role required</strong>
        <p>Requests are checked against the Authorization header or auth_token cookie before the route renders.</p>
      </div>
    </aside>
    <main class="content">
      {body}
    </main>
  </div>
  <script>
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav a').forEach((link) => {{
      if (link.getAttribute('href') === currentPath) {{
        link.classList.add('active');
      }}
    }});
    async function fetchJSON(url, options = {{}}) {{
      const response = await fetch(url, {{ headers: {{ 'Content-Type': 'application/json', ...(options.headers || {{}}) }}, ...options }});
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Request failed');
      return data;
    }}
    async function postJSON(url, payload) {{
      return fetchJSON(url, {{ method: 'POST', body: JSON.stringify(payload || {{}}) }});
    }}
    {script}
  </script>
</body>
</html>"""


def _course_snapshot() -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for course in courses.values():
        snapshots.append(
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "sections": [
                    {
                        "id": section.id,
                        "title": section.title,
                        "description": section.description,
                        "lessons": [
                            {
                                "id": lesson.id,
                                "title": lesson.title,
                                "description": lesson.description,
                                "locked": lesson.freemium_locked,
                                "quiz_id": lesson.quiz_id,
                                "assignment_id": lesson.assignment_id,
                            }
                            for lesson in section.children
                        ],
                    }
                    for section in course.outline
                ],
            }
        )
    return snapshots


def _user_snapshot() -> list[dict[str, Any]]:
    user_ids = set(enrollments) | set(user_xp) | {submission.user_id for submission in submissions.values()}
    if not user_ids:
        user_ids = {"me", "coach", "learner-2"}

    results: list[dict[str, Any]] = []
    for index, user_id in enumerate(sorted(user_ids), start=1):
        enrollment = enrollments.get(user_id)
        progress = 0
        if enrollment and enrollment.course_id in courses:
            course = courses[enrollment.course_id]
            total_lessons = sum(len(section.children) for section in course.outline)
            completed_lessons = 0
            results_for_user = [submission for submission in submissions.values() if submission.user_id == user_id]
            if total_lessons:
                completed_lessons = min(total_lessons, len(results_for_user))
            progress = round((completed_lessons / total_lessons) * 100, 2) if total_lessons else 0.0
        results.append(
            {
                "id": f"user-{index}",
                "user_id": user_id,
                "role": "admin" if user_id == "admin" else "learner",
                "plan_tier": enrollment.plan_tier if enrollment else "free",
                "xp": user_xp.get(user_id, 0),
                "progress": progress,
            }
        )
    return results


def _payment_snapshot() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "id": 1,
            "user_id": "me",
            "type": "stage_unlock",
            "amount": "$29.00",
            "status": "succeeded",
            "reference": "txn_stage_unlock_001",
        }
    ]
    rows.extend(
        {
            "id": index + 2,
            "user_id": application.get("email") or application.get("name") or "guest",
            "type": "application_fee",
            "amount": "$0.00",
            "status": "pending",
            "reference": f"txn_application_{application['id']}",
        }
        for index, application in enumerate(stage3_applications)
    )
    return rows


@router.get("")
def admin_dashboard(request: Request) -> str:
    denied = _admin_gate(request)
    if denied:
        return denied

    body = """
    <section class="topbar">
      <div>
        <h1>Admin dashboard</h1>
        <p>Summary stats are fetched from /admin/analytics.</p>
      </div>
      <a class="button ghost" href="/admin/analytics">Open analytics JSON</a>
    </section>
    <section id="admin-summary" class="grid stats"></section>
    <section class="grid two">
      <article class="card">
        <h2>Operations</h2>
        <p>Use the management routes to edit course content, users, partners, jobs, and payments.</p>
        <div class="pill-row">
          <span class="pill">Protected</span>
          <span class="pill">JWT role check</span>
          <span class="pill">Separate layout</span>
        </div>
      </article>
      <article class="card">
        <h2>System health</h2>
        <div id="health-copy" class="muted">Loading analytics...</div>
      </article>
    </section>
    """
    script = """
    fetchJSON('/admin/analytics', { headers: { Authorization: window.localStorage.getItem('admin_jwt') ? `Bearer ${window.localStorage.getItem('admin_jwt')}` : '' } })
      .then((data) => {
        const summary = document.getElementById('admin-summary');
        summary.innerHTML = [
          ['Courses', data.courses],
          ['Sections', data.sections],
          ['Lessons', data.lessons],
          ['Users', data.users],
          ['Quiz', data.quizzes],
          ['Payments', data.payments],
        ].map(([label, value]) => `<article class="card stat"><strong>${value}</strong><span class="muted">${label}</span></article>`).join('');
        document.getElementById('health-copy').textContent = `Stage 1 is ${data.stage1_locked ? 'locked' : 'active'} and ${data.partners} lab partners are available.`;
      })
      .catch((error) => {
        document.getElementById('admin-summary').innerHTML = `<article class="card"><h2>Analytics unavailable</h2><p>${error.message}</p></article>`;
        document.getElementById('health-copy').textContent = error.message;
      });
    """
    return _admin_shell("Admin dashboard", body, script)


@router.get("/analytics")
def admin_analytics(request: Request) -> dict[str, Any]:
    require_admin(request)
    return {
        "courses": len(courses),
        "sections": sum(len(course.outline) for course in courses.values()),
        "lessons": len(lessons),
        "users": len(_user_snapshot()),
        "quizzes": len(quizzes),
        "payments": len(_payment_snapshot()),
        "jobs": len(stage3_jobs),
        "partners": len(stage2_lab_partners),
        "applications": len(stage3_applications),
        "stage1_locked": stage1_state()["stage1_locked"],
    }


@router.get("/courses")
def admin_courses(request: Request) -> str:
    denied = _admin_gate(request)
    if denied:
        return denied

    course_data = json.dumps(_course_snapshot())
    body = f"""
    <section class="topbar">
      <div>
        <h1>Course manager</h1>
        <p>Manage courses, sections, and lessons with drag and drop ordering.</p>
      </div>
      <div class="toolbar">
        <button class="secondary" type="button">Add course</button>
        <button class="secondary" type="button">Add section</button>
        <button class="secondary" type="button">Add lesson</button>
      </div>
    </section>
    <section class="card">
      <div class="muted">Sort with SortableJS. Changes are staged in the browser for now.</div>
      <div id="course-tree" class="tree"></div>
    </section>
    <script type="application/json" id="course-data">{course_data}</script>
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.6/Sortable.min.js"></script>
    """
    script = """
    const tree = document.getElementById('course-tree');
    const data = JSON.parse(document.getElementById('course-data').textContent);

    tree.innerHTML = data.map((course) => `
      <article class="section" data-course-id="${course.id}">
        <div class="toolbar">
          <strong>${course.title}</strong>
          <button class="ghost" type="button">Publish</button>
        </div>
        <p class="muted">${course.description}</p>
        <div class="tree sections">
          ${course.sections.map((section) => `
            <section class="section" data-section-id="${section.id}">
              <div class="toolbar"><span class="handle">::</span><strong>${section.title}</strong></div>
              <p class="muted">${section.description || ''}</p>
              <div class="lesson-list">
                ${section.lessons.map((lesson) => `
                  <div class="lesson-item" data-lesson-id="${lesson.id}">
                    <div>
                      <strong>${lesson.title}</strong>
                      <small>${lesson.description}</small>
                    </div>
                    <div class="pill-row">
                      <span class="pill">${lesson.quiz_id ? 'Quiz' : 'Lesson'}</span>
                      <span class="handle">::</span>
                    </div>
                  </div>
                `).join('')}
              </div>
            </section>
          `).join('')}
        </div>
      </article>
    `).join('');

    if (window.Sortable) {
      new Sortable(tree, { animation: 150, handle: '.handle' });
      document.querySelectorAll('.sections, .lesson-list').forEach((element) => {
        new Sortable(element, { animation: 150, handle: '.handle' });
      });
    }
    """
    return _admin_shell("Admin courses", body, script)


@router.get("/quizzes")
def admin_quizzes(request: Request) -> str:
    denied = _admin_gate(request)
    if denied:
        return denied

    quiz_data = [
        {"id": quiz.id, "title": quiz.title, "questions": len(quiz.questions), "description": quiz.description}
        for quiz in quizzes.values()
    ]
    body = f"""
    <section class="topbar">
      <div>
        <h1>Quiz builder</h1>
        <p>Create quizzes and add questions.</p>
      </div>
      <div class="toolbar"><button class="secondary" type="button">Create quiz</button><button class="secondary" type="button">Add question</button></div>
    </section>
    <div class="grid two">
      <article class="card">
        <h2>Existing quizzes</h2>
        <div class="list">{''.join(f'<div class="row"><div><strong>{escape(item["title"])}</strong><small>{item["questions"]} questions</small></div><span class="pill">#{item["id"]}</span></div>' for item in quiz_data)}</div>
      </article>
      <article class="card">
        <h2>Quiz form</h2>
        <form class="form-grid">
          <input placeholder="Quiz title">
          <textarea placeholder="Quiz description"></textarea>
          <input placeholder="Pass threshold" value="70">
          <button type="button">Save quiz</button>
        </form>
      </article>
    </div>
    <article class="card" style="margin-top:16px;">
      <h2>Question editor</h2>
      <div class="form-grid">
        <input placeholder="Question prompt">
        <select><option>Multiple choice</option><option>True/false</option><option>Short answer</option></select>
        <textarea placeholder="Answer options or explanation"></textarea>
      </div>
    </article>
    """
    return _admin_shell("Admin quizzes", body)


@router.get("/users")
def admin_users(request: Request) -> str:
    denied = _admin_gate(request)
    if denied:
        return denied

    users = _user_snapshot()
    body = """
    <section class="topbar">
      <div>
        <h1>User management</h1>
        <p>List users, edit plan tier, and review progress.</p>
      </div>
    </section>
    <article class="card">
      <table class="table">
        <thead><tr><th>User</th><th>Role</th><th>Plan</th><th>XP</th><th>Progress</th><th>Action</th></tr></thead>
        <tbody id="user-table"></tbody>
      </table>
    </article>
    <script type="application/json" id="user-data">%s</script>
    """ % json.dumps(users)
    script = """
    const users = JSON.parse(document.getElementById('user-data').textContent);
    document.getElementById('user-table').innerHTML = users.map((user) => `
      <tr>
        <td><strong>${user.user_id}</strong></td>
        <td>${user.role}</td>
        <td>
          <select>
            <option ${user.plan_tier === 'free' ? 'selected' : ''}>free</option>
            <option ${user.plan_tier === 'pro' ? 'selected' : ''}>pro</option>
          </select>
        </td>
        <td>${user.xp}</td>
        <td>${user.progress}%</td>
        <td><button class="secondary" type="button">Save</button></td>
      </tr>
    `).join('');
    """
    return _admin_shell("Admin users", body, script)


@router.get("/lab-partners")
def admin_lab_partners(request: Request) -> str:
    denied = _admin_gate(request)
    if denied:
        return denied

    body = """
    <section class="topbar">
      <div>
        <h1>Lab partners</h1>
        <p>Manage partner profiles and availability.</p>
      </div>
      <button class="secondary" type="button">Add partner</button>
    </section>
    <div class="grid two">
      <article class="card">
        <h2>Partners</h2>
        <div class="list" id="partner-list"></div>
      </article>
      <article class="card">
        <h2>Partner form</h2>
        <form class="form-grid">
          <input placeholder="Partner name">
          <input placeholder="Skill area">
          <input placeholder="Availability">
          <button type="button">Save partner</button>
        </form>
      </article>
    </div>
    <script type="application/json" id="partner-data">%s</script>
    """ % json.dumps(stage2_lab_partners)
    script = """
    const partners = JSON.parse(document.getElementById('partner-data').textContent);
    document.getElementById('partner-list').innerHTML = partners.map((partner) => `
      <div class="row">
        <div><strong>${partner.name}</strong><small>${partner.skill}</small></div>
        <span class="pill">${partner.availability}</span>
      </div>
    `).join('');
    """
    return _admin_shell("Admin lab partners", body, script)


@router.get("/jobs")
def admin_jobs(request: Request) -> str:
    denied = _admin_gate(request)
    if denied:
        return denied

    body = """
    <section class="topbar">
      <div>
        <h1>Job listings</h1>
        <p>Manage job board entries and application flow.</p>
      </div>
      <button class="secondary" type="button">Add job</button>
    </section>
    <div class="grid two">
      <article class="card">
        <h2>Jobs</h2>
        <div class="list" id="job-list"></div>
      </article>
      <article class="card">
        <h2>Job form</h2>
        <form class="form-grid">
          <input placeholder="Title">
          <input placeholder="Location">
          <input placeholder="Type">
          <input placeholder="Salary range">
          <textarea placeholder="Job description"></textarea>
          <button type="button">Save listing</button>
        </form>
      </article>
    </div>
    <script type="application/json" id="job-data">%s</script>
    """ % json.dumps(stage3_jobs)
    script = """
    const jobs = JSON.parse(document.getElementById('job-data').textContent);
    document.getElementById('job-list').innerHTML = jobs.map((job) => `
      <div class="row">
        <div><strong>${job.title}</strong><small>${job.location} · ${job.type}</small></div>
        <span class="pill">${job.salary}</span>
      </div>
    `).join('');
    """
    return _admin_shell("Admin jobs", body, script)


@router.get("/payments")
def admin_payments(request: Request) -> str:
    denied = _admin_gate(request)
    if denied:
        return denied

    body = """
    <section class="topbar">
      <div>
        <h1>Payment transactions</h1>
        <p>View payment records and checkout events.</p>
      </div>
    </section>
    <article class="card">
      <table class="table">
        <thead><tr><th>Transaction</th><th>User</th><th>Type</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody id="payment-table"></tbody>
      </table>
    </article>
    <script type="application/json" id="payment-data">%s</script>
    """ % json.dumps(_payment_snapshot())
    script = """
    const payments = JSON.parse(document.getElementById('payment-data').textContent);
    document.getElementById('payment-table').innerHTML = payments.map((payment) => `
      <tr>
        <td>${payment.reference}</td>
        <td>${payment.user_id}</td>
        <td>${payment.type}</td>
        <td>${payment.amount}</td>
        <td>${payment.status}</td>
      </tr>
    `).join('');
    """
    return _admin_shell("Admin payments", body, script)
