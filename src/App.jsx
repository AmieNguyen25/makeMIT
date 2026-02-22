import { useState, useRef } from 'react'
import Eyes from "./eyes.jsx"
import HumanTrackingEyes from "./HumanTrackingEyes.jsx"
import TrashTracker from "./TrashTracker.jsx"
import ThankYou from "./ThankYou.jsx"

function App() {
  const [currentPage, setCurrentPage] = useState('eyes')
  const [eyeType, setEyeType] = useState('human') // 'mouse' or 'human'
  const audioRef = useRef(null)

  const speak = async (text) => {
    console.log('🎤 Using browser TTS:', text)
    useBrowserTTS(text)
  }

  const useBrowserTTS = (text) => {
    if ('speechSynthesis' in window) {
      // Clear any existing speech
      speechSynthesis.cancel()

      const speakText = () => {
        const utterance = new SpeechSynthesisUtterance(text)

        // Get available voices and select a female one
        const voices = speechSynthesis.getVoices()

        // Look for female voices (prefer different female voices)
        const femaleVoice = voices.find(voice =>
          voice.name.toLowerCase().includes('female') ||
          voice.name.toLowerCase().includes('samantha') ||
          voice.name.toLowerCase().includes('alex') ||
          voice.name.toLowerCase().includes('susan') ||
          voice.name.toLowerCase().includes('allison') ||
          voice.name.toLowerCase().includes('ava') ||
          voice.name.toLowerCase().includes('karen') ||
          voice.name.toLowerCase().includes('moira') ||
          voice.name.toLowerCase().includes('tessa') ||
          voice.name.toLowerCase().includes('veena') ||
          voice.name.toLowerCase().includes('fiona') ||
          (voice.name.toLowerCase().includes('microsoft') && voice.name.toLowerCase().includes('zira')) ||
          (voice.name.toLowerCase().includes('google') && voice.name.toLowerCase().includes('female'))
        ) || voices.find(voice => voice.gender === 'female')

        if (femaleVoice) {
          utterance.voice = femaleVoice
          console.log('Using female voice:', femaleVoice.name)
        }

        // Natural speech settings
        utterance.rate = 0.85    // Slightly slower for clarity
        utterance.pitch = 1.1    // Slightly higher pitch for female voice
        utterance.volume = 0.9   // Clear but not too loud

        // Add natural pauses
        const naturalText = text.replace(/\./g, '... ').replace(/,/g, ', ')
        utterance.text = naturalText

        speechSynthesis.speak(utterance)
      }

      // Check if voices are loaded
      if (speechSynthesis.getVoices().length > 0) {
        speakText()
      } else {
        // Wait for voices to load
        speechSynthesis.addEventListener('voiceschanged', speakText, { once: true })
      }
    } else {
      console.log("Speech synthesis not supported")
    }
  }

  const handleNavigation = (page) => {
    setCurrentPage(page)
  }

  return (
    <>
      <audio
        ref={audioRef}
        preload="auto"
        onLoadStart={() => console.log('🔄 Audio loading...')}
        onCanPlay={() => console.log('✅ Audio ready to play')}
        onPlay={() => console.log('▶️ Audio started playing')}
        onEnded={() => console.log('⏹️ Audio finished')}
        onError={(e) => console.error('❌ Audio error:', e)}
      />

      {currentPage === 'eyes' && eyeType === 'mouse' && (
        <div>
          <Eyes onNavigate={() => handleNavigation('tracker')} />
          <button
            onClick={() => setEyeType('human')}
            style={{
              position: "absolute",
              top: "100px",
              right: "30px",
              background: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "8px",
              padding: "12px 20px",
              fontSize: "14px",
              fontWeight: "bold",
              cursor: "pointer",
              boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
              zIndex: 1000
            }}
          >
            🤖 Switch to Human Tracking
          </button>
        </div>
      )}

      {currentPage === 'eyes' && eyeType === 'human' && (
        <div>
          <HumanTrackingEyes onNavigate={() => handleNavigation('tracker')} />
          <button
            onClick={() => setEyeType('mouse')}
            style={{
              position: "absolute",
              top: "170px",
              left: "30px",
              background: "#6c757d",
              color: "white",
              border: "none",
              borderRadius: "8px",
              padding: "12px 20px",
              fontSize: "14px",
              fontWeight: "bold",
              cursor: "pointer",
              boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
              zIndex: 1000
            }}
          >
            🖱️ Switch to Mouse Tracking
          </button>
        </div>
      )}

      {currentPage === 'tracker' && (
        <TrashTracker onNavigate={handleNavigation} />
      )}

      {currentPage === 'thankyou' && (
        <ThankYou onNavigate={handleNavigation} speak={speak} />
      )}
    </>
  )
}

export default App