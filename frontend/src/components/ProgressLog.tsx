/** Progress log displaying SSE progress messages with a spinner. */

interface ProgressLogProps {
  messages: string[];
  isActive: boolean;
}

export function ProgressLog({ messages, isActive }: ProgressLogProps) {
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
      {isActive && (
        <div
          data-testid="progress-spinner"
          className="mb-2 flex items-center gap-2 text-sm text-blue-600"
        >
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
          Working...
        </div>
      )}
      <ul className="space-y-1">
        {messages.map((msg, idx) => (
          <li key={idx} className="text-sm text-slate-600">
            {msg}
          </li>
        ))}
      </ul>
    </div>
  );
}
