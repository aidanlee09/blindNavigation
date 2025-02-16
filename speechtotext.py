from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from langchain.chains import LLMChain 
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import sounddevice as sd
import numpy as np
import tensorflow_hub as hub
from elevenlabs import play
import os
load_dotenv()

SAMPLE_RATE = 16000  # yAMNet requires 16kHz
RECORD_DURATION = 3  # seconds per analysis window
YAMNET_MODEL = 'https://tfhub.dev/google/yamnet/1'
yamnet_model = hub.load(YAMNET_MODEL)
class_map_path = yamnet_model.class_map_path().numpy().decode('utf-8')
class_names = []
with open(class_map_path) as csv_file:
    import csv
    reader = csv.reader(csv_file)
    class_names = [row[2] for row in reader]  # index 2 contains actual class names
os.environ["ELEVENLABS_API_KEY"] = "voice-key"
os.environ["OPENAI_API_KEY"] = "ai-key"
#keys redacted for now in repo
client = ElevenLabs()
llm = OpenAI(temperature=0.1)

def record_environment():
    """Capture live audio input"""
    try:
        audio = sd.rec(int(RECORD_DURATION * SAMPLE_RATE),
                      samplerate=SAMPLE_RATE,
                      channels=1,
                      dtype='float32')
        sd.wait()
        return audio.flatten()
    except Exception as e:
        print(f"Audio recording failed: {e}")
        return None
    
def analyze_sounds(audio):
    """Analyze audio using YAMNet classification"""
    try:
        # convert to expected format
        waveform = audio / np.max(np.abs(audio))  # Normalize
        scores, embeddings, spectrogram = yamnet_model(waveform)
        
        # get top predictions
        mean_scores = np.mean(scores, axis=0)
        top_classes = np.argsort(mean_scores)[::-1][:3]
        
        detected = []
        for class_idx in top_classes:
            if mean_scores[class_idx] > 0.15:  # confidence threshold
                detected.append(class_names[class_idx].split(',')[0])
                
        return detected if detected else ["No identifiable sounds"]
    except Exception as e:
        print(f"Sound analysis failed: {e}")
        return ["Analysis error"]
    
def generate_guidance(sound_labels):
    """Generate navigation advice using LLM"""
    prompt_template = PromptTemplate.from_template(
        """As a navigation assistant for the visually impaired, analyze these sound detections:
        {sound_input}
        
        Provide:
        1. Immediate directional advice
        2. Clear movement instructions
        3. Hazard warnings
        
        Format: 
        - [Priority Level] [Direction] [Instruction] [Reason]"""
    )
    
    safety_chain = LLMChain(llm=llm, prompt=prompt_template)
    return safety_chain.invoke({"sound_input": ", ".join(sound_labels)})['text']

def speak_response(text):
    """Convert text to speech"""
    try: 
        audio = client.text_to_speech.convert(
            text=text,
            voice_id="gOkFV1JMCt0G0n9xmBwV",
            model_id="eleven_flash_v2",
            output_format="mp3_44100_128"
        )
        play(audio)
    except Exception as e:
        print(f"Voice synthesis failed: {e}")

def navigation_assistant():
    """Main processing loop"""
    print("Listening to environment...")
    while True:
        # 1. Capture audio
        audio = record_environment()
        if audio is None:
            continue
          # 2. Analyze sounds
        sound_labels = analyze_sounds(audio)
        print(f"Detected: {', '.join(sound_labels)}")
        
        # 3. Generate guidance
        guidance = generate_guidance(sound_labels)
        print(f"Guidance: {guidance}")
        
        # 4. Speak response
        speak_response(guidance)
        
navigation_assistant()