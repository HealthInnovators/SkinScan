# chatbox-demo

## Installation

```bash
# Cloning the repository
git clone https://github.com/Zhongheng-Cheng/chatbox-demo
cd chatbox-demo

# [Optional] Creating virtual environment
python -m venv venv
source venv/bin/activate

# Download dependencies
pip install -r requirements.txt

# Setup Gemini API key
touch .env
# Enter your Google Gemini API Key in ".env" like this:
# GOOGLE_API_KEY="..."

# Run the project
python app.py
```