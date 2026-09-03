import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getMetric } from "./api";

function Chart({ title, data, dataKey, xKey }) {
  return (
    <div style={{ marginBottom: "2rem" }}>
      <h2>{title}</h2>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xKey} />
          <YAxis />
          <Tooltip />
          <Bar dataKey={dataKey} fill="#4f46e5" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function sortByPrNumber(data) {
  return [...data].sort((a, b) => a.pr_number - b.pr_number);
}

export default function App() {
  const [timeToMerge, setTimeToMerge] = useState([]);
  const [reviewTurnaround, setReviewTurnaround] = useState([]);
  const [prSize, setPrSize] = useState([]);
  const [syncing, setSyncing] = useState(false);

  async function loadAll() {
    setTimeToMerge(sortByPrNumber(await getMetric("/metrics/time-to-merge")));
    setReviewTurnaround(sortByPrNumber(await getMetric("/metrics/review-turnaround")));
    setPrSize(sortByPrNumber(await getMetric("/metrics/pr-size")));
  }

  ```
  async function handleSync() {
    setSyncing(true);
    try {
      await triggerSync();
      await loadAll();
    } finally {
      setSyncing(false);
    }
  }
  ```

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem" }}>
      <h1>PR Analytics Dashboard</h1>
      <button onClick={handleSync} disabled={syncing}>
        {syncing ? "Syncing…" : "Sync now"}
      </button>
      <button onClick={loadAll} style={{ marginLeft: "1rem" }}>
        Refresh charts
      </button>

      <Chart title="Time to merge (hours)" data={timeToMerge} dataKey="hours" xKey="pr_number" />
      <Chart title="Review turnaround (hours)" data={reviewTurnaround} dataKey="hours" xKey="pr_number" />
      <Chart title="PR size (lines changed)" data={prSize} dataKey="lines_changed" xKey="pr_number" />
    </div>
  );
  

}
