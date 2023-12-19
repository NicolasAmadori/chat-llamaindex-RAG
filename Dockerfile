FROM ubuntu

# Set work directory
RUN mkdir -p ./src
WORKDIR ./src
COPY . .

RUN apt update
RUN apt install curl -y
RUN apt install coreutils -y
RUN apt-get install -y ca-certificates curl gnupg && mkdir -p /etc/apt/keyrings && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN NODE_MAJOR=20 && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install nodejs -y
RUN apt-get install aptitude -y
RUN aptitude install npm -y
RUN npm install -g npm
RUN cd ./frontend && npm install

#RUN pip3 install torch==1.10.2+cu113 torchvision==0.11.3+cu113 torchaudio==0.10.2+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html

RUN apt update && apt upgrade -y
RUN apt install software-properties-common -y
#RUN add-apt-repository ppa:deadsnakes/ppa 
RUN apt install python3.11 -y
RUN apt install python3-pip -y

RUN pip3 install poetry
RUN cd ./backend && poetry install

RUN pip3 install --upgrade nvidia-ml-py3==7.352.0
RUN pip3 install transformers
RUN pip3 install llama-index
RUN pip3 install --upgrade sentence-transformers==2.2.2
RUN pip3 install --upgrade accelerate==0.14.0
RUN pip3 install --upgrade codecarbon==2.1.4
RUN pip3 install --upgrade streamlit==1.14.0
RUN pip3 install --upgrade wget==3.2
RUN pip3 install --upgrade scikit-learn==1.1.3
RUN pip3 install --upgrade nltk==3.7
RUN pip3 install --upgrade stqdm==0.0.4
RUN pip3 install --upgrade datasets==2.6.1
RUN pip3 install --upgrade wandb==0.13.5 
RUN pip3 install pymilvus
RUN pip3 install milvus
RUN pip3 install fastapi
RUN pip3 install uvicorn
RUN pip3 install pypdf
RUN pip3 install python-dotenv
RUN pip3 install einops

RUN pip3 install https://download.pytorch.org/whl/cu113/torch-1.12.1%2Bcu113-cp310-cp310-linux_x86_64.whl#sha256=be682ef94e37cd3f0768b8ce6106705410189df2c365d65d7bc1bebb302d84cd


