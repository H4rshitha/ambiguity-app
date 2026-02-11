import { useState,useEffect } from "react";
import API from "../api";

export default function Analyzer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hoveredWord, setHoveredWord] = useState(null);
  const [history, setHistory] = useState([]);
  useEffect(() => {
    fetchHistory();
    }, []);


  const analyzeText = async () => {
    try {
      setLoading(true);

      const res = await API.post("/analyze", {
        text: text
      });

      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error analyzing text");
    } finally {
      setLoading(false);
    }
  };

  const renderHighlightedText = () => {
    if (!result) return text;

    const words = text.split(" ");

    return words.map((word, i) => {
        const match = result.ambiguous.find(a => a.index === i);

        if (match) {
        return (
            <span
            key={i}
            onMouseEnter={() => setHoveredWord(match)}
            onMouseLeave={() => setHoveredWord(null)}
            style={{
                backgroundColor: "#ffe066",
                padding: "2px 4px",
                borderRadius: "4px",
                marginRight: 4,
                cursor: "pointer",
                position: "relative"
            }}
            >
            {word}
            </span>
        );
        }

        return <span key={i}>{word} </span>;
    });
    };

    const fetchHistory = async () => {
        try {
            const res = await API.get("/history");
            setHistory(res.data);
        } catch (err) {
            console.error("History fetch failed", err);
        }
        };


  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-10">

      <h1 className="text-4xl font-bold mb-8 tracking-tight">
        Ambiguity Analyzer
    </h1>


      <textarea
        className="
            w-full 
            bg-gray-900 
            border border-gray-800 
            rounded-xl 
            p-4 
            mb-6 
            focus:outline-none 
            focus:ring-2 
            focus:ring-blue-500
            transition
        "
        rows={6}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text..."
       />

    <button
        onClick={analyzeText}
        disabled={loading}
        className="
            bg-blue-600 
            hover:bg-blue-700 
            px-6 
            py-3 
            rounded-xl 
            font-semibold 
            transition 
            shadow-lg
            disabled:opacity-50
        "
        >
        {loading ? "Analyzing..." : "Analyze"}
    </button>

    {history.length > 0 && (
        <div className="mt-10">
            <h3 className="text-xl font-semibold mb-4">Recent Analyses</h3>

            <div className="grid md:grid-cols-2 gap-4">
            {history.map((item, i) => (
                <div
                key={i}
                onClick={() => {
                    setText(item.text);
                    setResult(item);
                }}
                className="
                    bg-gray-900
                    border border-gray-800
                    rounded-xl
                    p-4
                    cursor-pointer
                    hover:border-blue-500
                    hover:bg-gray-800
                    transition
                "
                >
                <p className="text-sm text-gray-400 mb-2 truncate">
                    {item.text}
                </p>

                <p className="text-xs text-gray-500">
                    Score: {item.ambiguity_score}
                </p>
                </div>
            ))}
            </div>
        </div>
        )}



    {result && (
        <div className="mt-10 bg-gray-900 border border-gray-800 p-6 rounded-2xl shadow-xl">
          <div className="mb-8 p-6 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 shadow-xl">
            <p className="text-sm text-blue-100 mb-1">Sentence Ambiguity Score</p>
            <p className="text-4xl font-bold">{result.ambiguity_score}</p>
          </div>

          {/* ⭐ HIGHLIGHTED TEXT BLOCK — PUT HERE */}
            <div className="mb-10">
                <h3 className="text-xl font-semibold mb-3">Highlighted Text</h3>

                <div className="
                    bg-gray-950
                    border border-gray-800
                    rounded-xl
                    p-5
                    leading-8
                ">
                    {renderHighlightedText()}
                </div>
                </div>
          <div>
            <h3 className="text-xl font-semibold mb-4">Ambiguous Words</h3>

            <div className="grid md:grid-cols-2 gap-4">
                {result.ambiguous.map((item, i) => (
                <div
                    key={i}
                    className="
                    bg-gray-950
                    border border-gray-800
                    rounded-xl
                    p-4
                    hover:border-blue-500
                    transition
                    "
                >
                    <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold text-lg">{item.word}</span>

                    <span className="
                        text-xs
                        px-2 py-1
                        rounded-full
                        bg-blue-900
                        text-blue-200
                    ">
                        {item.confidence}
                    </span>
                    </div>

                    <p className="text-gray-300 text-sm mb-2">
                    {item.best_sense}
                    </p>

                    <p className="text-xs text-gray-500">
                    Source: {item.decision_source}
                    </p>
                </div>
                ))}
            </div>
            </div>
        </div>
      )}

      {hoveredWord && (
        <div
            style={{
                position: "fixed",
                bottom: 40,
                right: 40,
                width: 320,
                background: "white",
                color: "#111",   // ⭐ ADD THIS
                border: "1px solid #ddd",
                borderRadius: 12,
                padding: 20,
                boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
                zIndex: 1000,
                wordBreak: "break-word",
                whiteSpace: "normal",
                overflowWrap: "break-word"
            }}
        >
            <h4 style={{ marginTop: 0, marginBottom: 10 }}>
            {hoveredWord.word}
            </h4>

            <p style={{ marginBottom: 8 }}>
            <b>Meaning:</b><br />
            {hoveredWord.best_sense}
            </p>

            <p style={{ marginBottom: 6 }}>
            <b>Confidence:</b> {hoveredWord.confidence}
            </p>

            <p style={{ marginBottom: 6 }}>
            <b>Source:</b> {hoveredWord.decision_source}
            </p>

            {hoveredWord.fallback_similarity && (
            <p>
                <b>Similarity:</b> {hoveredWord.fallback_similarity}
            </p>
            )}
            </div>
        )}

    </div>
    );
}
