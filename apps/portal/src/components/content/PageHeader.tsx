interface PageHeaderProps {
  title: string;
  description?: string;
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header>
      <h1 className="text-2xl font-bold">{title}</h1>
      {description ? (
        <p className="mt-1 text-gray-600">{description}</p>
      ) : null}
    </header>
  );
}
