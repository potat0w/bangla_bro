import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function FinalCta() {
  return (
    <section className="bg-foreground text-background">
      <div className="mx-auto flex max-w-5xl flex-col items-start gap-5 px-4 py-16 sm:px-6 sm:py-20">
        <h2 className="max-w-2xl text-3xl font-semibold tracking-tight sm:text-4xl">
          Ready to read Balladesh with questions?
        </h2>
        <p className="max-w-xl text-background/75">
          Open the chat and ask anything the book can support — with source pages
          attached.
        </p>
        <Link
          href="/chat"
          className="inline-flex items-center gap-2 rounded-md bg-accent px-4 py-3 text-sm font-medium text-white hover:opacity-90"
        >
          Go to chat
          <ArrowRight className="h-4 w-4" aria-hidden />
        </Link>
      </div>
    </section>
  );
}
