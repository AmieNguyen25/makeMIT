import { useEffect, useState } from "react"
import "./ThankYou.css"

export default function ThankYou({ onNavigate, speak }) {
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

    // 🔊 Trigger FAST voice after animation starts
    const voiceTimer = setTimeout(async () => {
      console.log('🎤 Auto-playing with FAST endpoint...')
      const startTime = performance.now()
      
      try {
        // Single fast API call for generation + TTS
        const res = await fetch("http://127.0.0.1:5000/fast-thankyou-speech", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`)
        }

        const data = await res.json();
        const clientTime = performance.now() - startTime
        console.log(`⚡ AUTO-FAST Response: ${clientTime.toFixed(0)}ms client + ${data.processing_time_ms}ms server`)
        console.log(`📝 Auto-message (${data.source}): ${data.message}`)

        if (data.audio) {
          console.log('🔊 Auto-playing FAST ElevenLabs audio')
          const audio = new Audio("data:audio/mp3;base64," + data.audio);
          await audio.play();
          console.log('✅ FAST auto-audio played successfully!')
        } else if (data.use_browser_tts) {
          console.log('🔄 Auto-playing browser TTS fallback')
          useBrowserTTS(data.message)
        } else {
          throw new Error('No audio data from fast endpoint')
        }
      } catch (err) {
        console.error("❌ Fast auto-speak failed:", err)
        // Fallback to passed speak function
        if (speak) {
          console.log('🔄 Using original fallback for auto-speak')
          speak("Thanks for recycling!")
        }
      }
    }, 500)

    return () => clearTimeout(voiceTimer)
  }, [speak])

  const handleSpeak = async () => {
    console.log('🎤 ThankYou: Using FAST combined endpoint...')
    const startTime = performance.now()
    
    try {
      // Single fast API call for generation + TTS
      const res = await fetch("http://127.0.0.1:5000/fast-thankyou-speech", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      }

      const data = await res.json();
      const clientTime = performance.now() - startTime
      console.log(`⚡ FAST Response: ${clientTime.toFixed(0)}ms client + ${data.processing_time_ms}ms server`)
      console.log(`📝 Message (${data.source}): ${data.message}`)

      if (data.audio) {
        console.log('🔊 Playing FAST ElevenLabs audio')
        const audio = new Audio("data:audio/mp3;base64," + data.audio);
        await audio.play();
        console.log('✅ FAST audio played successfully!')
      } else if (data.use_browser_tts) {
        console.log('🔄 Using browser TTS fallback')
        useBrowserTTS(data.message)
      } else {
        throw new Error('No audio data received')
      }
    } catch (err) {
      console.error("❌ Fast endpoint failed:", err)
      // Fallback to the passed speak function
      if (speak) {
        console.log('🔄 Using original speak function')
        speak("Thanks for recycling!")
      }
    }
  }

  return (
    <div className="thank-you-container">
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
      <div className={`emoji-main emoji-bounce ${showContent ? 'show' : 'hide'}`}>
        🎉
      </div>

      <h1 className={`thank-you-text ${showContent ? 'show' : 'hide'}`}>
        THANK YOU!
      </h1>

      <p className={`thank-you-message ${showContent ? 'show' : 'hide'}`}>
        Your contribution to recycling and waste management makes a difference! 
        Every item you've sorted helps create a more sustainable future for our planet. 
        Together, we're building a cleaner, greener world.
      </p>

      <div className={`button-container ${showContent ? 'show' : 'hide'}`}>
        <button
          className="thank-you-button"
          onClick={() => onNavigate('tracker')}
        >
          🗑️ Back to Tracker
        </button>

        <button
          className="thank-you-button"
          onClick={handleSpeak}
        >
          🔊 Speak Message
        </button>

        <button
          className="thank-you-button"
          onClick={() => onNavigate('eyes')}
        >
          👁️ Eyes Page
        </button>
      </div>

      {/* Decorative Elements */}
      <div className="decorative-element decorative-recycle">
        ♻️
      </div>
      
      <div className="decorative-element decorative-plant">
        🌱
      </div>
      
      <div className="decorative-element decorative-earth">
        🌍
      </div>
    </div>
  )
}