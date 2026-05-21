"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getJson } from "@/lib/api";
import { LessonTree } from "@/components/LessonTree";
import { useSessionStore } from "@/lib/store";

type ResponseData = {
  enrolled?: boolean;
  courses?: Array<{
    id: string;
    title: string;
    description?: string;
    sections: Array<{
      id: string;
      title: string;
      lessons: Array<{
        id: string;
        title: string;
        locked?: boolean;
        freePreview?: boolean;
      }>;
    }>;
  }>;
};

export default function CoursesPage() {
  const { enrollment, courses, setCourses } = useSessionStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([getJson<ResponseData>("/courses/my"), getJson("/enrollments/my")])
      .then(([coursesData, enrollmentData]) => {
        if (!active) return;
        if (coursesData.courses?.length) {
          setCourses(coursesData.courses as never);
        }
        if (!enrollment?.id && (enrollmentData as { id?: string }).id) {
          // store is already populated on dashboard, but keep the gate fresh here
        }
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load courses");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [enrollment?.id, setCourses]);

  const isEnrolled = Boolean(enrollment?.id);

  if (loading) {
    return <main className="p-8 text-slate-600">Loading courses...</main>;
  }

  if (error) {
    return <main className="p-8 text-red-600">{error}</main>;
  }

  if (!isEnrolled) {
    return (
      <main className="mx-auto max-w-4xl px-6 py-12">
        <div className="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
          <h1 className="text-3xl font-bold text-slate-900">You are not enrolled yet</h1>
          <p className="mt-3 text-slate-600">Pick a plan from your dashboard to unlock the course outline.</p>
          <Link
            className="mt-6 inline-flex rounded-full bg-sky-600 px-5 py-3 text-sm font-semibold text-white"
            href="/dashboard"
          >
            Go to dashboard
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-6">
        <p className="text-sm font-medium uppercase tracking-[0.3em] text-sky-600">
          Course outline
        </p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">Your lessons</h1>
      </div>
      {courses.length ? (
        <LessonTree courses={courses} />
      ) : (
        <div className="rounded-3xl bg-white p-8 text-slate-600 shadow-sm ring-1 ring-slate-200">
          No course outline is available yet.
        </div>
      )}
    </main>
  );
}
