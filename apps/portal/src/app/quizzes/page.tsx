import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";
import { listQuizEntries } from "@/content/quizzes";

export default function QuizzesPage() {
  const quizzes = listQuizEntries();

  return (
    <div>
      <PageHeader
        title="📝 Quizzes"
        description="Test your knowledge with quizzes covering design patterns, LLD projects, and more. Answers are hidden by default — attempt the quiz first!"
      />

      <ContentSection>
        <ContentList
          items={quizzes}
          columns="one"
          variant="comfortable"
          emptyText="No quizzes available yet."
        />
      </ContentSection>
    </div>
  );
}
