export type AskSource = {
  page: number | null;
  chunk_id: string | null;
  snippet: string;
};

export type AskResponse = {
  answer: string;
  sources: AskSource[];
};

export type HealthResponse = {
  status: string;
  index_ready: boolean;
};

function getApiBase(): string {
  const base = process.env.NEXT_PUBLIC_API_URL;
  if (!base) {
    throw new Error(
      "NEXT_PUBLIC_API_URL is not set. Add it to frontend/.env.local",
    );
  }
  return base.replace(/\/$/, "");
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
    if (Array.isArray(data?.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(", ");
    }
  } catch {
    // ignore
  }
  return `Request failed (${res.status})`;
}

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${getApiBase()}/health`, {
    method: "GET",
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${getApiBase()}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}
