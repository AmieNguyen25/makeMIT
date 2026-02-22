import { useEffect, useState } from "react"

export default function Eyes({ onNavigate }) {
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    const handleMouse = (e) => {
      const percent = e.clientX / window.innerWidth
      const newOffset = (percent - 0.5) * 70 // Increased range for more eye movement
      setOffset(newOffset)
    }

    window.addEventListener("mousemove", handleMouse)
    return () => window.removeEventListener("mousemove", handleMouse)
  }, [])

  const eyeSocketStyle = {
    width: "300px",
    height: "200px",
    background: "#1a202c",
    border: "8px solid #2d3748",
    borderRadius: "100px",
    position: "relative",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    margin: "0 50px",
    boxShadow: "inset 0 4px 8px rgba(0,0,0,0.5)"
  }

  const pixelEyeStyle = {
    width: "140px",
    height: "80px",
    background: "#00ff41",
    borderRadius: "40px",
    transform: `translateX(${offset}px)`,
    transition: "transform 0.15s ease-out",
    boxShadow: "inset 0 4px 8px rgba(0,255,65,0.3), 0 0 20px rgba(0,255,65,0.2)",
    border: "4px solid #00cc33"
  }



  return (
    <div style={{
      background: "linear-gradient(135deg, #28a745 0%, #20c997 100%)",
      width: "100vw",
      height: "100vh",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      fontFamily: "monospace"
    }}>
      {/* Eye Container */}
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
      }}>
        {/* Left Eye */}
        <div style={eyeSocketStyle}>
          <div style={pixelEyeStyle}></div>
        </div>

        {/* Right Eye */}
        <div style={eyeSocketStyle}>
          <div style={pixelEyeStyle}></div>
        </div>
      </div>

      {/* Navigation Button */}
      <button
        onClick={onNavigate}
        style={{
          position: "absolute",
          top: "30px",
          right: "30px",
          background: "#28a745",
          color: "white",
          border: "none",
          borderRadius: "12px",
          padding: "16px 32px",
          fontSize: "18px",
          fontWeight: "bold",
          cursor: "pointer",
          boxShadow: "0 4px 12px rgba(40, 167, 69, 0.3)",
          transition: "all 0.3s ease",
          zIndex: 1000
        }}
        onMouseOver={(e) => {
          e.target.style.background = "#218838"
          e.target.style.transform = "translateY(-2px)"
        }}
        onMouseOut={(e) => {
          e.target.style.background = "#28a745"
          e.target.style.transform = "translateY(0px)"
        }}
      >
        🗑️ Go to Trash Tracker
      </button>
    </div>
  )
}