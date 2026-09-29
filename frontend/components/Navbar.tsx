import Link from "next/link";
import { BookOpen } from "lucide-react";

const links = [
  { href: "/#about", label: "About" },
  { href: "/#how-it-works", label: "How it works" },
  { href: "/#ask", label: "What you can ask" },
  { href: "/#book", label: "The book" },
];

type NavbarProps = {
  variant?: "landing" | "chat";
};

export function Navbar({ variant = "landing" }: NavbarProps) {
  return (
    <header className="border-b border-border bg-surface/90 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <BookOpen className="h-5 w-5 text-accent" aria-hidden />
          <span>Balladesh</span>
        </Link>

        {variant === "landing" ? (
          <nav className="hidden items-center gap-6 text-sm text-muted md:flex">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className="hover:text-foreground">
                {link.label}
              </Link>
            ))}
          </nav>
        ) : (
          <p className="hidden text-sm text-muted sm:block">Grounded answers from the book</p>
        )}

        <Link
          href="/chat"
          className="rounded-md bg-accent px-3 py-2 text-sm font-medium text-white hover:opacity-90"
        >
          Open chat
        </Link>
      </div>
    </header>
  );
}
