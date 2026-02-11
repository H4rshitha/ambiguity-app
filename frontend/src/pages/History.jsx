import { useEffect, useState } from "react";
import API from "../api";

export default function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await API.get("/history");
      setHistory(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: 40 }}>
      <h1>Analysis History</h1>

      {history.map((item, i) => (
        <div
          key={i}
          style={{
            border: "1px solid #ccc",
            padding: 15,
            marginBottom: 15
          }}
        >
          <b>Text:</b> {item.text}
          <br />
          <b>Score:</b> {item.ambiguity_score}
          <br />
          <b>Date:</b> {new Date(item.created_at).toLocaleString()}
        </div>
      ))}
    </div>
  );
}
