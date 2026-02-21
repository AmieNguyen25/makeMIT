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

    // 🔊 Trigger ElevenLabs voice after animation starts
    const voiceTimer = setTimeout(async () => {
      console.log('🎤 Auto-speaking with ElevenLabs on ThankYou page load...')
      
      try {
        const text = "Thank you for recycling. Your action helps create a cleaner and greener future."
        
        const res = await fetch("http://127.0.0.1:5000/tts", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text }),
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`)
        }

        const data = await res.json();
        console.log('✅ ElevenLabs auto-speak response received')

        if (data.audio) {
          console.log('🔊 Auto-playing ElevenLabs Female Voice')
          const audio = new Audio("data:audio/mp3;base64," + data.audio);
          await audio.play();
          console.log('✅ ElevenLabs auto-speak played successfully!')
        } else {
          throw new Error('No audio data from ElevenLabs')
        }
      } catch (err) {
        console.error("❌ ElevenLabs auto-speak failed:", err)
        // Fallback to passed speak function
        if (speak) {
          console.log('🔄 Using fallback for auto-speak')
          speak("Thank you for recycling. Your action helps create a cleaner and greener future.")
        }
      }
    }, 1000)

    return () => clearTimeout(voiceTimer)
  }, [speak])

  const handleSpeak = async () => {
    console.log('🎤 ThankYou: Speaking with ElevenLabs API...')
    
    try {
      const text = "Thank you for recycling. Your action helps create a cleaner and greener future."
      
      const res = await fetch("http://127.0.0.1:5000/tts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      }

      const data = await res.json();
      console.log('✅ ElevenLabs Response received for ThankYou')

      if (data.audio) {
        console.log('🔊 Playing ElevenLabs Female Voice for ThankYou')
        const audio = new Audio("data:audio/mp3;base64," + data.audio);
        await audio.play();
        console.log('✅ ElevenLabs ThankYou audio played successfully!')
      } else {
        throw new Error('No audio data received from ElevenLabs')
      }
    } catch (err) {
      console.error("❌ ElevenLabs failed for ThankYou:", err)
      // Fallback to the passed speak function if ElevenLabs fails
      if (speak) {
        console.log('🔄 Using fallback speak function')
        speak("Thank you for recycling. Your action helps create a cleaner and greener future.")
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