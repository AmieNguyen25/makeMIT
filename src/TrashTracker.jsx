import { useEffect, useState, useRef } from "react"

const CLASSIFICATION_API_URL = 'http://localhost:5000';

export default function TrashTracker({ onNavigate }) {
  const [counts, setCounts] = useState({
    paper: 0,
    cans: 0,
    plasticBottles: 0,
    trash: 0
  })

  const [cameraSystem, setCameraSystem] = useState({
    running: false,
    classifying: false,
    inCooldown: false,
    latestClassification: null,
    systemStatus: 'disconnected'
  })

  // Use ref to persist classification tracking across re-renders
  const lastProcessedRef = useRef(null)

  // Generate unique key for classification result
  const getClassificationKey = (classificationData) => {
    if (!classificationData) return null;

    // Debug: Log the classification data structure
    console.log('Classification data:', classificationData);

    // Use combination of classification + processing_time as unique identifier
    // Note: timestamp might not be available in the response
    const key = `${classificationData.classification}_${classificationData.processing_time}`;
    console.log('Generated key:', key);
    return key;
  };

  // Fetch camera system status
  const fetchCameraStatus = async () => {
    try {
      const response = await fetch(`${CLASSIFICATION_API_URL}/status`);
      if (response.ok) {
        const data = await response.json();
        setCameraSystem({
          running: data.running,
          classifying: data.classification_in_progress,
          inCooldown: data.in_cooldown,
          latestClassification: data.latest_classification,
          systemStatus: 'connected'
        });

        // Auto-increment counts based on NEW classification only
        if (data.latest_classification &&
          data.latest_classification.classification !== 'error') {

          const currentClassificationKey = getClassificationKey(data.latest_classification);

          console.log('Current key:', currentClassificationKey);
          console.log('Last processed key:', lastProcessedRef.current);
          console.log('Keys match?', currentClassificationKey === lastProcessedRef.current);

          // Only count if this is a truly new classification (different processing instance)
          if (currentClassificationKey && currentClassificationKey !== lastProcessedRef.current) {
            console.log('🟢 NEW CLASSIFICATION DETECTED - Incrementing count');

            const category = data.latest_classification.classification;
            if (category === 'can') incrementCount('cans');
            else if (category === 'plastic') incrementCount('plasticBottles');
            else if (category === 'paper') incrementCount('paper');
            else incrementCount('trash');

            // Mark this classification as processed using the ref
            lastProcessedRef.current = currentClassificationKey;
          } else {
            console.log('🔴 Same classification - not counting');
          }
        }
      } else {
        setCameraSystem(prev => ({ ...prev, systemStatus: 'error' }));
      }
    } catch (error) {
      setCameraSystem(prev => ({ ...prev, systemStatus: 'disconnected' }));
    }
  };

  // Start camera system
  const startCameraSystem = async () => {
    try {
      const response = await fetch(`${CLASSIFICATION_API_URL}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        fetchCameraStatus();
      }
    } catch (error) {
      console.error('Failed to start camera system:', error);
    }
  };

  // Stop camera system
  const stopCameraSystem = async () => {
    try {
      const response = await fetch(`${CLASSIFICATION_API_URL}/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        fetchCameraStatus();
      }
    } catch (error) {
      console.error('Failed to stop camera system:', error);
    }
  };

  // Poll camera status every 2 seconds
  useEffect(() => {
    fetchCameraStatus(); // Initial fetch
    const interval = setInterval(fetchCameraStatus, 2000);
    return () => clearInterval(interval);
  }, []);

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
        {cameraSystem.systemStatus === 'connected' && cameraSystem.running ? (
          <div style={{
            width: "90%",
            height: "70%",
            borderRadius: "12px",
            overflow: "hidden",
            border: "3px solid #28a745",
            position: "relative"
          }}>
            <img
              src={`${CLASSIFICATION_API_URL}/video_feed`}
              alt="Live Camera Feed"
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover"
              }}
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />

            {/* Status Overlays */}
            <div style={{
              position: "absolute",
              top: "10px",
              left: "10px",
              background: "rgba(0,0,0,0.7)",
              color: "white",
              padding: "8px 12px",
              borderRadius: "6px",
              fontSize: "14px"
            }}>
              {cameraSystem.classifying ? "🔄 Classifying..." :
                cameraSystem.inCooldown ? "⏳ Cooldown" :
                  "✅ Ready"}
            </div>

            {cameraSystem.latestClassification && (
              <div style={{
                position: "absolute",
                bottom: "10px",
                left: "10px",
                background: "rgba(40, 167, 69, 0.9)",
                color: "white",
                padding: "8px 12px",
                borderRadius: "6px",
                fontSize: "16px",
                fontWeight: "bold"
              }}>
                Last: {cameraSystem.latestClassification.classification?.toUpperCase() || 'Unknown'}
              </div>
            )}
          </div>
        ) : (
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
              <div>Camera System</div>
              <div style={{ fontSize: "14px", marginTop: "8px" }}>
                {cameraSystem.systemStatus === 'disconnected' ? 'Service Offline' :
                  cameraSystem.systemStatus === 'error' ? 'Connection Error' :
                    'System Stopped'}
              </div>
            </div>
          </div>
        )}

        {/* Camera Controls */}
        <div style={{
          display: "flex",
          gap: "15px",
          marginTop: "20px"
        }}>
          <button
            onClick={startCameraSystem}
            disabled={cameraSystem.running || cameraSystem.systemStatus !== 'connected'}
            style={{
              ...buttonStyle,
              background: cameraSystem.running ? "#6c757d" : "#28a745",
              cursor: cameraSystem.running || cameraSystem.systemStatus !== 'connected' ? "not-allowed" : "pointer"
            }}
          >
            {cameraSystem.running ? "Running" : "Start Camera"}
          </button>

          <button
            onClick={stopCameraSystem}
            disabled={!cameraSystem.running || cameraSystem.systemStatus !== 'connected'}
            style={{
              ...buttonStyle,
              background: !cameraSystem.running ? "#6c757d" : "#dc3545",
              cursor: !cameraSystem.running || cameraSystem.systemStatus !== 'connected' ? "not-allowed" : "pointer"
            }}
          >
            Stop Camera
          </button>
        </div>

        <div style={{
          position: "absolute",
          bottom: "30px",
          color: cameraSystem.systemStatus === 'connected' ? "#28a745" : "#dc3545",
          fontSize: "14px",
          fontWeight: "bold"
        }}>
          Status: {cameraSystem.systemStatus === 'connected' ?
            (cameraSystem.running ? "Active Detection" : "System Ready") :
            cameraSystem.systemStatus === 'disconnected' ? "Service Offline" : "Connection Error"}
        </div>
      </div>

      {/* Tracking Panel Section */}
      <div style={trackingPanelStyle}>
        <div style={{
          marginBottom: "30px",
          textAlign: "center",
          position: "relative"
        }}>
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