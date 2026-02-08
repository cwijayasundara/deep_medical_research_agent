/** Hook for managing research history state. */

import { useCallback, useEffect, useState } from "react";
import {
  fetchReportById,
  fetchReports,
} from "../lib/reports-api.ts";
import type { ReportDetail, ReportSummary } from "../lib/reports-api.ts";

export function useReportHistory() {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<ReportDetail | null>(
    null,
  );

  useEffect(() => {
    let cancelled = false;

    async function loadReports() {
      setIsLoadingHistory(true);
      const data = await fetchReports();
      if (!cancelled) {
        setReports(data);
        setIsLoadingHistory(false);
      }
    }

    loadReports();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectReport = useCallback(async (reportId: string) => {
    setSelectedReportId(reportId);
    const detail = await fetchReportById(reportId);
    setSelectedReport(detail);
  }, []);

  const addReport = useCallback((report: ReportSummary) => {
    setReports((prev) => [report, ...prev]);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedReportId(null);
    setSelectedReport(null);
  }, []);

  const refreshReports = useCallback(async () => {
    const data = await fetchReports();
    setReports(data);
  }, []);

  return {
    reports,
    isLoadingHistory,
    selectedReportId,
    selectedReport,
    selectReport,
    addReport,
    clearSelection,
    refreshReports,
  };
}
