import { useEffect, useState, useRef } from "react"

export default function HumanTrackingEyes({ onNavigate }) {
    const [offset, setOffset] = useState(0)
    const [verticalOffset, setVerticalOffset] = useState(0)
    const [trackingMode, setTrackingMode] = useState("mouse") // "mouse" or "human"
    const [humanDetected, setHumanDetected] = useState(false)
    const [apiStatus, setApiStatus] = useState("disconnected")

    // Use ref to avoid stale closure in intervals
    const trackingModeRef = useRef(trackingMode)
    const intervalRef = useRef(null)

    // Update ref when state changes
    useEffect(() => {
        trackingModeRef.current = trackingMode
    }, [trackingMode])

    // Human detection API polling
    useEffect(() => {
        const fetchHumanCoordinates = async () => {
            if (trackingModeRef.current !== "human") return

            try {
                const response = await fetch('http://localhost:5001/coordinates')

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`)
                }

                const data = await response.json()
                setApiStatus("connected")

                if (data.detected && data.x !== null && data.y !== null) {
                    setHumanDetected(true)

                    // Convert human coordinates to eye movement
                    // Assuming camera resolution is 640x480 (adjust based on your camera)
                    const cameraWidth = 640
                    const cameraHeight = 480

                    // Calculate horizontal offset (-40 to 40 like mouse tracking) - FLIPPED for natural movement
                    const horizontalPercent = data.x / cameraWidth
                    const newOffset = (0.5 - horizontalPercent) * 40  // Flipped X-axis

                    // Calculate vertical offset for more natural tracking
                    const verticalPercent = data.y / cameraHeight
                    const newVerticalOffset = (verticalPercent - 0.5) * 20

                    setOffset(newOffset)
                    setVerticalOffset(newVerticalOffset)
                } else {
                    setHumanDetected(false)
                    // Keep last position when human not detected
                }

            } catch (error) {
                console.error('Failed to fetch human coordinates:', error)
                setApiStatus("disconnected")
                setHumanDetected(false)
            }
        }

        if (trackingMode === "human") {
            // Start polling for human coordinates
            intervalRef.current = setInterval(fetchHumanCoordinates, 100) // 10 FPS

            return () => {
                if (intervalRef.current) {
                    clearInterval(intervalRef.current)
                }
            }
        }
    }, [trackingMode])

    // Mouse tracking (original functionality)
    useEffect(() => {
        if (trackingMode !== "mouse") return

        const handleMouse = (e) => {
            const percent = e.clientX / window.innerWidth
            const newOffset = (percent - 0.5) * 40
            const verticalPercent = e.clientY / window.innerHeight
            const newVerticalOffset = (verticalPercent - 0.5) * 20

            setOffset(newOffset)
            setVerticalOffset(newVerticalOffset)
        }

        window.addEventListener("mousemove", handleMouse)
        return () => window.removeEventListener("mousemove", handleMouse)
    }, [trackingMode])

    // Start/stop human detection API
    const toggleDetectionMode = async () => {
        if (trackingMode === "mouse") {
            // Switch to human tracking - start detection
            try {
                const response = await fetch('http://localhost:5001/start', {
                    method: 'POST'
                })
                const data = await response.json()

                if (data.status === 'success') {
                    setTrackingMode("human")
                } else {
                    alert(`Failed to start human detection: ${data.message}`)
                }
            } catch (error) {
                alert(`Failed to start human detection: ${error.message}`)
            }
        } else {
            // Switch to mouse tracking - stop detection
            try {
                const response = await fetch('http://localhost:5001/stop', {
                    method: 'POST'
                })
                const data = await response.json()

                setTrackingMode("mouse")
                setHumanDetected(false)
                setApiStatus("disconnected")
            } catch (error) {
                console.error('Failed to stop human detection:', error)
                // Switch anyway since we're going back to mouse mode
                setTrackingMode("mouse")
                setHumanDetected(false)
                setApiStatus("disconnected")
            }
        }
    }

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
        width: "200px",
        height: "120px",
        background: trackingMode === "human" ?
            (humanDetected ? "#00ff41" : "#ff4444") : "#00ff41",
        borderRadius: "60px",
        transform: `translate(${offset}px, ${verticalOffset}px)`,
        transition: "transform 0.15s ease-out, background-color 0.3s ease",
        boxShadow: trackingMode === "human" ?
            (humanDetected ? "inset 0 4px 8px rgba(0,255,65,0.3), 0 0 20px rgba(0,255,65,0.2)" :
                "inset 0 4px 8px rgba(255,68,68,0.3), 0 0 20px rgba(255,68,68,0.2)") :
            "inset 0 4px 8px rgba(0,255,65,0.3), 0 0 20px rgba(0,255,65,0.2)",
        border: trackingMode === "human" ?
            (humanDetected ? "4px solid #00cc33" : "4px solid #cc3333") :
            "4px solid #00cc33"
    }

    const getStatusColor = () => {
        if (trackingMode === "mouse") return "#6c757d"
        if (apiStatus === "disconnected") return "#dc3545"
        if (humanDetected) return "#28a745"
        return "#ffc107"
    }

    const getStatusText = () => {
        if (trackingMode === "mouse") return "Mouse Tracking"
        if (apiStatus === "disconnected") return "API Disconnected"
        if (humanDetected) return "Human Detected"
        return "Searching for Human..."
    }

    return (
        <div style={{
            background: "linear-gradient(135deg, #28a745 0%, #20c997 100%)",
            width: "100vw",
            height: "100vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontFamily: "monospace",
            position: "relative"
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

            {/* Status Display */}
            <div style={{
                position: "absolute",
                top: "30px",
                left: "30px",
                background: "rgba(0,0,0,0.8)",
                color: "white",
                padding: "15px 20px",
                borderRadius: "10px",
                fontSize: "16px",
                fontWeight: "bold",
                display: "flex",
                alignItems: "center",
                gap: "10px"
            }}>
                <div style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    background: getStatusColor(),
                    boxShadow: `0 0 10px ${getStatusColor()}`
                }}></div>
                {getStatusText()}
            </div>

            {/* Tracking Mode Toggle */}
            <button
                onClick={toggleDetectionMode}
                style={{
                    position: "absolute",
                    top: "100px",
                    left: "30px",
                    background: trackingMode === "human" ? "#dc3545" : "#007bff",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "12px 20px",
                    fontSize: "14px",
                    fontWeight: "bold",
                    cursor: "pointer",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
                    transition: "all 0.3s ease"
                }}
                onMouseOver={(e) => {
                    e.target.style.transform = "translateY(-2px)"
                }}
                onMouseOut={(e) => {
                    e.target.style.transform = "translateY(0px)"
                }}
            >
                {trackingMode === "human" ? "👁️ Stop Human Tracking" : "🤖 Start Human Tracking"}
            </button>

            {/* Coordinate Display (when human detected) */}
            {trackingMode === "human" && humanDetected && (
                <div style={{
                    position: "absolute",
                    bottom: "30px",
                    left: "30px",
                    background: "rgba(0,255,65,0.9)",
                    color: "#000",
                    padding: "10px 15px",
                    borderRadius: "8px",
                    fontSize: "14px",
                    fontWeight: "bold"
                }}>
                    Eyes: ({Math.round(offset)}, {Math.round(verticalOffset)})
                </div>
            )}

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

            {/* Human Detection Video (when active) */}
            {trackingMode === "human" && (
                <div style={{
                    position: "absolute",
                    bottom: "30px",
                    right: "30px",
                    width: "240px",
                    height: "180px",
                    background: "#000",
                    border: "3px solid #fff",
                    borderRadius: "8px",
                    overflow: "hidden"
                }}>
                    <img
                        src="http://localhost:5001/video_feed"
                        alt="Human Detection Feed"
                        style={{
                            width: "100%",
                            height: "100%",
                            objectFit: "cover"
                        }}
                        onError={(e) => {
                            e.target.style.display = 'none'
                        }}
                    />
                </div>
            )}
        </div>
    )
}