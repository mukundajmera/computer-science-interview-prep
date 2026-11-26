import { Metadata } from "next";
import { LEARNING_PATHS_DATA } from "@/components/learning-paths/LearningPathData";
import { LearningPathCard } from "@/components/learning-paths/LearningPathCard";

export const metadata: Metadata = {
  title: "Structured Learning Paths | System Design Prep",
  description: "Curated learning roadmaps from Junior to Staff Engineer levels with milestone tracking.",
};

export default function LearningPathsPage() {
  return (
    <div className="mx-auto max-w-5xl py-8 px-4">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100 sm:text-5xl">
          Role-Based Learning Paths
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
          Targeted curriculum roadmaps tailored for Junior, Mid, Senior, Staff+ engineers, and GenAI specialists.
          Track your milestone progress and master the topics relevant to your target tier.
        </p>
      </header>

      <div className="space-y-12">
        {LEARNING_PATHS_DATA.map((path) => (
          <LearningPathCard key={path.id} path={path} />
        ))}
      </div>
    </div>
  );
}
