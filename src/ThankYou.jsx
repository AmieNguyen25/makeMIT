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

    // 🔊 Trigger voice after animation starts
    const voiceTimer = setTimeout(() => {
      console.log('🎤 Auto-playing with browser TTS...')
      useBrowserTTS("Thanks for recycling!")
    }, 500)

    return () => clearTimeout(voiceTimer)
  }, [speak])

  const useBrowserTTS = (text) => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      const voices = speechSynthesis.getVoices()

      const femaleVoice = voices.find(voice =>
        voice.name.toLowerCase().includes('female') ||
        voice.name.toLowerCase().includes('zira') ||
        voice.name.toLowerCase().includes('hazel') ||
        voice.name.toLowerCase().includes('samantha')
      )

      if (femaleVoice) {
        utterance.voice = femaleVoice
      }

      utterance.rate = 0.9
      utterance.pitch = 1.1
      utterance.volume = 0.8

      speechSynthesis.speak(utterance)
      console.log('🔊 Browser TTS playing')
    } else {
      console.log('❌ Browser TTS not supported')
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