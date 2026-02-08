/** Main application layout with header, sidebar, and content area. */
import type { ReactNode } from "react";

const APP_TITLE = "Deep Medical Research Agent";

interface LayoutProps {
  children?: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-slate-800 text-white px-6 py-4">
        <h1 className="text-xl font-bold">{APP_TITLE}</h1>
      </header>

      <div className="flex flex-1">
        <aside className="w-64 bg-slate-100 p-4 border-r border-slate-200">
          <p className="text-sm text-slate-500">Research History</p>
        </aside>

        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
