mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"tarasov@ucu.edu\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\