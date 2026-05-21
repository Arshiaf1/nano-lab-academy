"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getJson, postJson } from "@/lib/api";
import { QuizComponent } from "@/components/QuizComponent";
import { VideoPlayer } from "@/components/VideoPlayer";

type LessonResponse = {
  id: string;
  title: string;
  description?: string;
  videoUrl?: string;
  notesPdfUrl?: string;
  quizId?: string;
  assignmentId?: string;
  quiz?: { id: string; title?: string };
  assignment?: { id: string; title?: string };
};

export default function LessonPage() {
  const params = useParams<{ id: string }>();
  const lessonId = params?.id;
  const [lesson, setLesson] = useState<LessonResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!lessonId) {
      return;
    }

    let active = true;
    setLoading(true);
    getJson<LessonResponse>(`/lessons/${lessonId}`)
      .then((data) => {
        if (!active) return;
        setLesson(data);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load lesson");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [lessonId]);

  async function handleDownloadNotes() {
    if (!lessonId) return;
    setBusy(true);
    setMessage(null);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1"}/lessons/${lessonId}/download-notes`,
        {
          credentials: "include",
        },
      );
      if (!response.ok) {
        throw new Error("Failed to download notes");
      }
      const contentType = response.headers.get("content-type") ?? "";
      if (contentType.includes("application/json")) {
        const data = (await response.json()) as { url?: string; message?: string };
        if (data.url) {
          window.open(data.url, "_blank", "noopener,noreferrer");
        }
        setMessage(data.message ?? "Notes ready");
      } else {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = `${lesson?.title ?? "lesson-notes"}.pdf`;
        anchor.click();
        URL.revokeObjectURL(url);
        setMessage("Notes download started");
      }
    } catch (err: unknown) {
      setMessage(err instanceof Error ? err.message : "Failed to download notes");
    } finally {
      setBusy(false);
    }
  }

  async function handleMarkComplete() {
    if (!lessonId) return;
    setBusy(true);
    setMessage(null);
    try {
      await postJson(`/lessons/${lessonId}/progress`, { watched: true });
      setMessage("Lesson marked complete");
    } catch (err: unknown) {
      setMessage(err instanceof Error ? err.message : "Failed to mark complete");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return <main className="p-8 text-slate-600">Loading lesson...</main>;
  }

  if (error) {
    return <main className="p-8 text-red-600">{error}</main>;
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-8">
      <Link className="text-sm font-semibold text-sky-700" href="/courses">
        ← Back to courses
      </Link>

      <section className="mt-4 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h1 className="text-3xl font-bold text-slate-900">{lesson?.title}</h1>
        {lesson?.description ? <p className="mt-3 text-slate-600">{lesson.description}</p> : null}

        <div className="mt-6">
          <VideoPlayer src={lesson?.videoUrl} title={lesson?.title} />
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            className="rounded-full bg-sky-600 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
            disabled={busy}
            onClick={handleDownloadNotes}
            type="button"
          >
            Download notes
          </button>
          <button
            className="rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 disabled:opacity-60"
            disabled={busy}
            onClick={handleMarkComplete}
            type="button"
          >
            Mark complete
          </button>
          {lesson?.quizId ? (
            <Link
              className="rounded-full border border-sky-200 bg-sky-50 px-5 py-3 text-sm font-semibold text-sky-700"
              href={`#quiz-${lesson.quizId}`}
            >
              Open quiz
            </Link>
          ) : null}
          {lesson?.assignmentId ? (
            <Link
              className="rounded-full border border-emerald-200 bg-emerald-50 px-5 py-3 text-sm font-semibold text-emerald-700"
              href={`/assignments/${lesson.assignmentId}`}
            >
              View assignment
            </Link>
          ) : null}
        </div>

        {message ? <p className="mt-4 text-sm text-slate-600">{message}</p> : null}
      </section>

      {lesson?.quizId ? (
        <div id={`quiz-${lesson.quizId}`} className="mt-8">
          <QuizComponent quizId={lesson.quizId} />
        </div>
      ) : null}
    </main>
  );
}
