import { RevealPanel } from "@/components/content/RevealPanel";

interface Props {
  revealHref: string;
}

export function SolutionReveal({ revealHref }: Props) {
  return (
    <RevealPanel
      title="🏆 Coach Answer"
      description="Try the problem on your own first. The coach answer is hidden until you choose to reveal it."
      revealHref={revealHref}
      revealLabel="Reveal Solution"
      hideLabel="Hide Solution"
      tone="amber"
    />
  );
}
