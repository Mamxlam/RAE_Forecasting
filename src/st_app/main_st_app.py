import streamlit as st

# '''
# Here we redirect to the pages
# run streamlit run C:\Users\Nikolas\PycharmProjects\Master_Projects\web_mining_project_2_final\RAE_Forecasting\src\st_app\bouzi_main_streamlit.py
# '''
# ./st_app/pages/exploratory.py'
st.page_link('./pages/Exploratory.py',label='EDA', icon='📊')

st.page_link('./pages/Observatory.py',label='Observatory',icon='🔍')
st.page_link('./pages/Forecasting.py',label='Forecasting',icon='🔮')