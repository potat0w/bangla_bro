export function ExampleSection() {
  return (
    <section id="example" className="scroll-mt-20 border-b border-border">
      <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6">
        <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          A sample exchange
        </h2>
        <p className="mt-3 max-w-2xl text-muted">
          Example of the kind of grounded reply you can expect in chat.
        </p>
        <div className="mt-8 space-y-4 rounded-md border border-border bg-surface p-5 sm:p-6">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted">
              You asked
            </p>
            <p className="mt-2 text-sm sm:text-base">ভাষারীতির বৈচিত্র্য কী?</p>
          </div>
          <div className="border-t border-border pt-4">
            <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted">
              Balladesh
            </p>
            <p className="mt-2 text-sm leading-relaxed text-foreground sm:text-base">
              ভাষারীতি বলতে ভাষা ব্যবহারের বিভিন্ন ধরন বা শৈলীকে বোঝায় — যেমন লেখ্য ও
              কথ্য রীতি, সাধু ও চলিত রূপ। উত্তর বইয়ের প্রাসঙ্গিক পৃষ্ঠা থেকে আসে।
            </p>
            <p className="mt-3 text-xs text-muted">Source example: Page 5</p>
          </div>
        </div>
      </div>
    </section>
  );
}
