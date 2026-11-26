import {
  InterviewType,
} from "@/components/interview/interview-data";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";
import { listInterviewProblems } from "@/content/interviews";
import { InterviewSetup, type InterviewItem } from "@/components/interview/interview-setup";

const TYPE_LABELS: Record<InterviewType, string> = {
  lld: "LLD",
  hld: "HLD",
  "genai-hld": "GenAI HLD",
  behavioral: "Behavioral",
  "salary-negotiation": "Salary Negotiation",
  coding: "Coding",
};

const TYPE_EMOJI: Record<InterviewType, string> = {
  lld: "🏗️",
  hld: "🌐",
  "genai-hld": "🤖",
  behavioral: "🧠",
  "salary-negotiation": "💼",
  coding: "🔁",
};

export default function InterviewPage() {
  const interviewItems: InterviewItem[] = listInterviewProblems().map((problem) => ({
    id: `interview-${problem.type}-${problem.slug}`,
    href: `/interview/${problem.type}/${problem.slug}`,
    title: problem.title,
    difficulty: problem.difficulty,
    icon: TYPE_EMOJI[problem.type],
    meta: TYPE_LABELS[problem.type],
    type: problem.type,
  }));

  return (
    <div>
      <PageHeader
        title="🎯 Interview Mode"
        description="Practice system design and behavioral interviews with a step-by-step guided walkthrough. Each session follows a time-boxed template with prompts, tips, and a built-in timer."
      />

      <ContentSection>
        <InterviewSetup items={interviewItems} />
      </ContentSection>

      <div className="mt-8 rounded-lg bg-gray-50 p-4">
        <h2 className="font-semibold text-gray-700">💡 How It Works</h2>
        <ol className="mt-2 space-y-1 text-sm text-gray-600">
          <li>1. Choose a problem above to start an interview session.</li>
          <li>2. Follow the guided steps — each has a prompt and time target.</li>
          <li>3. Use the built-in timer to pace yourself.</li>
          <li>4. Jot notes in the text area for each step.</li>
          <li>5. After finishing, reveal the coach answer to compare your approach.</li>
        </ol>
      </div>
    </div>
  );
}
