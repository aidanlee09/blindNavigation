# blindNavigation

## Backend

### Setup

cd to project directory (../blindNavigation)

#### ENV SETUP
```
conda create --name blindnav python=3.11 -y
conda activate blindnav
```

#### INSTALL DEPENDENCIES
```
conda install pytorch torchvision torchaudio -c pytorch-nightly
pip install fastapi uvicorn opencv-python numpy pillow
pip install langchain langchain-openai openai
pip install elevenlabs
pip install python-dotenv
pip install python-multipart
pip install pillow pillow-heif
pip install sounddevice
pip install tensorflow tensorflow-hub
pip install tensorflow-macos tensorflow-metal tensorflow-hub
pip install scipy
pip install timm
pip install --upgrade langchain langchain-community langchain-openai
```

#### VERIFY (in terminal)

```
python
import torch 
import openai
import langchain
import elevenlabs
from dotenv import load_dotenv
print("MPS (Apple GPU) Available:", torch.backends.mps.is_available())
print("MPS Backend Built:", torch.backends.mps.is_built())
print("PyTorch Version:", torch.__version__)
print("OpenAI Installed:", openai.__version__)
print("LangChain Installed:", langchain.__version__)
print("ElevenLabs Installed:", hasattr(elevenlabs, "generate"))
```

#### check if everything returns the right string

#### DEACTIVATE
```
conda deactivate
```

### Start Fast API Server

```
uvicorn main:app --reload
```

Once the server starts, visit:

Swagger UI (API Docs): http://127.0.0.1:8000/docs

JSON Response (Basic Test): http://127.0.0.1:8000

### Exit

control + c