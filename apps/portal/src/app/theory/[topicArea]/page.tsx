import { buildRegistry } from "@/content/registry";
import { slugToTitle } from "@/lib/utils";
import { ContentList } from "@/components/content/ContentList";
import { ContentSection } from "@/components/content/ContentSection";
import { PageHeader } from "@/components/content/PageHeader";
import { listDirs } from "@/content/loader";
import { notFound } from "next/navigation";

interface Props {
  params: { topicArea: string };
}

export function generateStaticParams() {
  return listDirs("00-theory").map((area) => ({ topicArea: area }));
}

export default function TopicAreaPage({ params }: Props) {
  const { theory } = buildRegistry();
  const articles = theory.filter((a) => a.topicArea === params.topicArea);
  if (articles.length === 0) notFound();

  return (
    <div>
      <PageHeader title={slugToTitle(params.topicArea)} />
      <ContentSection>
        <ContentList items={articles} columns="one" />
      </ContentSection>
    </div>
  );
}
