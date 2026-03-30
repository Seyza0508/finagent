"use client";

import { useState } from "react";

interface Step {
  step_number: number;
  tool_name: string;
  tool_input: Record<string, unknown>;
  tool_output: string;
  reasoning: string;
}

export default function AgentSteps({ steps }: { steps: Step[] }) {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedStep, setExpandedStep] = useState<number | null>(null);

  if (steps.length === 0) return null;

  return (
    <div className="rounded-xl border border-zinc-800 overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-5 py-4 bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center">
            <svg
              className="w-4 h-4 text-emerald-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
          <span className="font-medium text-zinc-200">
            Agent Reasoning ({steps.length} steps)
          </span>
        </div>
        <svg
          className={`w-5 h-5 text-zinc-500 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="border-t border-zinc-800 divide-y divide-zinc-800/50">
          {steps.map((step) => (
            <div key={step.step_number} className="px-5 py-3">
              <button
                onClick={() =>
                  setExpandedStep(
                    expandedStep === step.step_number
                      ? null
                      : step.step_number
                  )
                }
                className="w-full flex items-center gap-3 text-left"
              >
                <span className="w-6 h-6 flex-shrink-0 rounded-full bg-zinc-800 text-xs flex items-center justify-center text-zinc-400">
                  {step.step_number}
                </span>
                <span className="text-sm font-mono text-emerald-400">
                  {step.tool_name}
                </span>
                <span className="text-xs text-zinc-600 truncate flex-1">
                  {step.reasoning}
                </span>
                <svg
                  className={`w-4 h-4 text-zinc-600 transition-transform flex-shrink-0 ${
                    expandedStep === step.step_number ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {expandedStep === step.step_number && (
                <div className="mt-3 ml-9 space-y-2">
                  <div>
                    <p className="text-xs text-zinc-600 mb-1">Input:</p>
                    <pre className="text-xs text-zinc-400 bg-zinc-900 rounded-lg p-3 overflow-x-auto max-h-40 overflow-y-auto">
                      {JSON.stringify(step.tool_input, null, 2)}
                    </pre>
                  </div>
                  {step.tool_output && (
                    <div>
                      <p className="text-xs text-zinc-600 mb-1">Output:</p>
                      <pre className="text-xs text-zinc-400 bg-zinc-900 rounded-lg p-3 overflow-x-auto max-h-40 overflow-y-auto">
                        {step.tool_output}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
