import { useEffect, useState } from "react"

export default function TrashTracker({ onNavigate }) {
  const [counts, setCounts] = useState({
    paper: 0,
    cans: 0,
    plasticBottles: 0,
    trash: 0
  })

  const incrementCount = (type) => {
    setCounts(prev => ({
      ...prev,
      [type]: prev[type] + 1
    }))
  }

  const resetCounts = () => {
    setCounts({
      paper: 0,
      cans: 0,
      plasticBottles: 0,
      trash: 0
    })
  }

  const getCurrentDate = () => {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const cameraViewStyle = {
    width: "50%",
    height: "100vh",
    background: "#1a1a1a",
    border: "4px solid #333",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    position: "relative"
  }

  const trackingPanelStyle = {
    width: "50%",
    height: "100vh",
    background: "#f8f9fa",
    padding: "30px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-start",
    overflow: "auto"
  }

  const itemCardStyle = {
    background: "white",
    borderRadius: "12px",
    padding: "24px",
    margin: "12px 0",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    border: "1px solid #e9ecef",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center"
  }

  const buttonStyle = {
    background: "#28a745",
    color: "white",
    border: "none",
    borderRadius: "8px",
    padding: "12px 24px",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: "pointer",
    transition: "background 0.3s ease"
  }

  const countStyle = {
    fontSize: "48px",
    fontWeight: "bold",
    color: "#343a40",
    minWidth: "80px",
    textAlign: "center"
  }

  return (
    <div style={{
      display: "flex",
      width: "100vw",
      height: "100vh",
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    }}>
      {/* Camera View Section */}
      <div style={cameraViewStyle}>
        <div style={{
          width: "80%",
          height: "60%",
          background: "#2d2d2d",
          borderRadius: "12px",
          border: "3px dashed #666",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          position: "relative"
        }}>
          <div style={{
            fontSize: "64px",
            color: "#666",
            marginBottom: "20px"
          }}>📹</div>
          <div style={{
            color: "#aaa",
            fontSize: "18px",
            textAlign: "center"
          }}>
            <div>Camera View</div>
            <div style={{ fontSize: "14px", marginTop: "8px" }}>
              Live feed will appear here
            </div>
          </div>
        </div>
        
        <div style={{
          position: "absolute",
          bottom: "30px",
          color: "#666",
          fontSize: "14px"
        }}>
          Real-time Detection Active
        </div>
      </div>

      {/* Tracking Panel Section */}
      <div style={trackingPanelStyle}>
        <div style={{
          marginBottom: "30px",
          textAlign: "center",
          position: "relative"
        }}>
          <div style={{ 
            position: "absolute",
            top: "0",
            right: "0",
            display: "flex",
            gap: "10px"
          }}>
            <button
              onClick={() => onNavigate('thankyou')}
              style={{
                background: "#28a745",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 24px",
                fontSize: "16px",
                fontWeight: "bold",
                cursor: "pointer",
                transition: "background 0.3s ease"
              }}
              onMouseOver={(e) => e.target.style.background = "#218838"}
              onMouseOut={(e) => e.target.style.background = "#28a745"}
            >
              🎉 Thank You
            </button>
            <button
              onClick={() => onNavigate('eyes')}
              style={{
                background: "#007bff",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "12px 24px",
                fontSize: "16px",
                fontWeight: "bold",
                cursor: "pointer",
                transition: "background 0.3s ease"
              }}
              onMouseOver={(e) => e.target.style.background = "#0056b3"}
              onMouseOut={(e) => e.target.style.background = "#007bff"}
            >
              👁️ Back to Eyes
            </button>
          </div>
          <h1 style={{
            color: "#343a40",
            fontSize: "32px",
            marginBottom: "8px"
          }}>
            Waste Tracking Dashboard
          </h1>
          <p style={{
            color: "#6c757d",
            fontSize: "16px",
            margin: "0"
          }}>
            {getCurrentDate()}
          </p>
        </div>

        {/* Paper */}
        <div style={itemCardStyle}>
          <div>
            <div style={{ fontSize: "24px", marginBottom: "8px" }}>📄 Paper</div>
            <div style={{ color: "#6c757d", fontSize: "14px" }}>Recyclable paper items</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <div style={countStyle}>{counts.paper}</div>
            <button 
              style={buttonStyle}
              onClick={() => incrementCount('paper')}
              onMouseOver={(e) => e.target.style.background = "#218838"}
              onMouseOut={(e) => e.target.style.background = "#28a745"}
            >
              + Add
            </button>
          </div>
        </div>

        {/* Cans */}
        <div style={itemCardStyle}>
          <div>
            <div style={{ fontSize: "24px", marginBottom: "8px" }}>🥤 Cans</div>
            <div style={{ color: "#6c757d", fontSize: "14px" }}>Aluminum cans</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <div style={countStyle}>{counts.cans}</div>
            <button 
              style={buttonStyle}
              onClick={() => incrementCount('cans')}
              onMouseOver={(e) => e.target.style.background = "#218838"}
              onMouseOut={(e) => e.target.style.background = "#28a745"}
            >
              + Add
            </button>
          </div>
        </div>

        {/* Plastic Bottles */}
        <div style={itemCardStyle}>
          <div>
            <div style={{ fontSize: "24px", marginBottom: "8px" }}>🍶 Plastic Bottles</div>
            <div style={{ color: "#6c757d", fontSize: "14px" }}>Recyclable plastic containers</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <div style={countStyle}>{counts.plasticBottles}</div>
            <button 
              style={buttonStyle}
              onClick={() => incrementCount('plasticBottles')}
              onMouseOver={(e) => e.target.style.background = "#218838"}
              onMouseOut={(e) => e.target.style.background = "#28a745"}
            >
              + Add
            </button>
          </div>
        </div>

        {/* Trash */}
        <div style={itemCardStyle}>
          <div>
            <div style={{ fontSize: "24px", marginBottom: "8px" }}>🗑️ General Trash</div>
            <div style={{ color: "#6c757d", fontSize: "14px" }}>Non-recyclable waste</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
            <div style={countStyle}>{counts.trash}</div>
            <button 
              style={buttonStyle}
              onClick={() => incrementCount('trash')}
              onMouseOver={(e) => e.target.style.background = "#218838"}
              onMouseOut={(e) => e.target.style.background = "#28a745"}
            >
              + Add
            </button>
          </div>
        </div>

        {/* Summary and Reset */}
        <div style={{
          marginTop: "30px",
          padding: "24px",
          background: "#e9f7ef",
          borderRadius: "12px",
          border: "1px solid #28a745"
        }}>
          <h3 style={{ color: "#28a745", margin: "0 0 16px 0" }}>Today's Summary</h3>
          <div style={{ fontSize: "18px", color: "#343a40" }}>
            Total Items Processed: {counts.paper + counts.cans + counts.plasticBottles + counts.trash}
          </div>
          <div style={{ marginTop: "16px" }}>
            <button 
              style={{
                ...buttonStyle,
                background: "#dc3545"
              }}
              onClick={resetCounts}
              onMouseOver={(e) => e.target.style.background = "#c82333"}
              onMouseOut={(e) => e.target.style.background = "#dc3545"}
            >
              Reset All Counts
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}