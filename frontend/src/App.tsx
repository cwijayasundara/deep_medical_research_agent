import { HealthIndicator } from "./components/HealthIndicator.tsx";
import { Layout } from "./components/Layout.tsx";
import { ProgressLog } from "./components/ProgressLog.tsx";
import { ReportViewer } from "./components/ReportViewer.tsx";
import { ResearchInput } from "./components/ResearchInput.tsx";
import { useResearch } from "./hooks/useResearch.ts";

export default function App() {
  const { isLoading, progressMessages, report, error, startResearch, stopResearch } =
    useResearch();

  return (
    <Layout>
      <div className="space-y-4">
        <HealthIndicator />
        <ResearchInput
          onSubmit={startResearch}
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

        {report && (
          <ReportViewer content={report.content} filename={report.filename} />
        )}
      </div>
    </Layout>
  );
}
