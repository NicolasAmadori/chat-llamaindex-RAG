FROM huggingface/transformers-pytorch-latest-gpu
# Set work directory
RUN mkdir -p ./src
WORKDIR ./src
COPY . .

RUN pip3 install torch==1.10.2+cu113 torchvision==0.11.3+cu113 torchaudio==0.10.2+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
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
RUN apt update
# RUN apt install nodejs 
# RUN apt install npm
# RUN npm install -g npm
# RUN cd ./frontend && npm install
# RUN cd ../backend && poetry install

RUN python3 -m http.server