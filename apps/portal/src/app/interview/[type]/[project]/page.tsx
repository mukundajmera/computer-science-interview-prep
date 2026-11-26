import { notFound } from "next/navigation";
import {
  getTemplate,
} from "@/components/interview/interview-data";
import { InterviewStepper } from "@/components/interview/InterviewStepper";
import { SolutionReveal } from "@/components/interview/SolutionReveal";
import { listInterviewProblems } from "@/content/interviews";

interface Props {
  params: { type: string; project: string };
}

export function generateStaticParams() {
  return listInterviewProblems().map((p) => ({
    type: p.type,
    project: p.slug,
  }));
}

export default async function InterviewSessionPage({ params }: Props) {
  const problem = listInterviewProblems().find(
    (p) => p.type === params.type && p.slug === params.project
  );
  if (!problem) notFound();

  const template = getTemplate(problem.type);
  if (!template) notFound();

  return (
    <div>
      <InterviewStepper template={template} problemTitle={problem.title} />
      <SolutionReveal
        revealHref={`../../../reveal/solution/${problem.type}/${problem.slug}/`}
      />
    </div>
  );
}
