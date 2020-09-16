python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
mkdir -p ~/.streamlit/
echo "[general]
email = \"tarasov@ucu.edu.ua\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml