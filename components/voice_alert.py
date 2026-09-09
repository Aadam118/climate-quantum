"""
components/voice_alert.py
---------------------------
Speaks the AQI result aloud using the browser-native Web Speech API
(SpeechSynthesisUtterance) — no server-side TTS engine or extra Python
dependency (e.g. gTTS) required, and it works fully offline.
"""

import streamlit.components.v1 as components


def get_voice_category(aqi_value: float) -> str:
    """Voice-friendly AQI category label. Kept as its own mapping (rather
    than reusing utils.get_aqi_category) to preserve the exact original
    spoken wording, e.g. 'Unhealthy for Sensitive Groups'."""
    if aqi_value <= 50:
        return "Good"
    elif aqi_value <= 100:
        return "Moderate"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi_value <= 200:
        return "Unhealthy"
    elif aqi_value <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def build_voice_text(aqi_value: float) -> str:
    category = get_voice_category(aqi_value)
    return f"predicted A Q I {aqi_value} hai . jo ki {category} category me aata hai."


def speak_announcement(text: str, run_id: int):
    """
    Inject a tiny, invisible HTML component that speaks `text` aloud.

    `run_id` is embedded in the component so that a *new* prediction with the
    exact same wording (e.g. two identical AQI results in a row) still forces
    Streamlit to re-mount the component and re-trigger speech, instead of
    silently reusing the previous iframe.
    """
    safe_text = text.replace("\\", "").replace('"', "'")
    components.html(
        f"""
        <script>
            (function() {{
                try {{
                    const synth = window.speechSynthesis;
                    synth.cancel();  // stop any previous utterance first
                    const utterance = new SpeechSynthesisUtterance("{safe_text}");
                    utterance.rate = 0.95;
                    utterance.pitch = 1.0;
                    utterance.volume = 1.0;
                    utterance.lang = "hi-IN";
                    synth.speak(utterance);
                }} catch (err) {{
                    console.warn("Speech synthesis unavailable:", err);
                }}
            }})();
        </script>
        <!-- run_id: {run_id} -->
        """,
        height=0,
        width=0,
    )
