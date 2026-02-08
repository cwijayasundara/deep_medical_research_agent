/** Report viewer that renders markdown content. */
import Markdown from "react-markdown";

interface ReportViewerProps {
  content: string | null;
  filename: string;
}

export function ReportViewer({ content, filename }: ReportViewerProps) {
  if (!content) {
    return null;
  }

  return (
    <article className="prose prose-slate max-w-none">
      <p className="text-xs text-slate-400">{filename}</p>
      <Markdown>{content}</Markdown>
    </article>
  );
}
