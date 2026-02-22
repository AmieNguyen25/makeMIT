import { useState } from "react";
import "./TTS.css";

function TTS() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const speak = async () => {
    if (!text) return;

    setLoading(true);

    const res = await fetch("http://127.0.0.1:5000/tts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    const data = await res.json();

    const audio = new Audio("data:audio/mp3;base64," + data.audio);
    audio.play();

    setLoading(false);
  };

  return (
    <div className="tts-container">
      <h2>ElevenLabs Voice Test</h2>

      <input
        type="text"
        placeholder="Type something..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button onClick={speak} disabled={loading}>
        {loading ? "Speaking..." : "Speak"}
      </button>
    </div>
  );
}

export default TTS;