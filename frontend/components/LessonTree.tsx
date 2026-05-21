"use client";

import Link from "next/link";
import type { CourseNode } from "@/lib/store";

type Props = {
  courses: CourseNode[];
};

export function LessonTree({ courses }: Props) {
  return (
    <div className="space-y-6">
      {courses.map((course) => (
        <section key={course.id} className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <div className="mb-4">
            <h2 className="text-xl font-semibold text-slate-900">{course.title}</h2>
            {course.description ? (
              <p className="mt-1 text-sm text-slate-600">{course.description}</p>
            ) : null}
          </div>
          <div className="space-y-4">
            {course.sections.map((section) => (
              <div key={section.id} className="rounded-2xl bg-slate-50 p-4">
                <h3 className="font-medium text-slate-800">{section.title}</h3>
                <div className="mt-3 space-y-2">
                  {section.lessons.map((lesson) => (
                    <div
                      key={lesson.id}
                      className="flex flex-col gap-3 rounded-xl bg-white p-4 ring-1 ring-slate-200 sm:flex-row sm:items-center sm:justify-between"
                    >
                      <div>
                        <p className="font-medium text-slate-900">{lesson.title}</p>
                        <p className="text-sm text-slate-500">
                          {lesson.freePreview ? "Free preview" : "Premium lesson"}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {lesson.locked ? (
                          <button className="rounded-full bg-amber-500 px-4 py-2 text-sm font-semibold text-white">
                            Upgrade
                          </button>
                        ) : (
                          <Link
                            className="rounded-full bg-sky-600 px-4 py-2 text-sm font-semibold text-white"
                            href={`/lessons/${lesson.id}`}
                          >
                            Open lesson
                          </Link>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
