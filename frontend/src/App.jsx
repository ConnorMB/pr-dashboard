import { use, useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getMetric, createOrSyncRepo, getRepoStatus } from "./api";
import RepoInput from "./repoInput";

const POLL_INTERVAL = 2000;
const MAX_POLL_ATTEMPTS = 30;

//bar chart reused for all metrics
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

// left to right order
function sortByPrNumber(data) {
  return [...data].sort((a, b) => a.pr_number - b.pr_number);
}

// actual page 
export default function App() {
  const [repo,setRepo] = useState(null);
  const [repoStatus, setRepoStatus] = useState(null);
  const [error, setError] = useState(null);
  const [timeToMerge, setTimeToMerge] = useState([]);
  const [reviewTurnaround, setReviewTurnaround] = useState([]);
  const [prSize, setPrSize] = useState([]);
  const pollAttempts = useState(0);

  async function loadMetrics(repoId) {
    setTimeToMerge(sortByPrNumber(await getMetric("/metrics/time-to-merge", repoId)));
    setReviewTurnaround(sortByPrNumber(await getMetric("/metrics/review-turnaround", repoId)));
    setPrSize(sortByPrNumber(await getMetric("/metrics/pr-size", repoId)));
  }

  // polling loop, checks repo status until ready/error/timeout
  useEffect(() => {
    if (!repo || repoStatus === "ready" || repoStatus === "error") return;
    const timer = setInterval(async () => {
      pollAttempts.current += 1;
      if (pollAttempts.current > MAX_POLL_ATTEMPTS) {
        setError("this repo took too long to load, try again later");
        setRepoStatus("error");
        return;
      }
      const current = await getRepoStatus(repo.id);
      setRepoStatus(current.status);
      if (current.status === "error") {
        setError(current.error_message || "couldn't load repo");
      }
    }, POLL_INTERVAL);

    return () => clearInterval(timer);
  }, [repo, repoStatus]);

  // once status ready, fetch actual chart data
  useEffect(() => {
    if (repoStatus === "ready" && repo) {
      loadMetrics(repo.id);
    }
  }, [repo, repoStatus]);

  // runs when repo input is submitted, starts sync
  async function handleRepoSubmit({ owner, name }) {
    setError(null);
    setRepoStatus(null);
    pollAttempts.current = 0;
    try {
      const created = await createOrSyncRepo(owner, name);
      setRepo(created);
      setRepoStatus(created.status);
    } catch (err) {
      setError(err.message);
    }
  }

  const isLoading = repoStatus === "pending" || repoStatus === "syncing";

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem" }}>
      <h1>PR Analytics Dashboard</h1>
      <RepoInput onSubmit={handleRepoSubmit} disabled={isLoading}  />
      
      {isLoading && repo && <p>Loading  {repo.owner}/{repo.name}...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {repoStatus === "ready" && repo && (
        <>
          <Chart title="Time to merge (hours)" data={timeToMerge} dataKey="hours" xKey="pr_number" />
          <Chart title="Review turnaround (hours)" data={reviewTurnaround} dataKey="hours" xKey="pr_number" />
          <Chart title="PR size (lines changed)" data={prSize} dataKey="lines_changed" xKey="pr_number" />
        </>
      )}
      
    </div>
  );
  

}
