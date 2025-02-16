import sounddevice as sd
import wavio
import tempfile
import os
from openai import OpenAI
from openai import APIConnectionError, APIError

def record_audio(filename, duration=5, fs=44100, channels=1):
    """Records audio from the microphone and saves it as a WAV file."""
    print(f"Recording audio for {duration} seconds...")
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=channels)
        sd.wait()
        wavio.write(filename, recording, fs, sampwidth=2)
        print(f"Recording saved to {filename}")
    except Exception as e:
        print(f"Recording error: {str(e)}")
        raise

def transcribe_audio(client, file_path):
    """Sends the audio file to OpenAI for transcription."""
    try:
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return response
    except APIConnectionError as e:
        print(f"Connection error: {e.__cause__}")
        raise
    except APIError as e:
        print(f"API error: {e}")
        raise
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        raise

def main():
    client = OpenAI(api_key="OPENAI_KEY")
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_filename = tmp.name
        print(f"Temporary file created: {temp_filename}")

        # Record audio
        record_audio(temp_filename, duration=5)
        
        # Verify the file exists and has content
        if os.path.getsize(temp_filename) == 0:
            raise ValueError("Recorded file is empty")
            
        # Transcribe audio
        transcription = transcribe_audio(client, temp_filename)
        
        print("\nTranscription Result:")
        print(transcription if transcription else "No transcription returned")
        
    except Exception as e:
        print(f"Main error: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            print(f"Temporary file {temp_filename} removed")

if __name__ == "__main__":
    main()



