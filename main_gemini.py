import os
from dotenv import load_dotenv
import speech_recognition as sr
from openai import OpenAI
from google import genai
from google.genai import types
import sounddevice  as sd
import numpy as np

load_dotenv()
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")

client = OpenAI(
    api_key = GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

gemini_client = genai.Client(
    api_key= GOOGLE_API_KEY
)


#tts with gemini
def tts(speech:str): #Function for Text to Speech
    print("in tts function...")

    stream = sd.OutputStream(samplerate=24000, channels=1,dtype=np.int16) #Used stream for faster audio outout
    stream.start()

    response_stream = gemini_client.models.generate_content_stream(
        model="gemini-3.1-flash-tts-preview",
        contents= speech,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                )
            )
        )
    )
    for chunk in response_stream:
        if chunk.candidates and chunk.candidates[0].content.parts:
            part =chunk.candidates[0].content.parts[0]
            pcm_chunk = part.inline_data.data
            audio_array = np.frombuffer(pcm_chunk,dtype=np.int16)
            stream.write(audio_array)
    
    stream.stop()
    stream.close()

def stt():  #Function for Speech to Text
    r= sr.Recognizer() # Will convert audio to text(STT)

    with sr.Microphone() as source: #Mic Access
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2 # Will wait for 2 second before processing audio

        print("Speak something...")
        audio = r.listen(source) #Listen user audio and saves it to audio

        print("Processing audio for STT...")
        speech = r.recognize_google(audio) #Convert audio to speech

        print(f"you said :",{speech}  )

        SYSTEM_PROMPT =f"""
            You are voice agent. You are given transcript what user has said.
            You will give answer to that transcript which will be again will be converted to voice as a reply to user.
        """
        response = client.chat.completions.create(
            model ="gemini-3-flash-preview",
            messages=[
                {"role": "system","content": SYSTEM_PROMPT},
                {"role" : "user","content": speech }
            ]
        )
        
        print("🤖:",response.choices[0].message.content)
        speech = response.choices[0].message.content
        tts(speech)

stt()