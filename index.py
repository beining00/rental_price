import streamlit as st

st.set_page_config(
    page_title="Apartment comparator",
    page_icon="🔥"
)


st.sidebar.title('Search Filters')
title = st.sidebar.text_input('Apartment Address')

if title:
    option=st.sidebar.selectbox('select graph',(title,'Karate', 'GOT'))

st.write("We are looking at " + title)
st.markdown('By <a href="https://willjobs.com" target="_blank">Will Jobs</a>' , unsafe_allow_html=True)