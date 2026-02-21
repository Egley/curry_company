import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🏡")

#image_path = 'C:/Users/Égley/Repos/CDC 2.0/Python2.0/ciclo7/'

image = Image.open('logo.png')
st.sidebar.image(image, width=600)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Entrega mais rápida da cidade')
st.sidebar.markdown("""___""")

st.write('# Cury Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    
    ### Como utilizar esse Growth Dashboard?
    
    - Visão empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insigths de geolocalização.
    - Visão entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
    - Time de Data Science no Discord
        - @meigarom
    """)
