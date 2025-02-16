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
pip install git+https://github.com/facebookresearch/segment-anything.git
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

## Citation

@article{depth_anything_v2,
  title={Depth Anything V2},
  author={Yang, Lihe and Kang, Bingyi and Huang, Zilong and Zhao, Zhen and Xu, Xiaogang and Feng, Jiashi and Zhao, Hengshuang},
  journal={arXiv:2406.09414},
  year={2024}
}

@inproceedings{depth_anything_v1,
  title={Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data}, 
  author={Yang, Lihe and Kang, Bingyi and Huang, Zilong and Xu, Xiaogang and Feng, Jiashi and Zhao, Hengshuang},
  booktitle={CVPR},
  year={2024}
}

@article{kirillov2023segany,
  title={Segment Anything},
  author={Kirillov, Alexander and Mintun, Eric and Ravi, Nikhila and Mao, Hanzi and Rolland, Chloe and Gustafson, Laura and Xiao, Tete and Whitehead, Spencer and Berg, Alexander C. and Lo, Wan-Yen and Doll{\'a}r, Piotr and Girshick, Ross},
  journal={arXiv:2304.02643},
  year={2023}
}