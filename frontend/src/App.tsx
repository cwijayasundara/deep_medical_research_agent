import { HealthIndicator } from "./components/HealthIndicator.tsx";
import { HistorySidebar } from "./components/HistorySidebar.tsx";
import { Layout } from "./components/Layout.tsx";
import { ProgressLog } from "./components/ProgressLog.tsx";
import { ReportViewer } from "./components/ReportViewer.tsx";
import { ResearchInput } from "./components/ResearchInput.tsx";
import { useReportHistory } from "./hooks/useReportHistory.ts";
import { useResearch } from "./hooks/useResearch.ts";

export default function App() {
  const { isLoading, progressMessages, report, error, startResearch, stopResearch } =
    useResearch();

  const {
    reports,
    selectedReportId,
    selectedReport,
    selectReport,
    addReport,
    clearSelection,
  } = useReportHistory();

  const handleStartResearch = async (query: string) => {
    clearSelection();
    await startResearch(query);
  };

  const displayedReport = selectedReport ?? report;
  const displayedFilename = selectedReport
    ? `${selectedReport.id}.md`
    : report?.filename ?? "";

  return (
    <Layout
      sidebar={
        <HistorySidebar
          reports={reports}
          onSelectReport={selectReport}
          selectedReportId={selectedReportId}
        />
      }
    >
      <div className="space-y-4">
        <HealthIndicator />
        <ResearchInput
          onSubmit={handleStartResearch}
          onStop={stopResearch}
          isLoading={isLoading}
        />

        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {(isLoading || progressMessages.length > 0) && !report && (
          <ProgressLog messages={progressMessages} isActive={isLoading} />
        )}

        {displayedReport && (
          <ReportViewer
            content={displayedReport.content}
            filename={displayedFilename}
          />
        )}
      </div>
    </Layout>
  );
}
