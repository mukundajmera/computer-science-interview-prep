interface ContentSectionProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function ContentSection({
  title,
  description,
  children,
  className = "mt-6",
}: ContentSectionProps) {
  return (
    <section className={className}>
      {title ? <h2 className="text-lg font-semibold">{title}</h2> : null}
      {description ? (
        <p className="mt-1 text-sm text-gray-500">{description}</p>
      ) : null}
      <div className={title || description ? "mt-3" : undefined}>{children}</div>
    </section>
  );
}
