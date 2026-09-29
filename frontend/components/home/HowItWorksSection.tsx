const steps = [
  {
    n: "01",
    title: "Ask naturally",
    body: "Type a question in Bangla or English, the way you would ask a careful reader.",
  },
  {
    n: "02",
    title: "Find relevant pages",
    body: "The backend retrieves the closest passages from the indexed Balladesh book.",
  },
  {
    n: "03",
    title: "Get a grounded answer",
    body: "You receive a clear reply plus source pages — not invented page numbers.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="scroll-mt-20 border-b border-border bg-surface">
      <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">How it works</h2>
        <p className="mt-3 max-w-2xl text-muted">
          Next.js talks to FastAPI. FastAPI runs Balladesh RAG. The browser never
          touches FAISS, OCR, or Groq directly.
        </p>
        <ol className="mt-10 grid gap-8 sm:grid-cols-3">
          {steps.map((step) => (
            <li key={step.n} className="space-y-2">
              <p className="text-xs font-medium uppercase tracking-[0.16em] text-accent">
                {step.n}
              </p>
              <h3 className="text-lg font-medium">{step.title}</h3>
              <p className="text-sm leading-relaxed text-muted">{step.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
