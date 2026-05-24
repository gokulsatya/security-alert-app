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

  // ---- Create-form state ----
  // showForm toggles the "Add New Alert" form on and off.
  const [showForm, setShowForm] = useState(false);

  // One piece of state per input. The dropdowns start on sensible defaults
  // so the form is never half-empty when submitted.
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newSeverity, setNewSeverity] = useState("Low");
  const [newStatus, setNewStatus] = useState("Open");
  const [newSource, setNewSource] = useState("SIEM");

  // ---- View-details state ----
  // Holds the ONE alert the user clicked "View" on.
  // null = no alert selected = popup hidden.
  // When it holds an alert object, the popup shows.
  const [viewingAlert, setViewingAlert] = useState(null);
  
  // ---- Edit state ----
  // Holds the id of the alert being edited.
  // null = we're CREATING a new alert; a number = we're EDITING that alert.
  const [editingId, setEditingId] = useState(null);

  // ---- Action-error state ----
  // Holds a friendly message when a create/update/delete/close fails.
  // null = no error = banner hidden.
  const [actionError, setActionError] = useState(null);

  // ---- Reusable function to fetch all alerts from the backend ----
  // We pull this out of useEffect so we can also call it AFTER a delete,
  // create, or edit — to refresh the table with the latest data.
  const loadAlerts = () => {
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
  };

  // ---- Effect: run loadAlerts once when the page first loads ----
  useEffect(() => {
    loadAlerts();
  }, []); // the empty [] means "run this only once, on first load"

  // ---- Delete an alert by its id ----
  const handleDelete = (id) => {
    // 1. Confirm first — deleting is permanent.
    //    window.confirm shows a browser OK/Cancel popup.
    //    It returns true if the user clicks OK, false if Cancel.
    const confirmed = window.confirm("Are you sure you want to delete this alert?");
    if (!confirmed) {
      return; // user clicked Cancel — stop here, do nothing
    }

    // 2. Send a DELETE request to the backend.
    //    Unlike a plain fetch (which defaults to GET), we pass a second
    //    argument telling fetch the method is "DELETE".
    fetch(`${API_URL}/alerts/${id}`, {
      method: "DELETE",
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Could not delete (server said ${response.status})`);
        }
        // 3. Success — refresh the table so the deleted row disappears
        //    and the summary cards recount.
        loadAlerts();
        setActionError(null); // clear any previous error on success
      })
      .catch((err) => {
        setActionError(`Delete failed: ${err.message}`);
      });
  };
  
  // ---- Create a new alert ----
  const handleCreate = () => {
    // Bundle the form values into one object — this becomes the request body.
    const newAlert = {
      title: newTitle,
      description: newDescription,
      severity: newSeverity,
      status: newStatus,
      source: newSource,
    };

    // POST request: like DELETE, but now we also SEND data.
    fetch(`${API_URL}/alerts`, {
      method: "POST",
      // Tell the server we're sending JSON.
      headers: { "Content-Type": "application/json" },
      // Convert our JS object into a JSON string for the request body.
      body: JSON.stringify(newAlert),
    })
      .then((response) => {
        if (!response.ok) {
          // 422 means the backend's validation rejected our data.
          throw new Error(`Could not create (server said ${response.status})`);
        }
        return response.json(); // the newly created alert comes back
      })
      .then(() => {
        // Success! Refresh the table so the new alert appears.
        loadAlerts();
        setActionError(null); // clear any previous error on success

        // Clear the form's text boxes and hide the form.
        setNewTitle("");
        setNewDescription("");
        setShowForm(false);
      })
      .catch((err) => {
        setActionError(`Create failed: ${err.message}`);
      });
  };

  // ---- Begin editing: load an alert's values into the form ----
  const handleEdit = (alert) => {
    // Copy this alert's current values into the form fields.
    setNewTitle(alert.title);
    setNewDescription(alert.description);
    setNewSeverity(alert.severity);
    setNewStatus(alert.status);
    setNewSource(alert.source);

    // Remember WHICH alert we're editing, and open the form.
    setEditingId(alert.id);
    setShowForm(true);
  };

  // ---- Save an edit: send the updated values to the backend ----
  const handleUpdate = () => {
    const updatedAlert = {
      title: newTitle,
      description: newDescription,
      severity: newSeverity,
      status: newStatus,
      source: newSource,
    };

    // PUT request: like POST, but it UPDATES an existing alert.
    // Note the id in the URL — that's which alert to update.
    fetch(`${API_URL}/alerts/${editingId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedAlert),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Could not update (server said ${response.status})`);
        }
        return response.json();
      })
      .then(() => {
        loadAlerts();          // refresh the table
        setActionError(null);  // clear any previous error on success
        setNewTitle("");       // clear the form
        setNewDescription("");
        setEditingId(null);    // back to "create" mode
        setShowForm(false);    // hide the form
      })
      .catch((err) => {
        setActionError(`Update failed: ${err.message}`);
      });
  };

  // ---- Close an alert: a one-click shortcut that sets status to "Closed" ----
  const handleClose = (alert) => {
    // Send back all the same fields, but with status forced to "Closed".
    const closedAlert = {
      title: alert.title,
      description: alert.description,
      severity: alert.severity,
      status: "Closed",
      source: alert.source,
    };

    fetch(`${API_URL}/alerts/${alert.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(closedAlert),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Could not close (server said ${response.status})`);
        }
        return response.json();
      })
      .then(() => {
        loadAlerts(); // refresh so the status change shows
        setActionError(null); // clear any previous error on success
      })
      .catch((err) => {
        setActionError(`Close failed: ${err.message}`);
      });
  };

  // ---- Open a CLEAN create form (clears any leftover edit values) ----
  const handleOpenCreateForm = () => {
    // Reset every form field back to its default.
    setNewTitle("");
    setNewDescription("");
    setNewSeverity("Low");
    setNewStatus("Open");
    setNewSource("SIEM");

    // Make sure we're in CREATE mode, not edit mode.
    setEditingId(null);

    // Show the form.
    setShowForm(true);
  };

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

      {/* ---- Error banner: only shows when an action fails ---- */}
      {actionError && (
        <div style={{
          background: "#3a1212",
          border: "1px solid #d32f2f",
          color: "#ff8a80",
          padding: "0.75rem 1rem",
          borderRadius: "6px",
          marginBottom: "1rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)}>Dismiss</button>
        </div>
      )}

      {/* ---- Toggle button: show or hide the Create form ---- */}
      <button
        onClick={() => (showForm ? setShowForm(false) : handleOpenCreateForm())}
        style={{ marginBottom: "1rem" }}
      >
        {showForm ? "Cancel" : "+ Add New Alert"}
      </button>

      {/* ---- Export CSV button (standalone link styled as a button) ---- */}
      <a
        href={`${API_URL}/alerts/export`}
        style={{
          display: "inline-block",
          marginBottom: "1rem",
          marginLeft: "0.5rem",
          padding: "0.4rem 0.8rem",
          background: "#1e1e2e",
          border: "1px solid #333",
          borderRadius: "4px",
          color: "inherit",
          textDecoration: "none",
          fontSize: "0.9rem",
        }}
      >
        Export CSV
      </a>

      {/* ---- The Create form (only shown when showForm is true) ---- */}
      {showForm && (
        <div style={{ border: "1px solid #333", borderRadius: "8px", padding: "1rem", marginBottom: "1.5rem", maxWidth: "500px" }}>
          <h3>{editingId ? "Edit Alert" : "New Alert"}</h3>

          <div style={{ marginBottom: "0.5rem" }}>
            <input
              type="text"
              placeholder="Title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              style={{ width: "100%", padding: "0.4rem" }}
            />
          </div>

          <div style={{ marginBottom: "0.5rem" }}>
            <textarea
              placeholder="Description (at least 10 characters)"
              value={newDescription}
              onChange={(e) => setNewDescription(e.target.value)}
              style={{ width: "100%", padding: "0.4rem", minHeight: "60px" }}
            />
          </div>

          <div style={{ marginBottom: "0.5rem" }}>
            Severity:{" "}
            <select value={newSeverity} onChange={(e) => setNewSeverity(e.target.value)}>
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
              <option>Critical</option>
            </select>
          </div>

          <div style={{ marginBottom: "0.5rem" }}>
            Status:{" "}
            <select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
              <option>Open</option>
              <option>In Progress</option>
              <option>Closed</option>
            </select>
          </div>

          <div style={{ marginBottom: "0.75rem" }}>
            Source:{" "}
            <select value={newSource} onChange={(e) => setNewSource(e.target.value)}>
              <option>Email</option>
              <option>Endpoint</option>
              <option>Firewall</option>
              <option>Cloud</option>
              <option>SIEM</option>
            </select>
          </div>

          <button onClick={editingId ? handleUpdate : handleCreate}>
            {editingId ? "Update Alert" : "Save Alert"}
          </button>
        </div>
      )}

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
                <button onClick={() => setViewingAlert(alert)}>View</button>{" "}
                <button onClick={() => handleEdit(alert)}>Edit</button>{" "}
                <button onClick={() => handleClose(alert)}>Close</button>{" "}
                <button onClick={() => handleDelete(alert.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* ---- View-details popup (only shows when an alert is selected) ---- */}
      {viewingAlert && (
        <div style={{ border: "1px solid #333", borderRadius: "8px", padding: "1.5rem", marginTop: "1.5rem", maxWidth: "500px", background: "#1e1e2e" }}>
          <h3>Alert Details</h3>
          <p><strong>ID:</strong> {viewingAlert.id}</p>
          <p><strong>Title:</strong> {viewingAlert.title}</p>
          <p><strong>Description:</strong> {viewingAlert.description}</p>
          <p><strong>Severity:</strong> {viewingAlert.severity}</p>
          <p><strong>Status:</strong> {viewingAlert.status}</p>
          <p><strong>Source:</strong> {viewingAlert.source}</p>
          <p><strong>Created:</strong> {new Date(viewingAlert.created_at).toLocaleString()}</p>
          <p><strong>Last Updated:</strong> {new Date(viewingAlert.updated_at).toLocaleString()}</p>
          <button onClick={() => setViewingAlert(null)}>Close</button>
        </div>
      )}
    </div>
  );
}

export default App;