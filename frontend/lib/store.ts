"use client";

import { create } from "zustand";

export type LessonNode = {
  id: string;
  title: string;
  locked?: boolean;
  freePreview?: boolean;
  videoUrl?: string;
  quizId?: string;
  assignmentId?: string;
};

export type SectionNode = {
  id: string;
  title: string;
  lessons: LessonNode[];
};

export type CourseNode = {
  id: string;
  title: string;
  description?: string;
  sections: SectionNode[];
};

export type Enrollment = {
  id: string;
  courseId: string;
  stage?: string;
  stage1Completed?: boolean;
  stage2Completed?: boolean;
  stage1Locked?: boolean;
};

export type Badge = {
  id: string;
  name: string;
  description?: string;
  imageUrl?: string;
};

export type GamificationStatus = {
  xp?: number;
  streak?: number;
  badges?: Badge[];
  stage?: string;
  stageProgress?: number;
};

type SessionState = {
  enrollment?: Enrollment | null;
  gamification?: GamificationStatus | null;
  courses: CourseNode[];
  setEnrollment: (enrollment: Enrollment | null) => void;
  setGamification: (gamification: GamificationStatus | null) => void;
  setCourses: (courses: CourseNode[]) => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  enrollment: null,
  gamification: null,
  courses: [],
  setEnrollment: (enrollment) => set({ enrollment }),
  setGamification: (gamification) => set({ gamification }),
  setCourses: (courses) => set({ courses }),
}));
