import { LevelAssessment } from "@/components/start/level-assessment";
import { StudyTrackSelector } from "@/components/start/study-track-selector";

export const metadata = {
  title: "Start Here | System Design Prep",
  description: "Find your level and pick a study track for system design interviews.",
};

export default function StartHerePage() {
  return (
    <div className="mx-auto max-w-4xl py-8">
      <h1 className="mb-4 text-4xl font-extrabold text-gray-900 dark:text-white">
        🚀 Start Your Journey
      </h1>
      <p className="mb-10 text-lg text-gray-600 dark:text-gray-400">
        Not sure where to begin? Take the self-assessment quiz to find your recommended starting track, or pick a structured study plan based on your timeline.
      </p>

      <LevelAssessment />
      
      <div className="my-16 border-t border-gray-200 dark:border-gray-800" />
      
      <StudyTrackSelector />
    </div>
  );
}
