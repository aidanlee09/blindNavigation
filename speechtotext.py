from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from langchain.chains import LLMChain 
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import openai
from elevenlabs import play, save
import os 
load_dotenv()

os.environ["ELEVENLABS_API_KEY"] = "voice-key"
os.environ["OPENAI_API_KEY"] = "ai-key"
#keys redacted for now in repo
client = ElevenLabs()

def speak_response(text):
    try: 
        audio = client.text_to_speech.convert(
            text=text,
            voice_id="gOkFV1JMCt0G0n9xmBwV",
            model_id="eleven_flash_v2_5",
            #realtime model. 75ms 
            output_format="mp3_44100_128"
        )
        play(audio)
        save(audio, "last_response.mp3") 
        #can save audios in app, might be a good feature for fine tuning the AI and creating better alerts
    except Exception as e:
        print(f"Voice system unavailable: {e}")

def navigation_assistant():
    audio_file = open("envsounds.mp3", "rb")
    #change file type/name to whatever youre pulling from the app. 
    sound_description = openai.audio.transcribe(
        file=audio_file,
        model="whisper-1",
        response_format="text"
    )

    print(f"{sound_description}")

    llm = OpenAI(temperature=0.1)
    prompt_template = PromptTemplate.from_template(
    """You are a helpful navigation assistant for visually impaired users. 
        Analyze these environmental sounds: {sound_input}
        
        Respond with:
        1. Immediate navigation advice (1-2 sentences)
        2. Clear movement instructions
        3. Potential hazards to avoid and environmental context
        
        Examples of good responses:
        - "I hear rushing water ahead. Please turn right to avoid the drainage ditch."
        - "There's loud honking 10 meters ahead. Pause and wait for traffic to clear."
        - "Bird chirping detected to your left, clear path ahead. Continue straight."
        
        Current situation:"""
    )
    safety_chain = LLMChain(llm=llm, prompt=prompt_template)
    guidance = safety_chain.invoke({"sound_input": sound_description})

    speak_response(guidance['text'])
    return guidance['text'] 

advice = navigation_assistant()
print(f"\n Navigation Assistant: {advice}")