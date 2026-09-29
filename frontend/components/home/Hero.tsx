import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function Hero() {
  return (
    <section className="bg-hero-wash">
      <div className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-16 sm:px-6 sm:py-24">
        <p className="text-sm font-medium uppercase tracking-[0.18em] text-accent">
          Balladesh
        </p>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-foreground sm:text-5xl">
          Read the Bangla book with grounded AI answers.
        </h1>
        <p className="max-w-2xl text-lg text-muted">
          Ask questions in Bangla or English. Balladesh answers from the book and shows
          the source page for every reply.
        </p>
        <div className="flex flex-wrap gap-3 pt-2">
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-md bg-accent px-4 py-3 text-sm font-medium text-white hover:opacity-90"
          >
            Start asking
            <ArrowRight className="h-4 w-4" aria-hidden />
          </Link>
          <Link
            href="/#how-it-works"
            className="inline-flex items-center rounded-md border border-border bg-surface px-4 py-3 text-sm font-medium hover:bg-background"
          >
            See how it works
          </Link>
        </div>
      </div>
    </section>
  );
}
