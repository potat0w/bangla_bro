import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-8 text-sm text-muted sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p>
          <span className="font-medium text-foreground">Balladesh</span> — Bangla book
          reading assistant
        </p>
        <div className="flex gap-4">
          <Link href="/" className="hover:text-foreground">
            Home
          </Link>
          <Link href="/chat" className="hover:text-foreground">
            Chat
          </Link>
          {/* /about reserved for later */}
        </div>
      </div>
    </footer>
  );
}
