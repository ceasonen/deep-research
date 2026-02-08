'use client';

import { useMemo, useState } from 'react';

import { postLLMVerify } from '@/lib/api';
import type { RuntimeLLMConfig } from '@/types';

interface ApiConfigPanelProps {
  config: RuntimeLLMConfig | null;
  onSave: (config: RuntimeLLMConfig | null) => void;
}

const presets = [
  { label: 'OpenAI Compatible', base_url: '', model: '' },
  { label: 'Groq', base_url: 'https://api.groq.com/openai/v1', model: 'llama-3.3-70b-versatile' },
  { label: 'OpenRouter Free', base_url: 'https://openrouter.ai/api/v1', model: 'openrouter/free' },
  { label: 'Gemini OpenAI', base_url: 'https://generativelanguage.googleapis.com/v1beta/openai/', model: 'gemini-2.5-flash' },
];

export function ApiConfigPanel({ config, onSave }: ApiConfigPanelProps) {
  const [open, setOpen] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; text: string } | null>(null);
  const [draft, setDraft] = useState<RuntimeLLMConfig>({
    base_url: config?.base_url || '',
    api_key: config?.api_key || '',
    model: config?.model || '',
    temperature: config?.temperature ?? 0.2,
    max_tokens: config?.max_tokens ?? 1200,
  });

  const configuredLabel = useMemo(() => {
    if (!config?.base_url || !config?.model) return 'No API';
    return `API: ${config.model}`;
  }, [config]);

  function openPanel() {
    setDraft({
      base_url: config?.base_url || '',
      api_key: config?.api_key || '',
      model: config?.model || '',
      temperature: config?.temperature ?? 0.2,
      max_tokens: config?.max_tokens ?? 1200,
    });
    setOpen(true);
    setTestResult(null);
  }

  function savePanel() {
    const parsedTemp = Number(draft.temperature ?? 0.2);
    const parsedMaxTokens = Number(draft.max_tokens ?? 1200);
    const cleaned: RuntimeLLMConfig = {
      base_url: (draft.base_url || '').trim(),
      api_key: (draft.api_key || '').trim(),
      model: (draft.model || '').trim(),
      temperature: Number.isFinite(parsedTemp) ? parsedTemp : 0.2,
      max_tokens: Number.isFinite(parsedMaxTokens) ? parsedMaxTokens : 1200,
    };
    if (!cleaned.base_url || !cleaned.model) {
      onSave(null);
    } else {
      onSave(cleaned);
    }
    setOpen(false);
  }

  async function runVerify() {
    const payload: RuntimeLLMConfig = {
      base_url: (draft.base_url || '').trim(),
      api_key: (draft.api_key || '').trim(),
      model: (draft.model || '').trim(),
      temperature: draft.temperature ?? 0.2,
      max_tokens: draft.max_tokens ?? 1200,
    };
    setTesting(true);
    setTestResult(null);
    try {
      const response = await postLLMVerify(payload);
      const data = (await response.json()) as { ok: boolean; model_used: string; message: string };
      setTestResult({
        ok: Boolean(data.ok),
        text: `${data.ok ? 'OK' : 'Failed'} · ${data.model_used} · ${data.message}`,
      });
    } catch (error) {
      setTestResult({ ok: false, text: `Failed · ${(error as Error).message}` });
    } finally {
      setTesting(false);
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={openPanel}
        className="soft-ring hover-lift fixed left-4 top-4 z-40 rounded-full border border-ink/20 bg-white/85 px-4 py-2 text-xs text-ink shadow-soft md:text-sm"
      >
        {configuredLabel}
      </button>

      {open ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 p-4">
          <section className="glass-panel w-full max-w-xl space-y-4 p-5">
            <div className="flex items-center justify-between">
              <h3 className="font-display text-2xl text-ink">Runtime LLM API</h3>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="soft-ring rounded-full border border-ink/20 bg-white/70 px-3 py-1 text-xs text-ink"
              >
                Close
              </button>
            </div>

            <div className="flex flex-wrap gap-2">
              {presets.map((item) => (
                <button
                  key={item.label}
                  type="button"
                  onClick={() => setDraft((prev) => ({ ...prev, base_url: item.base_url, model: item.model }))}
                  className="soft-ring rounded-full border border-ink/20 bg-sand px-3 py-1 text-xs text-ink"
                >
                  {item.label}
                </button>
              ))}
            </div>

            <label className="block space-y-1">
              <span className="text-xs text-ink/75">Base URL (OpenAI compatible)</span>
              <input
                value={draft.base_url || ''}
                onChange={(event) => setDraft((prev) => ({ ...prev, base_url: event.target.value }))}
                className="soft-ring h-11 w-full rounded-xl border border-ink/20 bg-white/85 px-3 text-sm text-ink outline-none"
                placeholder="https://api.groq.com/openai/v1"
              />
            </label>

            <label className="block space-y-1">
              <span className="text-xs text-ink/75">API Key</span>
              <input
                type="password"
                value={draft.api_key || ''}
                onChange={(event) => setDraft((prev) => ({ ...prev, api_key: event.target.value }))}
                className="soft-ring h-11 w-full rounded-xl border border-ink/20 bg-white/85 px-3 text-sm text-ink outline-none"
                placeholder="AIza... or sk-..."
              />
            </label>

            <div className="grid gap-3 md:grid-cols-4">
              <label className="block space-y-1 md:col-span-2">
                <span className="text-xs text-ink/75">Model</span>
                <input
                  value={draft.model || ''}
                  onChange={(event) => setDraft((prev) => ({ ...prev, model: event.target.value }))}
                  className="soft-ring h-11 w-full rounded-xl border border-ink/20 bg-white/85 px-3 text-sm text-ink outline-none"
                  placeholder="llama-3.3-70b-versatile"
                />
              </label>
              <label className="block space-y-1">
                <span className="text-xs text-ink/75">Temperature</span>
                <input
                  type="number"
                  min={0}
                  max={2}
                  step={0.1}
                  value={draft.temperature ?? 0.2}
                  onChange={(event) => setDraft((prev) => ({ ...prev, temperature: Number(event.target.value) }))}
                  className="soft-ring h-11 w-full rounded-xl border border-ink/20 bg-white/85 px-3 text-sm text-ink outline-none"
                />
              </label>
              <label className="block space-y-1">
                <span className="text-xs text-ink/75">Max Tokens</span>
                <input
                  type="number"
                  min={64}
                  max={32768}
                  step={64}
                  value={draft.max_tokens ?? 1200}
                  onChange={(event) => setDraft((prev) => ({ ...prev, max_tokens: Number(event.target.value) }))}
                  className="soft-ring h-11 w-full rounded-xl border border-ink/20 bg-white/85 px-3 text-sm text-ink outline-none"
                />
              </label>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={runVerify}
                disabled={testing}
                className="soft-ring rounded-full border border-ink/20 bg-white/75 px-4 py-2 text-sm text-ink disabled:opacity-60"
              >
                {testing ? 'Testing...' : 'Test Connection'}
              </button>
              <button
                type="button"
                onClick={savePanel}
                className="soft-ring rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white"
              >
                Save
              </button>
              <button
                type="button"
                onClick={() => {
                  onSave(null);
                  setOpen(false);
                }}
                className="soft-ring rounded-full border border-ink/20 bg-white/75 px-4 py-2 text-sm text-ink"
              >
                Disable Runtime API
              </button>
              <p className="text-xs text-ink/65">Saved locally in your browser. Sent only with your search requests.</p>
            </div>
            {testResult ? (
              <p className={`rounded-xl p-2 text-xs ${testResult.ok ? 'bg-mint/20 text-ink' : 'bg-ember/15 text-ember'}`}>
                {testResult.text}
              </p>
            ) : null}
          </section>
        </div>
      ) : null}
    </>
  );
}
