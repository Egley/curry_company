import plotly.express as px
from haversine import haversine
import plotly.graph_objects as go
import folium
import pandas as pd
import streamlit as st
from datetime import datetime
from datetime import date
from PIL import Image
from streamlit_folium import folium_static
st.set_page_config(
    page_title="Visão entregadores",
    page_icon="🛵",
    layout='wide')

#-------------------------------------------Funções------------------------------------------------
def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe:
        
        Tipos de limpeza:
        1.Remoção dos espaços
        2.Mudança do tipo da coluna de dados
        3.Remoção das Nan
        4.Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe"""
        
    #Removendo espaços
    df1.columns = df1.columns.str.strip()
    df1['ID'] = df1['ID'].str.strip()
    df1['Delivery_person_ID'] = df1['Delivery_person_ID'].str.strip()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].str.strip()
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].str.strip()
    df1['Weatherconditions'] = df1['Weatherconditions'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()
    df1['City'] = df1['City'].str.strip()

    #Removendo Nan#
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN'
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['City'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['Type_of_order'] != 'nan')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['Delivery_person_Ratings'] != 'nan')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    #Convertendo para tipo certo de dado#
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #Criando coluna de Semanas
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    #Limpando a coluna Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x:x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1
#_________________________________________________________________________________________________________________
def top_delivers (df1, top_asc):
    mais_rapidos = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
                        .groupby(['City','Delivery_person_ID'])
                        .mean().sort_values(['City','Time_taken(min)'],ascending=top_asc)
                        .reset_index())

    resultado = {}

    for cidade in mais_rapidos['City'].unique():
        resultado[cidade] = (
            mais_rapidos
            .loc[mais_rapidos['City'] == cidade,['Delivery_person_ID', 'Time_taken(min)']]
            .head(10)
        )

    return resultado
#__________________________________________________________________________________________________________________

#__________________________________________________________________________________________________________________
#VISÃO ENTREGADORES

#---------------------------------Início da estrutura lógica do código-----------------------------------------

#Importando dados
df = pd.read_csv('dataset/train.csv')

#Limpar o código
df1 = clean_code(df)

#-------------------------------------Barra Lateral-------------------------------------------------------
st.set_page_config(layout="wide")
st.title('Marketplace - Visão Entregadores')

#image_path = 'C:/Users/Égley/Repos/CDC 2.0/Python2.0/ciclo6/logo.png'

image=Image.open('logo.png')

st.sidebar.image (image, width=600)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Entrega mais rápida da cidade')
st.sidebar.markdown("""___""")

data = st.sidebar.slider(
    'Até qual data?',
    min_value=datetime(2022, 4, 11),
    max_value=datetime(2022,4,13),
    value=datetime(2022,4,13),
    format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

st.markdown(f'{data.strftime('%d-%m-%Y')}')

transito =st.sidebar.multiselect(
    'Qual o tipo de tráfego?',
    ['Jam','High','Medium','Low'],
    default=['Jam','High','Medium','Low'],)

st.sidebar.markdown("""___""")

clima = st.sidebar.multiselect(
    'Qual o clima?',
    ['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'],
    default=['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'])

st.sidebar.markdown("""___""")

st.sidebar.markdown('### Powered by Égley Rodrigues')

#Filtro de datas
linhas_selecionadas = df1['Order_Date'] < data
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de densidades
linhas_selecionadas = df1['Road_traffic_density'].isin(transito)
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(clima)
df1 = df1.loc[linhas_selecionadas,:]
#-------------------------------------Barra Lateral-------------------------------------------------------
#Layout no Streamlit

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Avaliações','Ranking'])

with tab1:
    with st.container():
        st.header('Métricas Gerais')

        col1,col2,col3,col4,col5 = st.columns(5, gap='xxsmall')
        #Quantidade de entregadores
        with col1:
            col1.metric(label='Qtd de entregadores únicos', value=df1.loc[:,'Delivery_person_ID'].nunique(), border=True)
            
        with col2:
        #Menor idade dos entregadores
            col2.metric(label='Menor Idade', value=df1.loc[:,'Delivery_person_Age'].min(), border=True)

        with col3:
        #Maior idade dos entregadores   
            col3.metric(label='Maior Idade', value=df1.loc[:,'Delivery_person_Age'].max(), border=True)

        with col4:
        #Melhor condição de veículo
            col4.metric(label='Melhor condição de veículo', value=df1.loc[:,'Vehicle_condition'].max(), border=True)

        with col5:   
        #Pior condição de veículo
            col5.metric(label='Pior condição de veículo', value=df1.loc[:,'Vehicle_condition'].min(), border=True)
          

        with st.container():
        #Avaliação média por entregador
            st.markdown("""___""")
            st.markdown('#### Avaliação média por entregador')
            avl_media = df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index()
            

            fig = px.histogram(avl_media,
                x='Delivery_person_Ratings',
                nbins=50,
                color_discrete_sequence=["#0EDAB8"])
            fig.update_traces(
                marker_line_color='black',
                marker_line_width=1)
            st.plotly_chart(fig,use_container_width=True)

with tab2:
    #Avalição média por tipo de tráfego
    with st.container():
        st.markdown('#### Avalição média por tipo de tráfego')
        avl_media = df1.groupby('Road_traffic_density')['Delivery_person_Ratings'].agg(AvaliaçãoM='mean', DesvioP='std').reset_index()

        fig = px.bar(avl_media, 
            x='Road_traffic_density', 
            y='AvaliaçãoM', 
            error_y='DesvioP',
            color_discrete_sequence=["#D82424"])
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
    #Avaliação média por condições climáticas    
        st.markdown("""___""")
        st.markdown('#### Avaliação média por condições climáticas')
        avl_media = df1.groupby('Weatherconditions')['Delivery_person_Ratings'].agg(AvaliaçãoM='mean', DesvioP='std').reset_index()

        fig = px.bar(avl_media, x='Weatherconditions',y='AvaliaçãoM',error_y='DesvioP',color_discrete_sequence=['pink'])
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    #Entregadores mais rápidos
    with st.container():
        st.markdown('#### Top 10 entregadores mais rápidos por cidade')
        tabelas = top_delivers (df1, top_asc=True)

        cols = st.columns(len(tabelas))
        
        for col, (cidade, tabela) in zip(cols, tabelas.items()):
            with col:
                st.subheader(cidade)
                st.dataframe(tabela) 
    
    with st.container():
    #Entregadores mais lentos
        st.markdown("""___""")
        st.markdown('#### Top 10 entregadores mais lentos por cidade')
        tabelas = top_delivers(df1, top_asc=False)

        cols = st.columns(len(tabelas))

        for col, (cidade, tabela) in zip(cols, tabelas.items()):
            with col:
                st.subheader(cidade)
                st.dataframe(tabela)
        


    

