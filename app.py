import streamlit as st

from pipelines import used_vocabulary
from settings import root_path

text_sample = open(root_path+"/text_sample.txt", "r", encoding='utf8').read()

st.title('Vocabulary recommendation demo')

user_input = st.text_area("label goes here", text_sample)
print(user_input)

vocabulary = used_vocabulary(user_input)
print(vocabulary)

st.header("Used vocabulary")
st.table(vocabulary)
