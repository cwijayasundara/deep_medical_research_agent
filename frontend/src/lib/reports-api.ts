/** Reports API client for fetching saved research reports. */

import { API_BASE_URL } from "./api-client.ts";

const REPORTS_ENDPOINT = "/reports";

export interface ReportSummary {
  id: string;
  query: string;
  timestamp: string;
}

export interface ReportDetail {
  id: string;
  query: string;
  timestamp: string;
  content: string;
  models_used: string[] | null;
}

export async function fetchReports(): Promise<ReportSummary[]> {
  try {
    const response = await fetch(`${API_BASE_URL}${REPORTS_ENDPOINT}`);
    if (!response.ok) {
      return [];
    }
    return (await response.json()) as ReportSummary[];
  } catch {
    return [];
  }
}

export async function fetchReportById(
  reportId: string,
): Promise<ReportDetail | null> {
  try {
    const response = await fetch(
      `${API_BASE_URL}${REPORTS_ENDPOINT}/${reportId}`,
    );
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as ReportDetail;
  } catch {
    return null;
  }
}
