/** Backend health status indicator. */
import { useEffect, useState } from "react";
import { fetchHealth } from "../lib/api-client.ts";

export function HealthIndicator() {
  const [connected, setConnected] = useState<boolean | null>(null);

  useEffect(() => {
    fetchHealth().then((result) => {
      setConnected(result !== null);
    });
  }, []);

  if (connected === null) {
    return (
      <div data-testid="health-indicator" className="flex items-center gap-2">
        <span data-testid="health-dot" className="w-2 h-2 rounded-full bg-gray-400" />
        <span className="text-sm text-gray-500">Checking...</span>
      </div>
    );
  }

  return (
    <div data-testid="health-indicator" className="flex items-center gap-2">
      <span
        data-testid="health-dot"
        className={`w-2 h-2 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`}
      />
      <span className={`text-sm ${connected ? "text-green-700" : "text-red-700"}`}>
        {connected ? "Connected" : "Disconnected"}
      </span>
    </div>
  );
}
