FROM ubuntu

# Set work directory
RUN mkdir -p ./src
WORKDIR ./src
COPY . .

# Install basic dependencies
RUN apt update
RUN apt install nano -y
RUN apt install git -y
RUN apt install curl -y

# Install NodeJS
RUN apt install coreutils -y
RUN apt-get install -y ca-certificates curl gnupg && mkdir -p /etc/apt/keyrings && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN NODE_MAJOR=20 && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install nodejs -y
RUN apt-get install aptitude -y
RUN aptitude install npm -y
RUN npm install -g npm
RUN cd ./frontend && npm install

# Install Python
RUN apt update && apt upgrade -y
RUN apt install software-properties-common -y
RUN apt install python3.11 -y
RUN apt install python3-pip -y

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Install NodeJS dependencies
RUN npm install @fortaine/fetch-event-source @vercel/analytics rehype-highlight rehype-katex remark-breaks mermaid next-themes use-debounce emoji-picker-react