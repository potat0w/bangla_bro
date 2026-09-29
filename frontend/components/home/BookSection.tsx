export function BookSection() {
  return (
    <section id="book" className="scroll-mt-20 border-b border-border bg-accent-soft">
      <div className="mx-auto grid max-w-5xl gap-6 px-4 py-16 sm:px-6 md:grid-cols-2">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
            Built on Balladesh
          </h2>
          <p className="mt-3 text-muted leading-relaxed">
            The assistant is grounded in OCR text from the scanned Bangla book
            Balladesh — 121 pages indexed for retrieval.
          </p>
        </div>
        <dl className="grid gap-4 text-sm sm:grid-cols-2">
          <div className="rounded-md border border-border bg-surface p-4">
            <dt className="text-muted">Source</dt>
            <dd className="mt-1 font-medium">Balladesh.pdf</dd>
          </div>
          <div className="rounded-md border border-border bg-surface p-4">
            <dt className="text-muted">Language</dt>
            <dd className="mt-1 font-medium">Bangla (+ English questions)</dd>
          </div>
          <div className="rounded-md border border-border bg-surface p-4">
            <dt className="text-muted">Pages indexed</dt>
            <dd className="mt-1 font-medium">121</dd>
          </div>
          <div className="rounded-md border border-border bg-surface p-4">
            <dt className="text-muted">Answer style</dt>
            <dd className="mt-1 font-medium">Grounded + page sources</dd>
          </div>
        </dl>
      </div>
    </section>
  );
}
