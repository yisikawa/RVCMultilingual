export function apiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000`;
  }

  return "http://localhost:8000";
}

export interface Job {
  status: "pending" | "running" | "done" | "error";
  progress: number;
  message: string;
  result: Record<string, string> | null;
  error: string | null;
}

export async function translateAndTTS(params: {
  text: string;
  target_lang: string;
  lang_code: string;
  character_setting: string;
}): Promise<string> {
  const res = await fetch(`${apiBaseUrl()}/api/translate-tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(await res.text());
  const { job_id } = await res.json();
  return job_id;
}

export async function runRVC(params: {
  rvc_model: string;
  index_file: string;
}): Promise<string> {
  const res = await fetch(`${apiBaseUrl()}/api/rvc`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(await res.text());
  const { job_id } = await res.json();
  return job_id;
}

export function watchJob(
  jobId: string,
  onUpdate: (job: Job) => void
): () => void {
  const es = new EventSource(`${apiBaseUrl()}/api/status/${jobId}`);
  es.onmessage = (e) => {
    const job: Job = JSON.parse(e.data);
    onUpdate(job);
    if (job.status === "done" || job.status === "error") es.close();
  };
  es.onerror = () => es.close();
  return () => es.close();
}

export function audioUrl(filename: string): string {
  return `${apiBaseUrl()}/api/audio/${filename}`;
}
