import { useEffect, useState } from "react"

export default function ThankYou({ onNavigate }) {
  const [showContent, setShowContent] = useState(false)
  const [particles, setParticles] = useState([])

  useEffect(() => {
    // Trigger content animation
    setTimeout(() => setShowContent(true), 500)

    // Generate floating particles
    const newParticles = []
    for (let i = 0; i < 15; i++) {
      newParticles.push({
        id: i,
        left: Math.random() * 100,
        animationDelay: Math.random() * 3,
        size: Math.random() * 20 + 10
      })
    }
    setParticles(newParticles)
  }, [])

  const containerStyle = {
    width: "100vw",
    height: "100vh",
    background: "linear-gradient(45deg, #667eea 0%, #764ba2 50%, #f093fb 100%)",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
    overflow: "hidden",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
  }

  const thankYouTextStyle = {
    fontSize: "4rem",
    fontWeight: "bold",
    color: "white",
    textAlign: "center",
    marginBottom: "2rem",
    textShadow: "0 4px 8px rgba(0,0,0,0.3)",
    transform: showContent ? "translateY(0) scale(1)" : "translateY(50px) scale(0.8)",
    opacity: showContent ? 1 : 0,
    transition: "all 1s ease-out"
  }

  const messageStyle = {
    fontSize: "1.5rem",
    color: "white",
    textAlign: "center",
    marginBottom: "3rem",
    maxWidth: "600px",
    lineHeight: "1.6",
    textShadow: "0 2px 4px rgba(0,0,0,0.3)",
    transform: showContent ? "translateY(0)" : "translateY(30px)",
    opacity: showContent ? 1 : 0,
    transition: "all 1.2s ease-out 0.3s"
  }

  const buttonContainerStyle = {
    display: "flex",
    gap: "20px",
    transform: showContent ? "translateY(0)" : "translateY(30px)",
    opacity: showContent ? 1 : 0,
    transition: "all 1s ease-out 0.6s"
  }

  const buttonStyle = {
    background: "rgba(255,255,255,0.2)",
    color: "white",
    border: "2px solid rgba(255,255,255,0.3)",
    borderRadius: "50px",
    padding: "16px 32px",
    fontSize: "18px",
    fontWeight: "bold",
    cursor: "pointer",
    backdropFilter: "blur(10px)",
    transition: "all 0.3s ease",
    textShadow: "0 1px 2px rgba(0,0,0,0.3)"
  }

  return (
    <div style={containerStyle}>
      {/* Animated CSS */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        @keyframes sparkle {
          0%, 100% { opacity: 0.7; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.2); }
        }
        
        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-10px); }
          60% { transform: translateY(-5px); }
        }
        
        .particle {
          position: absolute;
          background: rgba(255,255,255,0.8);
          border-radius: 50%;
          pointer-events: none;
          animation: float 4s ease-in-out infinite;
        }
        
        .emoji-bounce {
          animation: bounce 2s ease-in-out infinite;
        }
      `}</style>

      {/* Floating Particles */}
      {particles.map(particle => (
        <div
          key={particle.id}
          className="particle"
          style={{
            left: `${particle.left}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            animationDelay: `${particle.animationDelay}s`,
            top: `${Math.random() * 100}%`
          }}
        />
      ))}

      {/* Main Content */}
      <div style={{
        fontSize: "5rem",
        marginBottom: "1rem",
        transform: showContent ? "scale(1)" : "scale(0)",
        transition: "all 0.8s ease-out 0.2s"
      }} className="emoji-bounce">
        🎉
      </div>

      <h1 style={thankYouTextStyle}>
        THANK YOU!
      </h1>

      <p style={messageStyle}>
        Your contribution to recycling and waste management makes a difference! 
        Every item you've sorted helps create a more sustainable future for our planet. 
        Together, we're building a cleaner, greener world.
      </p>

      <div style={buttonContainerStyle}>
        <button
          style={buttonStyle}
          onClick={() => onNavigate('tracker')}
          onMouseOver={(e) => {
            e.target.style.background = "rgba(255,255,255,0.3)"
            e.target.style.transform = "translateY(-3px)"
            e.target.style.boxShadow = "0 8px 20px rgba(255,255,255,0.2)"
          }}
          onMouseOut={(e) => {
            e.target.style.background = "rgba(255,255,255,0.2)"
            e.target.style.transform = "translateY(0)"
            e.target.style.boxShadow = "none"
          }}
        >
          🗑️ Back to Tracker
        </button>

        <button
          style={buttonStyle}
          onClick={() => onNavigate('eyes')}
          onMouseOver={(e) => {
            e.target.style.background = "rgba(255,255,255,0.3)"
            e.target.style.transform = "translateY(-3px)"
            e.target.style.boxShadow = "0 8px 20px rgba(255,255,255,0.2)"
          }}
          onMouseOut={(e) => {
            e.target.style.background = "rgba(255,255,255,0.2)"
            e.target.style.transform = "translateY(0)"
            e.target.style.boxShadow = "none"
          }}
        >
          👁️ Eyes Page
        </button>
      </div>

      {/* Decorative Elements */}
      <div style={{
        position: "absolute",
        bottom: "50px",
        fontSize: "2rem",
        color: "rgba(255,255,255,0.7)",
        animation: "sparkle 2s ease-in-out infinite",
        left: "10%"
      }}>
        ♻️
      </div>
      
      <div style={{
        position: "absolute",
        top: "100px",
        right: "15%",
        fontSize: "2rem",
        color: "rgba(255,255,255,0.7)",
        animation: "sparkle 2s ease-in-out infinite 0.5s"
      }}>
        🌱
      </div>
      
      <div style={{
        position: "absolute",
        bottom: "100px",
        right: "20%",
        fontSize: "2rem",
        color: "rgba(255,255,255,0.7)",
        animation: "sparkle 2s ease-in-out infinite 1s"
      }}>
        🌍
      </div>
    </div>
  )
}