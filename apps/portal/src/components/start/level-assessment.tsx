"use client";

import { useState } from "react";
import Link from "next/link";

type Level = "Junior" | "Mid" | "Senior" | "Staff" | null;

const questions = [
  {
    id: 1,
    question: "How many years of software engineering experience do you have?",
    options: [
      { text: "0-2 years", value: 1 },
      { text: "3-5 years", value: 2 },
      { text: "6-9 years", value: 3 },
      { text: "10+ years", value: 4 },
    ],
  },
  {
    id: 2,
    question: "Have you ever led the design of a distributed system from scratch?",
    options: [
      { text: "No, mostly worked on existing services", value: 1 },
      { text: "Yes, but with significant guidance", value: 2 },
      { text: "Yes, led a mid-sized service design independently", value: 3 },
      { text: "Yes, led complex, cross-team distributed architectures", value: 4 },
    ],
  },
  {
    id: 3,
    question: "How comfortable are you with concepts like Consistent Hashing, Paxos/Raft, and LSM Trees?",
    options: [
      { text: "What are those?", value: 1 },
      { text: "I know the high-level concepts", value: 2 },
      { text: "I can explain how they work and their trade-offs", value: 3 },
      { text: "I have implemented them or debugged deep issues in systems using them", value: 4 },
    ],
  },
  {
    id: 4,
    question: "What is your primary goal for system design preparation?",
    options: [
      { text: "Learn the basics to pass a standard engineering loop", value: 1 },
      { text: "Nail a mid-level design interview", value: 2 },
      { text: "Target Senior Engineering roles at Big Tech", value: 3 },
      { text: "Target Staff/Principal roles with deep dives", value: 4 },
    ],
  },
];

export function LevelAssessment() {
  const [currentStep, setCurrentStep] = useState(0);
  const [scores, setScores] = useState<number[]>([]);
  const [result, setResult] = useState<Level>(null);

  const handleAnswer = (value: number) => {
    const newScores = [...scores, value];
    setScores(newScores);

    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      calculateResult(newScores);
    }
  };

  const calculateResult = (finalScores: number[]) => {
    const total = finalScores.reduce((a, b) => a + b, 0);
    let level: Level = "Junior";
    if (total >= 14) level = "Staff";
    else if (total >= 10) level = "Senior";
    else if (total >= 6) level = "Mid";
    setResult(level);
  };

  const reset = () => {
    setCurrentStep(0);
    setScores([]);
    setResult(null);
  };

  const getRecommendation = (level: Level) => {
    switch (level) {
      case "Junior":
        return {
          title: "Foundations Track",
          desc: "Start with 00 Theory, then move to 01 Patterns. Once comfortable, tackle 02 LLD.",
          links: [
            { label: "00 Theory", href: "/theory" },
            { label: "01 Patterns", href: "/patterns" },
          ],
        };
      case "Mid":
        return {
          title: "Builder Track",
          desc: "Review 01 Patterns quickly, then dive deep into 02 LLD and start with basic 03 HLD Concepts.",
          links: [
            { label: "02 LLD Projects", href: "/lld" },
            { label: "03 HLD Concepts", href: "/hld-concepts" },
          ],
        };
      case "Senior":
        return {
          title: "Architect Track",
          desc: "Skim 03 HLD Concepts, focus heavily on 04 HLD Projects, and try Mock Interviews.",
          links: [
            { label: "03 HLD Concepts", href: "/hld-concepts" },
            { label: "04 HLD Projects", href: "/hld" },
          ],
        };
      case "Staff":
        return {
          title: "Principal Track",
          desc: "Focus on edge cases in 04 HLD Projects, system scaling limits, and explore 06 GenAI Systems.",
          links: [
            { label: "04 HLD Projects", href: "/hld" },
            { label: "06 GenAI Systems", href: "/genai" },
          ],
        };
      default:
        return null;
    }
  };

  if (result) {
    const rec = getRecommendation(result);
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            You are testing at a <span className="text-blue-600 dark:text-blue-400">{result}</span> level!
          </h3>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Based on your answers, here is your recommended starting track:
          </p>
        </div>

        {rec && (
          <div className="mt-6 rounded-lg bg-blue-50 p-6 dark:bg-blue-900/20">
            <h4 className="text-xl font-semibold text-blue-900 dark:text-blue-100">
              {rec.title}
            </h4>
            <p className="mt-2 text-blue-800 dark:text-blue-200">{rec.desc}</p>
            <div className="mt-4 flex flex-wrap gap-3">
              {rec.links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={reset}
          className="mt-6 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
        >
          Retake Assessment
        </button>
      </div>
    );
  }

  const question = questions[currentStep];

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-950">
      <div className="mb-6 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Self-Assessment Quiz
        </h3>
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
          Question {currentStep + 1} of {questions.length}
        </span>
      </div>

      <div className="mb-2 h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
        <div
          className="h-full bg-blue-600 transition-all duration-300 dark:bg-blue-500"
          style={{ width: `${((currentStep + 1) / questions.length) * 100}%` }}
        />
      </div>

      <div className="mt-8">
        <h4 className="mb-4 text-xl font-medium text-gray-800 dark:text-gray-200">
          {question.question}
        </h4>
        <div className="space-y-3">
          {question.options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => handleAnswer(option.value)}
              className="w-full rounded-lg border border-gray-200 p-4 text-left transition-colors hover:border-blue-500 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-800 dark:hover:border-blue-500 dark:hover:bg-blue-900/20"
            >
              <span className="text-gray-700 dark:text-gray-300">
                {option.text}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
