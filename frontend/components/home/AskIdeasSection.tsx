const ideas = [
  "ভাষারীতির বৈচিত্র্য কী?",
  "সাধু ও চলিত রীতির পার্থক্য কী?",
  "What does the book say about Bangla dialects?",
  "Summarize the idea of মান্য ভাষা from the book.",
];

export function AskIdeasSection() {
  return (
    <section id="ask" className="scroll-mt-20 border-b border-border">
      <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          What you can ask
        </h2>
        <p className="mt-3 max-w-2xl text-muted">
          Start with language, style, definitions, or chapter ideas from Balladesh.
        </p>
        <ul className="mt-8 grid gap-3 sm:grid-cols-2">
          {ideas.map((idea) => (
            <li
              key={idea}
              className="rounded-md border border-border bg-surface px-4 py-3 text-sm"
            >
              {idea}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
