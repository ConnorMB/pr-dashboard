import { useState } from "react";
import { parseRepoInput } from "./parseRepoInput";

// the form totype in repo and hit submit
export default function RepoInput({ onSubmit, disabled }) {
  const [value, setValue] = useState("");
  const [error, setError] = useState(null);

  // parses whatever typed, shows an error inline if doesn't look like a repo
  function handleSubmit(event) {
    event.preventDefault();
    const parsed = parseRepoInput(value);
    if (!parsed) {
      setError("Enter a GitHub URL or owner/repo, e.g. facebook/react");
      return;
    }
    setError(null);
    onSubmit(parsed);
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "1.5rem" }}>
      <input
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="owner/repo or https://github.com/owner/repo"
        disabled={disabled}
        style={{ width: "320px", marginRight: "0.5rem" }}
      />
      <button type="submit" disabled={disabled}>
        Load repo
      </button>
      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}
    </form>
  );
}