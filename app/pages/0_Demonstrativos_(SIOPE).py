# IMPORTS/CONFIGURAÇÕES
# Bibliotecas de processamento de dados
import numpy as np
import pandas as pd
import datetime as dt
import base64
# Bibliotecas de visualização
import plotly.express as px
import streamlit as st
import warnings
# Configurações das bibliotecas
warnings.filterwarnings('ignore')
pd.options.display.float_format = '{:,.2f}'.format
pd.options.display.max_rows = None
pd.options.display.max_colwidth = None
st.set_page_config(
    page_title="INFO FUNDEB",
    page_icon=":material/edit:",
    layout='wide')
st.logo(r'Dados\Imagens\Logo-CACS-Fundeb.png')


# FUNÇÕES
def show_pdf(pdf_path, width=700, height=600):
    try:
        # Lê o conteúdo do PDF como bytes
        with open(pdf_path, 'rb') as file:
            pdf_bytes = file.read()

        # Codifica o PDF para base64
        pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        # Exibe o PDF usando um iframe embutido
        pdf_display = f'''<iframe src="data:application/pdf;base64,{pdf}" width="{
            width}" height="{height}" type="application/pdf"></iframe>'''
        st.markdown(pdf_display, unsafe_allow_html=True)
    except:
        st.error('Arquivo não encontrado.')


# SIDEBAR
with st.sidebar:
    st.write('# FILTROS')
    bimester = st.selectbox(
        "Bimestre",
        options=[str(int(m/2)) for m in range(13) if m % 2 == 0 and m != 0])
    report = st.selectbox(
        "Relatório",
        options=[f'RREO {bimester}B 2024 (SIOPE) RESUMIDO', f'RREO {bimester}B 2024 (SIOPE)', f'RREO {bimester}B 2024 (SIAFE)'])

# VARIÁVEIS
path = f'./Dados/SIOPE-RREO/{bimester} Bi/{report}.pdf'

# BODY
st.write(f'# {report}')
show_pdf(path, width=1000)
# st.feedback()
st.download_button(label='Download', data=path)
