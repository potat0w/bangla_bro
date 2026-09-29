"use client";

import { FormEvent, useEffect, useState } from "react";
import { LoaderCircle, Send } from "lucide-react";
import { askQuestion, AskResponse, checkHealth } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: AskResponse["sources"];
};

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [indexReady, setIndexReady] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth()
      .then((h) => setIndexReady(h.index_ready))
      .catch(() => setIndexReady(false));
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setError(null);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const result = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-3xl flex-col px-4 py-6 sm:px-6">
      <div className="mb-4 flex items-center justify-between gap-3 text-sm">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Chat with Balladesh</h1>
          <p className="text-muted">Ask in Bangla or English. Answers cite book pages.</p>
        </div>
        <span
          className={`rounded-full px-2.5 py-1 text-xs font-medium ${
            indexReady
              ? "bg-accent-soft text-accent"
              : "bg-border text-muted"
          }`}
        >
          {indexReady === null
            ? "Checking API…"
            : indexReady
              ? "Index ready"
              : "API offline"}
        </span>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto rounded-md border border-border bg-surface p-4">
        {messages.length === 0 && (
          <p className="text-sm text-muted">
            Try: ভাষারীতির বৈচিত্র্য কী?
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={`${msg.role}-${i}`}
            className={`max-w-[90%] rounded-md px-3 py-2 text-sm leading-relaxed ${
              msg.role === "user"
                ? "ml-auto bg-accent text-white"
                : "bg-background text-foreground"
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <ul className="mt-3 space-y-2 border-t border-border/60 pt-2 text-xs text-muted">
                {msg.sources.map((s, j) => (
                  <li key={`${s.chunk_id}-${j}`}>
                    <span className="font-medium text-foreground">
                      Page {s.page ?? "?"}
                    </span>
                    {s.chunk_id ? ` — ${s.chunk_id}` : ""}
                    {s.snippet ? (
                      <span className="mt-0.5 block text-muted">{s.snippet}</span>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {loading && (
          <p className="inline-flex items-center gap-2 text-sm text-muted">
            <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden />
            Thinking…
          </p>
        )}
      </div>

      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}

      <form onSubmit={onSubmit} className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about Balladesh…"
          className="min-w-0 flex-1 rounded-md border border-border bg-surface px-3 py-3 text-sm outline-none focus:border-accent"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="inline-flex items-center gap-2 rounded-md bg-accent px-4 py-3 text-sm font-medium text-white disabled:opacity-50"
        >
          <Send className="h-4 w-4" aria-hidden />
          Ask
        </button>
      </form>
    </div>
  );
}
