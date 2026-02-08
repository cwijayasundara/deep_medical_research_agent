/** Research query input with submit and stop controls. */
import { type FormEvent, useState } from "react";

interface ResearchInputProps {
  onSubmit: (query: string) => void;
  onStop: () => void;
  isLoading: boolean;
}

export function ResearchInput({
  onSubmit,
  onStop,
  isLoading,
}: ResearchInputProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        disabled={isLoading}
        placeholder="Enter a medical research question..."
        className="flex-1 rounded-md border border-slate-300 px-4 py-2 text-sm
                   focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500
                   disabled:bg-slate-100 disabled:text-slate-400"
      />
      {isLoading ? (
        <button
          type="button"
          onClick={onStop}
          className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white
                     hover:bg-red-700"
        >
          Stop
        </button>
      ) : (
        <button
          type="submit"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white
                     hover:bg-blue-700"
        >
          Research
        </button>
      )}
    </form>
  );
}
