import os
from flask import Flask, request, jsonify
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
import openai

# Set up Flask app
app = Flask("FermiVoice")

# Set up Google Speech-to-Text client
speech_client = speech.SpeechClient()

# Set up Google Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

# Set up OpenAI API client
openai.api_key = os.environ.get('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')

# Define endpoint for voice assistant
@app.route('/voice-assistant', methods=['POST'])
def voice_assistant():
    # Get audio data from request
    audio_data = request.files['audio_data'].read()

    # Convert audio data to text
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='en-US',
        sample_rate_hertz=16000,
    )
    audio = speech.RecognitionAudio(content=audio_data)
    response = speech_client.recognize(config=config, audio=audio)
    text_input = response.results[0].alternatives[0].transcript

    # Generate response with ChatGPT
    response = openai.Completion.create(
        engine='text-davinci-002',
        prompt=text_input,
        max_tokens=50,
    )
    text_output = response.choices[0].text.strip()

    # Convert response text to speech
    synthesis_input = texttospeech.SynthesisInput(text=text_output)
    voice = texttospeech.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Wavenet-D',
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    tts_response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    audio_output = tts_response.audio_content

    # Return speech response to voice assistant
    return jsonify({'audio_data': audio_output})
