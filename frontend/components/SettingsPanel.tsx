"use client";

import { useState, useEffect } from "react";
import { apiBaseUrl } from "@/lib/api";

interface Props {
  open: boolean;
  onClose: () => void;
  rvcModel: string;
  indexFile: string;
  onChange: (key: "rvcModel" | "indexFile", value: string) => void;
}

interface Models {
  pth: string[];
  index: string[];
}

export default function SettingsPanel({ open, onClose, rvcModel, indexFile, onChange }: Props) {
  const [models, setModels] = useState<Models>({ pth: [], index: [] });

  useEffect(() => {
    fetch(`${apiBaseUrl()}/api/models`)
      .then((r) => r.json())
      .then(setModels)
      .catch(() => {});
  }, []);

  const label = (path: string) => path.replace(/^models[/\\]/, "");

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />

      <div className="fixed top-0 left-0 h-full w-72 bg-white shadow-2xl z-50 overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="font-semibold text-gray-700">&#127897; RVC Settings</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none p-2"
          >
            &#x2715;
          </button>
        </div>

        <div className="p-4 space-y-5 text-sm">
          <div>
            <label className="block text-gray-600 mb-1">RVC Model</label>
            <select
              className="w-full border rounded px-2 py-2"
              value={rvcModel}
              onChange={(e) => onChange("rvcModel", e.target.value)}
            >
              {models.pth.length === 0 && (
                <option value={rvcModel}>{label(rvcModel)}</option>
              )}
              {models.pth.map((f) => (
                <option key={f} value={f}>{label(f)}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-gray-600 mb-1">Index File</label>
            <select
              className="w-full border rounded px-2 py-2"
              value={indexFile}
              onChange={(e) => onChange("indexFile", e.target.value)}
            >
              <option value="">(none)</option>
              {models.index.length === 0 && indexFile && (
                <option value={indexFile}>{label(indexFile)}</option>
              )}
              {models.index.map((f) => (
                <option key={f} value={f}>{label(f)}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </>
  );
}
