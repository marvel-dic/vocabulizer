mkdir -p ~/.streamlit/
echo "[general]
email = \"tarasov@ucu.edu.ua\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml