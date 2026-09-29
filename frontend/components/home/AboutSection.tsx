export function AboutSection() {
  return (
    <section id="about" className="scroll-mt-20 border-b border-border">
      <div className="mx-auto grid max-w-5xl gap-6 px-4 py-16 sm:px-6 md:grid-cols-[1fr_1.4fr]">
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          A reading companion for Balladesh
        </h2>
        <p className="text-muted leading-relaxed">
          Balladesh-RAG helps you explore the scanned Bangla book without flipping
          endless pages. Ask about language, style, or passages — and get answers
          tied back to the original text.
        </p>
      </div>
    </section>
  );
}
