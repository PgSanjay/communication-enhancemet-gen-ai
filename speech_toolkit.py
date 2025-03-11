import os
import wave
import sounddevice as sd
import speech_recognition as sr
from difflib import SequenceMatcher
import openai

# Set OpenAI API key (replace with your key)
openai.api_key = "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"

RECORDED_FILE = "recorded_audio.wav"

# Record Audio Function
def record_audio(duration=5, rate=16000, channels=1):
    try:
        audio = sd.rec(int(duration * rate), samplerate=rate, channels=channels, dtype="int16")
        sd.wait()
        with wave.open(RECORDED_FILE, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(rate)
            wf.writeframes(audio.tobytes())
        return "Recording complete."
    except Exception as e:
        return f"Failed to record audio: {e}"

# Transcribe Audio Function
def transcribe_audio():
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(RECORDED_FILE) as source:
            audio = recognizer.record(source)
        transcription_result = recognizer.recognize_google(audio)
        return transcription_result
    except Exception as e:
        return f"Failed to transcribe audio: {e}"

# Compare Texts Function
def compare_texts(reference_text, transcription_result):
    sm = SequenceMatcher(None, reference_text, transcription_result)
    accuracy = sm.ratio() * 100
    opcodes = sm.get_opcodes()
    comparison_result = highlight_differences(reference_text, transcription_result, opcodes)
    return accuracy, comparison_result

# Highlight Differences Function
def highlight_differences(reference, transcription, opcodes):
    highlighted = ""
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            highlighted += transcription[j1:j2]
        elif tag == "replace":
            highlighted += f"[{transcription[j1:j2]}]"
        elif tag == "insert":
            highlighted += f"(+{transcription[j1:j2]})"
        elif tag == "delete":
            highlighted += f"(-{reference[i1:i2]})"
    return highlighted

# Generate Suggestions Function
def generate_suggestions(reference_text, transcription_result, differences):
    prompt = (f"Transcription:\n{transcription_result}\n"
              f"Reference:\n{reference_text}\n"
              f"Differences:\n{differences}\n"
              f"Based on these details, suggest how the transcription accuracy can be improved.")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert transcription assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        suggestions = response["choices"][0]["message"]["content"].strip()
        return suggestions
    except Exception as e:
        return f"Failed to generate suggestions: {e}"
