from flask import Flask, request, jsonify
from flask_cors import CORS
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os
import base64

load_dotenv()

app = Flask(__name__)
CORS(app)

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

@app.route("/tts", methods=["POST"])
def text_to_speech():
    try:
        data = request.get_json()
        text = data["text"]

        # Check if API key is valid
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key or len(api_key) < 10:
            raise Exception("Invalid or missing ElevenLabs API key")

        audio_stream = client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",  # Bella - Natural female voice
            model_id="eleven_multilingual_v2",
            text=text,
            voice_settings={
                "stability": 0.75,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True
            }
        )

        audio_bytes = b"".join(audio_stream)

        # Convert to base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return jsonify({
            "audio": audio_base64
        })
        
    except Exception as e:
        print(f"TTS Error: {e}")
        # Return a fallback response to trigger browser TTS
        return jsonify({
            "error": "ElevenLabs TTS unavailable - using browser fallback",
            "audio": None,
            "use_browser_tts": True
        }), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)