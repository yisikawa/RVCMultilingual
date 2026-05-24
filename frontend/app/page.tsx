"use client";

import { useState, useCallback } from "react";
import SettingsPanel from "@/components/SettingsPanel";
import ProgressBar from "@/components/ProgressBar";
import { translateAndTTS, runRVC, watchJob, audioUrl, Job } from "@/lib/api";

const LANGUAGES: Record<string, string> = {
  Japanese: "ja-JP",
  "Japanese (Hakata-ben)": "ja-JP",
  English: "en-US",
  French: "fr-FR",
  Spanish: "es-ES",
  Chinese: "zh-CN",
  Korean: "ko-KR",
  German: "de-DE",
  Italian: "it-IT",
};

const idleJob = (): Job => ({
  status: "pending", progress: 0, message: "", result: null, error: null,
});

export default function Home() {
  const [text, setText] = useState("");
  const [charSetting, setCharSetting] = useState("");
  const [targetLang, setTargetLang] = useState("Japanese");
  const [rvcModel, setRvcModel] = useState("models/imadaMio.pth");
  const [indexFile, setIndexFile] = useState("models/imadaMio_v2.index");

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [ttsJob, setTtsJob] = useState<Job>(idleJob());
  const [rvcJob, setRvcJob] = useState<Job>(idleJob());
  const [translatedText, setTranslatedText] = useState("");
  const [ttsReady, setTtsReady] = useState(false);
  const [rvcReady, setRvcReady] = useState(false);

  const handleGenerateAudio = useCallback(async () => {
    setTtsJob({ status: "running", progress: 5, message: "開始中...", result: null, error: null });
    setTranslatedText("");
    setTtsReady(false);
    setRvcReady(false);
    try {
      const jobId = await translateAndTTS({
        text, target_lang: targetLang,
        lang_code: LANGUAGES[targetLang] ?? "en-US",
        character_setting: charSetting,
      });
      watchJob(jobId, (job) => {
        setTtsJob(job);
        if (job.status === "done" && job.result) {
          setTranslatedText(job.result.translated_text ?? "");
          setTtsReady(true);
        }
      });
    } catch (e) {
      setTtsJob({ status: "error", progress: 0, message: "", result: null, error: String(e) });
    }
  }, [text, targetLang, charSetting]);

  const handleRVC = useCallback(async () => {
    setRvcJob({ status: "running", progress: 5, message: "開始中...", result: null, error: null });
    setRvcReady(false);
    try {
      const jobId = await runRVC({ rvc_model: rvcModel, index_file: indexFile });
      watchJob(jobId, (job) => {
        setRvcJob(job);
        if (job.status === "done") setRvcReady(true);
      });
    } catch (e) {
      setRvcJob({ status: "error", progress: 0, message: "", result: null, error: String(e) });
    }
  }, [rvcModel, indexFile]);

  return (
    <div className="min-h-screen bg-white text-gray-800">
      <SettingsPanel
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        rvcModel={rvcModel}
        indexFile={indexFile}
        onChange={(key, val) => key === "rvcModel" ? setRvcModel(val) : setIndexFile(val)}
      />

      <header className="sticky top-0 z-30 bg-white border-b px-4 py-3 flex items-center gap-3">
        <button
          type="button"
          onClick={() => setSettingsOpen(true)}
          className="text-gray-700 p-2 rounded-md hover:bg-gray-100 text-xl leading-none"
          aria-label="Settings"
        >
          &#9776;
        </button>
        <h1 className="text-base md:text-lg font-bold">🌐 Multi-language RVC Base Generator</h1>
      </header>

      <main className="p-4 md:p-8 max-w-4xl mx-auto">
        <p className="text-gray-500 mb-6 md:mb-8 text-sm">Geminiで翻訳し、Google TTSで高品質なベース音声を生成します。</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
          {/* Left: Input */}
          <div className="space-y-6">
            <section>
              <h2 className="text-base font-semibold mb-3">1. Input Dialogue</h2>
              <label className="block text-xs text-gray-500 mb-1">Japanese Text</label>
              <textarea
                className="w-full border rounded p-2 h-28 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-gray-400"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="こんにちは、皆さんお元気ですか？"
              />
              <label className="block text-xs text-gray-500 mt-3 mb-1">Character Personality / Setting</label>
              <input
                className="w-full border rounded p-2 text-sm focus:outline-none focus:ring-1 focus:ring-gray-400"
                value={charSetting}
                onChange={(e) => setCharSetting(e.target.value)}
                placeholder="例：元気な女の子、クールな執事"
              />
            </section>

            <section>
              <h2 className="text-base font-semibold mb-3">2. Target Settings</h2>
              <label className="block text-xs text-gray-500 mb-1">Target Language</label>
              <select
                className="w-full border rounded p-2 text-sm"
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
              >
                {Object.keys(LANGUAGES).map((lang) => (
                  <option key={lang}>{lang}</option>
                ))}
              </select>

              <button
                onClick={handleGenerateAudio}
                disabled={!text || ttsJob.status === "running"}
                className="mt-4 w-full bg-gray-800 text-white rounded py-2 text-sm font-medium hover:bg-gray-700 disabled:opacity-50 transition-colors"
              >
                ✨ Generate Base Audio
              </button>

              {ttsJob.status === "running" && (
                <div className="mt-3">
                  <ProgressBar progress={ttsJob.progress} message={ttsJob.message} status={ttsJob.status} />
                </div>
              )}
              {ttsJob.error && <p className="mt-2 text-red-500 text-xs">{ttsJob.error}</p>}
            </section>
          </div>

          {/* Right: Results */}
          <div className="space-y-6">
            <section>
              <h2 className="text-base font-semibold mb-3">3. Results &amp; Playback</h2>

              <div className="mb-4">
                <p className="text-sm font-medium text-blue-600 mb-2">🔹 Base Audio (TTS)</p>
                {translatedText ? (
                  <div className="bg-blue-50 rounded p-3 text-sm mb-2">
                    <p className="text-blue-700 font-medium mb-1">Translated Script ({targetLang}):</p>
                    <p className="text-blue-600">{translatedText}</p>
                  </div>
                ) : (
                  <p className="text-gray-400 text-sm">翻訳・合成を実行するとここに表示されます。</p>
                )}
                {ttsReady && (
                  <audio key={ttsReady ? "ready" : "empty"} controls className="w-full mt-2"
                    src={audioUrl("rvc_input.wav")} />
                )}
              </div>

              <hr className="my-4" />

              <div>
                <p className="text-sm font-medium text-yellow-600 mb-2">👑 RVC Converted Voice</p>
                <button
                  onClick={handleRVC}
                  disabled={!ttsReady || rvcJob.status === "running"}
                  className="w-full bg-red-500 text-white rounded py-2 text-sm font-medium hover:bg-red-600 disabled:opacity-50 transition-colors"
                >
                  🚀 Run RVC Conversion
                </button>

                {rvcJob.status === "running" && (
                  <div className="mt-3">
                    <ProgressBar progress={rvcJob.progress} message={rvcJob.message} status={rvcJob.status} />
                  </div>
                )}
                {rvcJob.error && <p className="mt-2 text-red-500 text-xs">{rvcJob.error}</p>}

                {rvcReady && (
                  <div className="mt-3 space-y-2">
                    <p className="text-green-600 text-sm font-medium">✅ RVC Conversion Complete!</p>
                    <audio key="rvc-done" controls className="w-full"
                      src={audioUrl("rvc_result.wav")} />
                    <button
                      onClick={async () => {
                        const res = await fetch(audioUrl("rvc_result.wav"));
                        const blob = await res.blob();
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `converted_voice_${targetLang}.wav`;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                      className="block w-full text-center bg-gray-100 border rounded py-2 text-sm hover:bg-gray-200 transition-colors"
                    >
                      💾 Save Converted Voice
                    </button>
                  </div>
                )}

                {rvcJob.status === "pending" && !rvcReady && (
                  <p className="mt-2 text-gray-400 text-sm">上のボタンを押してRVC変換を実行してください。</p>
                )}
              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
