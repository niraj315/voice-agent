import asyncio
import aiohttp
import speech_recognition as sr
from openai import OpenAI

GOOGLE_API_KEY=""
client = OpenAI(
    api_key = GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
def main():
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
        
        print("🤖:",response.choices[0].message.content )

main()