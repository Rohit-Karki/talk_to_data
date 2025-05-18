I have a requirement of running a LLM in remote server which will host a llama:70b model which will be conected from my local setup using langchain. The requirements of the llama:70b


```bash
$ sudo systemctl stop ollama
$ sudo rm $(which ollama)
$ sudo rm -rf /usr/share/ollama
$ sudo groupdel ollama
$ sudo userdel ollama
```

```bash
sudo curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama
sudo chmod +x /usr/bin/ollama
```

```bash
sudo nano /etc/systemd/system/ollama.service
```
Then save the file and start the ollama service.
```shell
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Environment="OLLAMA_HOST=0.0.0.0"
ExecStart=/usr/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
```

## 5. Start Ollama Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
```

## 6. Configure Firewall
```bash
sudo ufw allow 11434/tcp
sudo ufw reload
```

## 7. Test the Setup
From another machine:
```bash
curl -X POST http://YOUR_SERVER_IP:11434/api/generate -d '{
  "model": "codellama",
  "prompt": "Write me a function that outputs the fibonacci sequence"
}'
```

## Hardware Requirements
- For 70B models: Recommended 140GB+ RAM
- GPU: At least 80GB VRAM (A100 or similar)
- Storage: At least 140GB free space

## Note
Make sure your server has sufficient resources for the 70B model. The default memory requirements are:
- 7B models: 8GB RAM
- 13B models: 16GB RAM
- 33B models: 32GB RAM
- 70B models: 140GB RAM

```bash
ollama run codellama
```
or
For 13b model
```bash
ollama run codellama:13B
```

For testing the setup use 
```bash 
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "codellama",
  "prompt": "Write me a function that outputs the fibonacci sequence"
}'
```