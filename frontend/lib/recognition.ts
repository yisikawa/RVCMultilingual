// Web Speech API (SpeechRecognition) wrapper.
// Handles cross-browser quirks: iOS non-Safari, Android Chrome auto-stop,
// and recovers interim text when the engine never marks it final.

export interface RecognitionOptions {
  lang: string;
  captureAudio?: boolean;
  onInterim?: (text: string) => void;
  onFinal?: (text: string) => void;
  onSoundStart?: () => void;
  onSoundEnd?: () => void;
  onEnd?: () => void;
  onError?: (error: string) => void;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type SpeechRecognitionCtor = new () => any;

function getCtor(): SpeechRecognitionCtor | undefined {
  if (typeof window === "undefined") return undefined;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = window as any;
  return w.SpeechRecognition ?? w.webkitSpeechRecognition;
}

// iOS Chrome/Firefox expose webkitSpeechRecognition but always fail with
// "service-not-allowed". Treat them as unsupported and force Safari.
function isIOSNonSafari(): boolean {
  if (typeof navigator === "undefined") return false;
  const ua = navigator.userAgent;
  if (!/iPad|iPhone|iPod/.test(ua)) return false;
  return /CriOS|FxiOS|OPiOS/.test(ua);
}

export function isAndroid(): boolean {
  if (typeof navigator === "undefined") return false;
  return /Android/i.test(navigator.userAgent);
}

export function isSupported(): boolean {
  if (isIOSNonSafari()) return false;
  return !!getCtor() && !!navigator.mediaDevices;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let current: any | null = null;
let currentStream: MediaStream | null = null;
// Android Chrome ends sessions early even with continuous=true.
// Restart automatically while shouldContinue is set.
let shouldContinue = false;

function releaseStream() {
  currentStream?.getTracks().forEach((t) => t.stop());
  currentStream = null;
}

function startRec(Ctor: SpeechRecognitionCtor, options: RecognitionOptions): void {
  // Track the last interim phrase so we can finalize it on end
  // (Android Chrome sometimes never sets isFinal=true).
  let lastInterim = "";

  const rec = new Ctor();
  rec.lang = options.lang;
  rec.continuous = true;
  rec.interimResults = true;

  rec.onsoundstart = () => options.onSoundStart?.();
  rec.onsoundend = () => options.onSoundEnd?.();

  rec.onresult = (event: { resultIndex: number; results: SpeechRecognitionResultList }) => {
    let interim = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i];
      if (result.isFinal) {
        const text = result[0].transcript.trim();
        if (text) {
          options.onFinal?.(text);
          lastInterim = "";
        }
      } else {
        interim += result[0].transcript;
      }
    }
    lastInterim = interim.trim();
    options.onInterim?.(lastInterim);
  };

  rec.onend = () => {
    current = null;
    if (shouldContinue) {
      try {
        startRec(Ctor, options);
        return;
      } catch {
        shouldContinue = false;
      }
    }
    if (lastInterim) {
      options.onFinal?.(lastInterim);
      options.onInterim?.("");
      lastInterim = "";
    }
    releaseStream();
    options.onEnd?.();
  };

  rec.onerror = (event: { error: string }) => {
    console.warn("[SpeechRecognition] error:", event.error);
    // no-speech / aborted are non-fatal; let onend handle restart.
    if (event.error === "no-speech" || event.error === "aborted") return;
    shouldContinue = false;
    options.onError?.(event.error);
  };

  current = rec;
  try {
    rec.start();
  } catch (e) {
    shouldContinue = false;
    current = null;
    options.onError?.(e instanceof Error ? e.name : "start-failed");
    options.onEnd?.();
  }
}

export async function start(options: RecognitionOptions): Promise<MediaStream | null> {
  const Ctor = getCtor();
  if (!Ctor) return null;
  stop();
  shouldContinue = true;

  if (options.captureAudio !== false) {
    try {
      currentStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      options.onError?.("not-allowed");
      options.onEnd?.();
      return null;
    }
  }

  startRec(Ctor, options);
  return currentStream;
}

export function stop(): void {
  shouldContinue = false;
  if (current) {
    current.stop();
    current = null;
  }
  releaseStream();
}
