interface InsightProps {
  title: string;
  description: string;
  severity: string;
}

const severityStyles: Record<string, { border: string; bg: string; icon: string }> = {
  info: {
    border: "border-blue-500/30",
    bg: "bg-blue-500/5",
    icon: "text-blue-400",
  },
  warning: {
    border: "border-amber-500/30",
    bg: "bg-amber-500/5",
    icon: "text-amber-400",
  },
  alert: {
    border: "border-red-500/30",
    bg: "bg-red-500/5",
    icon: "text-red-400",
  },
};

export default function InsightCard({ title, description, severity }: InsightProps) {
  const style = severityStyles[severity] || severityStyles.info;

  return (
    <div className={`rounded-xl border ${style.border} ${style.bg} p-4`}>
      <div className="flex items-start gap-3">
        <div className={`mt-0.5 ${style.icon}`}>
          {severity === "alert" ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          ) : severity === "warning" ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          )}
        </div>
        <div>
          <h4 className="font-semibold text-zinc-200 text-sm">{title}</h4>
          <p className="text-zinc-400 text-sm mt-1">{description}</p>
        </div>
      </div>
    </div>
  );
}
