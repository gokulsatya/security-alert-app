import { useState, useEffect } from "react";

// The address of your backend. Kept in one place so it's easy to change later.
const API_URL = "http://127.0.0.1:8000";

// ---- Reusable styles for the summary cards ----
const cardStyle = {
  flex: 1,
  padding: "1.25rem",
  borderRadius: "8px",
  background: "#1e1e2e",
  border: "1px solid #333",
  textAlign: "center",
};
const cardNumber = { fontSize: "2rem", fontWeight: "bold" };
const cardLabel = { fontSize: "0.9rem", opacity: 0.8, marginTop: "0.25rem" };

function App() {
  // ---- State: the component's memory ----
  // `alerts` holds the list we get from the backend (starts as an empty array).
  // `setAlerts` is the function we call to update it.
  const [alerts, setAlerts] = useState([]);

  // ---- Filter state ----
  const [severityFilter, setSeverityFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [search, setSearch] = useState("");

  // `loading` lets us show "Loading..." until the data arrives.
  const [loading, setLoading] = useState(true);

  // `error` holds an error message if the fetch fails.
  const [error, setError] = useState(null);

  // ---- Effect: run once when the page first loads ----
  useEffect(() => {
    // Go ask the backend for all alerts.
    fetch(`${API_URL}/alerts`)
      .then((response) => {
        if (!response.ok) {
          // e.g. a 404 or 500 from the server
          throw new Error(`Server responded with ${response.status}`);
        }
        return response.json(); // turn the response into a JS array
      })
      .then((data) => {
        setAlerts(data);     // save the alerts into state
        setLoading(false);   // we're done loading
      })
      .catch((err) => {
        // e.g. backend not running, or CORS blocked it
        setError(err.message);
        setLoading(false);
      });
  }, []); // the empty [] means "run this only once, on first load"

  // ---- What to show on screen ----

  if (loading) {
    return <p style={{ padding: "2rem" }}>Loading alerts...</p>;
  }

  if (error) {
    return (
      <p style={{ padding: "2rem", color: "red" }}>
        Could not load alerts: {error}
      </p>
    );
  }
  
  // ---- Apply the filters to produce the list we actually display ----
  const visibleAlerts = alerts.filter((alert) => {
    // Severity: keep if "All" is selected, or it matches exactly.
    const matchesSeverity =
      severityFilter === "All" || alert.severity === severityFilter;

    // Status: same idea.
    const matchesStatus =
      statusFilter === "All" || alert.status === statusFilter;

    // Search: case-insensitive match against title OR source.
    const text = search.toLowerCase();
    const matchesSearch =
      alert.title.toLowerCase().includes(text) ||
      alert.source.toLowerCase().includes(text);

    // Keep the alert only if it passes all three.
    return matchesSeverity && matchesStatus && matchesSearch;
  });

    // ---- Count alerts for the summary cards ----
  const totalCount = alerts.length;
  const openCount = alerts.filter((a) => a.status === "Open").length;
  const criticalCount = alerts.filter((a) => a.severity === "Critical").length;
  const closedCount = alerts.filter((a) => a.status === "Closed").length;

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Security Alert Dashboard</h1>
      <p>Showing {visibleAlerts.length} of {alerts.length} alerts.</p>

      {/* ---- Summary cards ---- */}
      <div style={{ display: "flex", gap: "1rem", margin: "1.5rem 0" }}>
        <div style={cardStyle}>
          <div style={cardNumber}>{totalCount}</div>
          <div style={cardLabel}>Total Alerts</div>
        </div>
        <div style={cardStyle}>
          <div style={cardNumber}>{openCount}</div>
          <div style={cardLabel}>Open</div>
        </div>
        <div style={cardStyle}>
          <div style={{ ...cardNumber, color: "#d32f2f" }}>{criticalCount}</div>
          <div style={cardLabel}>Critical</div>
        </div>
        <div style={cardStyle}>
          <div style={cardNumber}>{closedCount}</div>
          <div style={cardLabel}>Closed</div>
        </div>
      </div>
      
      {/* ---- Filter controls ---- */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", alignItems: "center" }}>
        <label>
          Severity:{" "}
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option>All</option>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Critical</option>
          </select>
        </label>

        <label>
          Status:{" "}
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option>All</option>
            <option>Open</option>
            <option>In Progress</option>
            <option>Closed</option>
          </select>
        </label>

        <input
          type="text"
          placeholder="Search by title or source..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: "0.4rem", flex: 1 }}
        />
      </div>

      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Source</th>
            <th>Created Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {/* Loop over each alert and draw one table row per alert */}
          {visibleAlerts.map((alert) => (
            <tr key={alert.id}>
              <td>{alert.id}</td>
              <td>{alert.title}</td>
              <td>{alert.severity}</td>
              <td>{alert.status}</td>
              <td>{alert.source}</td>
              <td>{new Date(alert.created_at).toLocaleDateString()}</td>
              <td>
                <button>View</button>{" "}
                <button>Edit</button>{" "}
                <button>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;