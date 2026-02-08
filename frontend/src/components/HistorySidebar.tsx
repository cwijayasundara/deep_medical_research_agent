/** Sidebar displaying research history with clickable report entries. */

import type { ReportSummary } from "../lib/reports-api.ts";

const EMPTY_STATE_MESSAGE =
  "No research history yet. Start by asking a question!";
const SIDEBAR_HEADING = "Research History";

interface HistorySidebarProps {
  reports: ReportSummary[];
  onSelectReport: (reportId: string) => void;
  selectedReportId?: string | null;
}

export function HistorySidebar({
  reports,
  onSelectReport,
  selectedReportId,
}: HistorySidebarProps) {
  return (
    <div>
      <p className="mb-3 text-sm font-semibold text-slate-700">
        {SIDEBAR_HEADING}
      </p>

      {reports.length === 0 ? (
        <p className="text-sm text-slate-400">{EMPTY_STATE_MESSAGE}</p>
      ) : (
        <ul className="space-y-1">
          {reports.map((report) => (
            <li key={report.id}>
              <button
                type="button"
                className={`w-full rounded px-2 py-1.5 text-left text-sm ${
                  selectedReportId === report.id
                    ? "bg-blue-100 text-blue-800"
                    : "text-slate-600 hover:bg-slate-200"
                }`}
                onClick={() => onSelectReport(report.id)}
              >
                <span className="block truncate font-medium">
                  {report.query}
                </span>
                <span className="block text-xs text-slate-400">
                  {report.timestamp}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
