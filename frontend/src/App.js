import React, { useState } from "react";
import axios from "axios";

function App() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");
  const [results, setResults] = useState([]);

  const addJob = async () => {
    try {
      await axios.post("http://127.0.0.1:8000/job", {
        title,
        description
      });
      setMsg("Job Added Successfully");
    } catch {
      setMsg("Error adding job");
    }
  };

  const uploadResume = async () => {
    if (!file) {
      setMsg("Select file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(
        "http://127.0.0.1:8000/upload_resume",
        formData
      );
      setMsg("Resume Uploaded Successfully");
    } catch {
      setMsg("Upload Failed");
    }
  };

  const getMatches = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/match/1");

      if (res.data.rankings) {
        setResults(res.data.rankings);
      } else {
        setResults(res.data);
      }

      setMsg("Matching Complete");
    } catch {
      setMsg("Matching Failed");
    }
  };

  return (
    <div style={page}>
      <h1 style={heading}>ResumeX AI</h1>
      <p style={sub}>
        Smart Resume Screening & Job Matching System
      </p>

      <div style={grid}>
        {/* Add Job */}
        <div style={card}>
          <h2>Add Job</h2>

          <input
            placeholder="Job Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={input}
          />

          <textarea
            placeholder="Job Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={textarea}
          />

          <button style={btn} onClick={addJob}>
            Add Job
          </button>
        </div>

        {/* Upload Resume */}
        <div style={card}>
          <h2>Upload Resume</h2>

          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <br /><br />

          <button style={btn} onClick={uploadResume}>
            Upload Resume
          </button>
        </div>

        {/* Results */}
        <div style={card}>
          <h2>AI Match Results</h2>

          <button style={btn} onClick={getMatches}>
            View Results
          </button>

          <div style={{ marginTop: "20px" }}>
            {results.map((item, index) => (
              <div key={index} style={resultBox}>
                {item.resume || item.name}
                <br />
                <strong>{item.score}% Match</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p style={msgStyle}>{msg}</p>
    </div>
  );
}

/* Styles */

const page = {
  minHeight: "100vh",
  background: "linear-gradient(135deg,#0f172a,#1e293b,#334155)",
  padding: "30px",
  color: "white",
  fontFamily: "Arial"
};

const heading = {
  textAlign: "center",
  fontSize: "42px",
  marginBottom: "5px"
};

const sub = {
  textAlign: "center",
  color: "#cbd5e1",
  marginBottom: "30px"
};

const grid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit,minmax(320px,1fr))",
  gap: "20px"
};

const card = {
  background: "rgba(255,255,255,0.08)",
  padding: "25px",
  borderRadius: "16px",
  boxShadow: "0 8px 25px rgba(0,0,0,0.3)"
};

const input = {
  width: "100%",
  padding: "12px",
  marginBottom: "12px",
  borderRadius: "10px",
  border: "none"
};

const textarea = {
  width: "100%",
  height: "120px",
  padding: "12px",
  marginBottom: "12px",
  borderRadius: "10px",
  border: "none"
};

const btn = {
  background: "#38bdf8",
  color: "white",
  border: "none",
  padding: "12px 18px",
  borderRadius: "10px",
  cursor: "pointer",
  fontWeight: "bold"
};

const resultBox = {
  background: "#1e293b",
  padding: "12px",
  borderRadius: "10px",
  marginBottom: "10px"
};

const msgStyle = {
  textAlign: "center",
  marginTop: "30px",
  color: "#22c55e",
  fontWeight: "bold"
};

export default App;