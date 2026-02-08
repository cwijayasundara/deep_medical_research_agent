import { HealthIndicator } from "./components/HealthIndicator.tsx";
import { Layout } from "./components/Layout.tsx";

export default function App() {
  return (
    <Layout>
      <div className="space-y-4">
        <HealthIndicator />
        <p className="text-slate-600">
          Enter a medical research query to get started.
        </p>
      </div>
    </Layout>
  );
}
