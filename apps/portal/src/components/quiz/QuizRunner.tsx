"use client";

import { useState, useEffect } from "react";
import { StructuredQuiz } from "@/content/quiz-parser";

interface Props {
  quiz: StructuredQuiz;
}

interface Attempt {
  date: string;
  score: number;
  total: number;
  sections: Record<string, { correct: number; total: number }>;
  missed: number[];
}

export function QuizRunner({ quiz }: Props) {
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [showMissedOnly, setShowMissedOnly] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem(`quiz-progress-${quiz.slug}`);
    if (stored) {
      try {
        setAttempts(JSON.parse(stored));
      } catch {
        // ignore JSON parse error
      }
    }
  }, [quiz.slug]);

  const handleSelect = (qId: number, letter: string) => {
    // If submitted, don't allow selecting unless we are in retry mode
    if (submitted && !showMissedOnly) return;
    setAnswers((prev) => ({ ...prev, [qId]: letter }));
  };

  const handleSubmit = () => {
    setSubmitted(true);
    setShowMissedOnly(false); // Reset this on a fresh submit
    
    let correct = 0;
    const sections: Record<string, { correct: number; total: number }> = {};
    const missed: number[] = [];

    quiz.questions.forEach((q) => {
      if (!sections[q.section]) {
        sections[q.section] = { correct: 0, total: 0 };
      }
      sections[q.section].total++;

      const ans = quiz.answers[q.id]?.answer;
      if (answers[q.id] === ans) {
        correct++;
        sections[q.section].correct++;
      } else {
        missed.push(q.id);
      }
    });

    const attempt: Attempt = {
      date: new Date().toISOString(),
      score: correct,
      total: quiz.questions.length,
      sections,
      missed,
    };

    const newAttempts = [...attempts, attempt];
    setAttempts(newAttempts);
    localStorage.setItem(`quiz-progress-${quiz.slug}`, JSON.stringify(newAttempts));
  };

  const currentAttempt = submitted ? attempts[attempts.length - 1] : null;
  
  let band = quiz.bands[quiz.bands.length - 1]; // Default to lowest
  if (currentAttempt) {
      const percentage = (currentAttempt.score / currentAttempt.total) * 100;
      for (const b of quiz.bands) {
          const [min, max] = b.percentage.replace('%', '').split('-').map(Number);
          if (percentage >= min && percentage <= max) {
              band = b;
              break;
          }
      }
  }

  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="mb-6 flex justify-between items-center bg-gray-50 p-4 rounded-lg">
        <div>
          <p className="font-semibold text-gray-700">⏱️ Time suggested: {quiz.timeStr}</p>
        </div>
        {attempts.length > 0 && !submitted && (
          <div className="text-sm text-gray-500">
            Previous best: {Math.max(...attempts.map(a => a.score))}/{quiz.questions.length}
          </div>
        )}
      </div>

      {submitted && currentAttempt && (
        <div className="mb-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <h2 className="text-2xl font-bold text-blue-900 mb-2">
            Score: {currentAttempt.score} / {currentAttempt.total} ({Math.round((currentAttempt.score / currentAttempt.total) * 100)}%)
          </h2>
          <div className="mb-4">
            <span className="inline-block bg-blue-200 text-blue-800 px-3 py-1 rounded-full font-semibold mr-2">{band.assessment}</span>
            <span className="text-blue-700">{band.recommendation}</span>
          </div>
          
          <h3 className="font-semibold mb-2">Section Breakdown:</h3>
          <ul className="text-sm space-y-1 mb-4">
            {Object.entries(currentAttempt.sections).map(([sec, stats]) => (
              <li key={sec} className="flex justify-between border-b border-blue-100 pb-1">
                <span className="truncate pr-4">{sec}</span>
                <span>{stats.correct}/{stats.total}</span>
              </li>
            ))}
          </ul>
          
          {currentAttempt.missed.length > 0 && (
              <button 
                onClick={() => {
                  setShowMissedOnly(!showMissedOnly);
                  if (!showMissedOnly) {
                    setSubmitted(false); // Un-submit so they can re-answer the missed ones
                  }
                }}
                className="text-sm font-medium text-blue-600 hover:text-blue-800 underline"
              >
                  {showMissedOnly ? "Show all questions" : "Retry/Review missed only"}
              </button>
          )}
        </div>
      )}

      <div className="space-y-8">
        {quiz.questions
          .filter(q => showMissedOnly ? currentAttempt?.missed.includes(q.id) : true)
          .map((q) => (
          <div key={q.id} className="border border-gray-200 rounded-lg p-6 bg-white shadow-sm">
            <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">{q.section}</div>
            <h3 className="text-lg font-medium text-gray-900 mb-4 whitespace-pre-wrap">
              {q.id}. {q.text}
            </h3>
            <div className="space-y-2">
              {q.options.map((opt) => {
                const isSelected = answers[q.id] === opt.letter;
                const isCorrect = submitted && quiz.answers[q.id]?.answer === opt.letter;
                const isWrongSelected = submitted && isSelected && !isCorrect;
                
                let bgClass = "bg-white hover:bg-gray-50 border-gray-300";
                if (isSelected && !submitted) bgClass = "bg-blue-50 border-blue-500 text-blue-700";
                if (submitted && isCorrect) bgClass = "bg-green-100 border-green-500 text-green-800";
                if (submitted && isWrongSelected) bgClass = "bg-red-100 border-red-500 text-red-800";

                return (
                  <button
                    key={opt.letter}
                    onClick={() => handleSelect(q.id, opt.letter)}
                    disabled={submitted && !showMissedOnly}
                    className={`w-full text-left p-3 rounded border transition-colors flex items-start ${bgClass}`}
                  >
                    <span className="font-bold mr-3">{opt.letter})</span>
                    <span>{opt.text}</span>
                  </button>
                );
              })}
            </div>
            {submitted && quiz.answers[q.id] && (
                <div className="mt-4 p-4 bg-gray-50 rounded text-sm text-gray-700">
                    <strong>Explanation:</strong>
                    <div className="mt-1 whitespace-pre-wrap">{quiz.answers[q.id].explanation}</div>
                </div>
            )}
          </div>
        ))}
      </div>

      {!submitted && (
        <div className="mt-8 flex justify-end">
          <button
            onClick={handleSubmit}
            disabled={Object.keys(answers).length === 0}
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Submit Quiz
          </button>
        </div>
      )}
    </div>
  );
}
