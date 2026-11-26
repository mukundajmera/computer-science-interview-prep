"use client";

import { RevealPanel } from "@/components/content/RevealPanel";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import { useState } from "react";
import { QuizRunner } from "@/components/quiz/QuizRunner";

import { StructuredQuiz } from "@/content/quiz-parser";

interface Props {
  quizHtml: string;
  answersHref: string | null;
  structuredQuiz?: StructuredQuiz | null;
}

export function QuizViewer({ quizHtml, answersHref, structuredQuiz }: Props) {
  const [viewMode, setViewMode] = useState<'interactive' | 'markdown'>(structuredQuiz ? 'interactive' : 'markdown');

  return (
    <div>
      {structuredQuiz && (
        <div className="flex border-b border-gray-200 mb-6">
          <button
            className={`py-2 px-4 font-medium text-sm border-b-2 transition-colors ${viewMode === 'interactive' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
            onClick={() => setViewMode('interactive')}
          >
            Interactive Mode
          </button>
          <button
            className={`py-2 px-4 font-medium text-sm border-b-2 transition-colors ${viewMode === 'markdown' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
            onClick={() => setViewMode('markdown')}
          >
            Markdown View
          </button>
        </div>
      )}

      {viewMode === 'interactive' && structuredQuiz ? (
        <QuizRunner quiz={structuredQuiz} />
      ) : (
        <>
          <MarkdownRenderer html={quizHtml} />
          {answersHref && (
            <RevealPanel
              title="📝 Answer Key"
              description="Complete the quiz first, then reveal the answers to check your score."
              revealHref={answersHref}
              revealLabel="Reveal Answers"
              hideLabel="Hide Answers"
              tone="green"
            />
          )}
        </>
      )}
    </div>
  );
}
