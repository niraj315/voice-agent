import asyncio
import aiohttp
import speech_recognition as sr
from openai import OpenAI,AsyncOpenAI
from openai.helpers import LocalAudioPlayer

GOOGLE_API_KEY="AIzaSyB0p1v8YhZbUnUedsnFd1T0pWICsPRaWh0"
client = OpenAI(
    api_key = GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
# async_client = AsyncOpenAI(
#     api_key = "AIzaSyB0p1v8YhZbUnUedsnFd1T0pWICsPRaWh0",
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )

# async def tts(speech: str):
#     async with async_client.audio.speech.with_streaming_response.create(
#         model="google/gemini-3.1-flash-tts-preview",
#         input=speech,
#         response_format="pcm",
#         voice="coral"

#     )as response:
#         await LocalAudioPlayer().play(response)

#FROM GEMINI CHAT
async def tts(speech: str):
    # This is Google's official REST path for text-to-speech models
    url = f"https://googleapis.com{GOOGLE_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": speech}]}],
        "generationConfig": {
            "responseMimeType": "audio/pcm", # Forces raw PCM output 
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": "coral"}
                }
            }
        }
    }

    # Stream the raw bytes directly over an HTTP pipe to dodge the 404
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                # LocalAudioPlayer reads this clean stream without formatting issues
                await LocalAudioPlayer().play(response)
            else:
                print(f"TTS Engine Error: {response.status}")
#######   
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
        asyncio.run(tts(speech=response.choices[0].message.content))

main()