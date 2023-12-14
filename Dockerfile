FROM python:3.10.6
# Set work directory
RUN mkdir -p ./src
WORKDIR ./src
COPY . .

#ÂRUN apt-key del 7fa2af80
#RUN apt install wget
#RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
#RUN dpkg -i cuda-keyring_1.0-1_all.deb
RUN apt update
RUN pip install https://download.pytorch.org/whl/cu113/torch-1.12.1%2Bcu113-cp310-cp310-linux_x86_64.whl#sha256=be682ef94e37cd3f0768b8ce6106705410189df2c365d65d7bc1bebb302d84cd

#RUN pip3 install torch==1.10.2+cu113 torchvision==0.11.3+cu113 torchaudio==0.10.2+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
RUN pip3 install git+https://github.com/huggingface/transformers
RUN pip3 install --upgrade nvidia-ml-py3==7.352.0
RUN pip3 install --upgrade sentence-transformers==2.2.2
RUN pip3 install --upgrade accelerate==0.14.0
RUN pip3 install --upgrade codecarbon==2.1.4
RUN pip3 install --upgrade streamlit==1.14.0
RUN pip3 install --upgrade wget==3.2
RUN pip3 install --upgrade tensorflow==2.10.0
RUN pip3 install --upgrade tensorflow-datasets==4.7.0
RUN pip3 install --upgrade scikit-learn==1.1.3
RUN pip3 install --upgrade nltk==3.7
RUN pip3 install --upgrade stqdm==0.0.4
RUN pip3 install --upgrade datasets==2.6.1
RUN pip3 install --upgrade wandb==0.13.5 
RUN pip3 install poetry


RUN apt install -y nodejs 
RUN apt install -y npm
RUN npm install -g npm
RUN cd ./frontend && npm install
RUN cd ../backend && poetry install

RUN python3 -m http.server
