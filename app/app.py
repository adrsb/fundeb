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


# BODY
st.write("# Bem vindo(a)!")
st.write(
    '''Este aplicativo divulga informações de caráter financeiras e contábeis relativas FUNDEB, além disso, disponibilizará
    todos os dados originais disponibilizadas pela secretaria de educação dos estado do Amapá e os dados processados para as devidas informações.''')
st.write('As informações serão subdivididas em "Financeiro", "Contábil" e "Folha".')
