import streamlit as st

from pipelines import used_vocabulary
from settings import root_path

from scipy.spatial.distance import hamming


def sort_vocabulary_by_similarity(voc_df):
    sorted_idx = list(voc_df.index)
    for i in range(1, len(sorted_idx)):
        best_j = i
        best_distance = float("inf")
        for j in range(i, len(sorted_idx)):
            distance = hamming(sorted_idx[i - 1][0], sorted_idx[j][0])
            if distance < best_distance:
                best_j = j
                best_distance = distance
        sorted_idx[i], sorted_idx[best_j] = sorted_idx[best_j], sorted_idx[i]
    return voc_df.loc[sorted_idx, :]


text_sample = open(root_path+"/text_sample.txt", "r", encoding='utf8').read()

st.title('Vocabulary recommendation demo')

user_input = st.text_area("label goes here", text_sample)
print(user_input)

vocabulary = used_vocabulary(user_input)
if st.checkbox("Sort results by similarity"):
    vocabulary = sort_vocabulary_by_similarity(vocabulary)

print(vocabulary)

st.header("Used vocabulary")
st.table(vocabulary)
