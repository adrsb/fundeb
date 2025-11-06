# IMPORTS/CONFIGURAÇÕES
# Bibliotecas de processamento de dados
from Scripts.banks_utils import *
import numpy as np
import pandas as pd
import datetime as dt
import base64
# Bibliotecas de visualização
import plotly.express as px
import streamlit as st
import warnings
# Bibliotecas próprias
from Scripts.banks_utils import *
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

# SIDEBAR
with st.sidebar:
    st.selectbox(
        'Bimestre',
        options=[str(int(m/2)) for m in range(13) if m % 2 == 0 and m != 0])


# Dados
@st.cache_data
def load_data(opening_balance=16545059.40, path_banks='./Dados/Originais/Extratos/Conta_corrente', path_applications='./Dados/Originais/Extratos/Rendimentos'):
    df = banks_consolidation(
        opening_balance=opening_balance,
        path_banks=path_banks,
        path_applications=path_applications,
        year=2024)
    return df


# BODY
data = load_data()
balance = data.resample(rule='me')[['SALDO']].last()
fig = px.bar(
    title='SALDO FINAL MENSAL',
    data_frame=balance,
    x=balance.index-pd.DateOffset(months=1),
    y=balance.SALDO,
    text_auto='.4s',
    hover_data={'SALDO': ":,.2f"}
    # labels=['DATA', 'SALDO']
)
# fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='inside')
st.plotly_chart(fig)
st.write(balance)
st.write(data)
