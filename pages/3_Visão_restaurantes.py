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
import numpy as np
st.set_page_config(
    page_title="Visão restaurante",
    page_icon="🍽️",
    layout='wide')





#---------------------------------------------------------------------------------------------------------

#Funções
#=======================================================================================================#
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
#____________________________________________________________________________________________________________
def medium_distance(df1):
    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['distance'] = df1.loc[:,cols].apply( lambda x: haversine(( x['Restaurant_latitude'] , x['Restaurant_longitude'] ) , ( x['Delivery_location_latitude'], x['Delivery_location_longitude'] )),axis=1 )
    
    avg_distance = df1['distance'].mean()
    

    return avg_distance
#____________________________________________________________________________________________________________
def time_festival(df1, tem_festival, op):
    cols = ['Time_taken(min)','Festival']
    df_aux = df1.loc[:, cols].groupby( 'Festival' ).agg({'Time_taken(min)':[op]})
    df_aux.columns = ['avg_std']
    df_aux = df_aux.reset_index()
    linhas = df_aux['Festival'] == tem_festival
    df_aux = df_aux.loc[linhas,:]
    results = df_aux['avg_std'].values[0]

    return results
#____________________________________________________________________________________________________________
def time_delivery_city_avg(df1):
    cols = ['City','Time_taken(min)']
    df_aux = df1.loc[:, cols].groupby( 'City' ).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['tempo_medio','tempo_desvioP']
    df_aux = df_aux.reset_index()

    fig = px.bar(df_aux, 
                x='City', 
                y='tempo_medio', 
                error_y='tempo_desvioP',
                color_discrete_sequence=['#00CCAA'])
    
    return fig
#____________________________________________________________________________________________________________
def avg_delivery_time(df1):  
    cols = ['City','Time_taken(min)','Type_of_order']
    df_aux = df1.loc[:, cols].groupby( ['City','Type_of_order'] ).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['tempo_medio','tempo_desvioP']
    df_aux = df_aux.reset_index()

    fig = px.scatter(df_aux,x='City',y='Type_of_order',size='tempo_medio',color='tempo_desvioP')
    return fig
#____________________________________________________________________________________________________________
def time_avg_del_city_traffic(df1):
    cols = ['City','Time_taken(min)','Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby( ['City','Road_traffic_density'] ).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['tempo_medio','tempo_desvioP']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values='tempo_medio',
                    width=600,
                    height=600,
                    color='tempo_desvioP', color_continuous_scale=["#00967D","#00CCAA","#FF93A5","#FF3355"],
                    color_continuous_midpoint=np.average(df_aux['tempo_desvioP']))
    return fig

#VISÃO RESTAURANTES

#=======================================================================================================#

#---------------------------------Início da estrutura lógica do código-----------------------------------------
#--------------------------------------------Barra lateral-----------------------------------------------------

#Importando dados
df = pd.read_csv('dataset/train.csv')


#Limpar o código
df1 = clean_code(df)

st.header('Marketplace - Visão Restaurantes')

#image_path = 'C:/Users/Égley/Repos/CDC 2.0/Python2.0/ciclo6/logo.png'
image= Image.open('logo.png')
st.sidebar.image( image, width=500)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Entrega mais rápida da cidade')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 13),
    value=datetime(2022, 4, 13),
    format='DD-MM-YYYY'
)

st.markdown(f'{date_slider.strftime('%d-%m-%Y')}')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")

weatherconditions_options = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    ['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'],
    default=['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('##### Powered by Égley Rodrigues')

#Filtro de datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de densidades
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(weatherconditions_options)
df1 = df1.loc[linhas_selecionadas,:]

#Layout no Streamlit

tab1, tab2 = st.tabs(['Visão Gerencial','Visão Tática'])

with tab1:
    with st.container():
        st.subheader('Métricas Gerais')
        col1, col2 = st.columns(2, gap="xsmall", border=True)
        with col1:
            #Quantidade de entregadores (cartões)
            delivery_unique = df1.loc[:,'Delivery_person_ID'].nunique()
            col1.metric('Entregadores', delivery_unique)

        with col2:
            #Distancia média (cartões)
            avg_distance = medium_distance(df1)
            col2.metric(label="Distância média de entrega",value=f"{avg_distance:.2f} km")        
        
    with st.container():
        col1, col2 = st.columns(2, gap='xsmall', border=True)
        with col1:
            #Tempo no festival (cartões)
            tempo = time_festival(df1, 'Yes', op='mean' )
            col1.metric(label='Tempo médio de entrega no Festival', value=f"{tempo:.0f} min")
            
            #Desvio padrão (Tempo no festival) (cartões)
            df_aux = time_festival(df1,'Yes', op='std')
            col1.metric(label='Desvio Padrão (Festival)', value=f"{df_aux:.2f}")

        with col2: 
            #Tempo no festival (cartões)
            tempo = time_festival(df1, 'No', op='mean' )
            col2.metric(label='Tempo médio de entrega sem Festival', value=f"{tempo:.0f} min")
            
            #Desvio padrão (Tempo no festival) (cartões)
            df_aux = time_festival(df1,'No', op='std')
            col2.metric(label='Desvio Padrão (Sem Festival)', value=f"{df_aux:.2f}")
            

    with st.container():#tempo médio de entrega por cidade e desvio padrão
        st.markdown("""___""")
        st.markdown('#### Tempo de entrega por cidade e desvio padrão')
        fig = time_delivery_city_avg(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():#Tempo médio de entrega por cidade e tipo de pedido e desvio padrão (barra com linha de erro)
        st.markdown('#### Tempo médio de entrega por cidade e tipo de pedido e desvio padrão')
        fig = avg_delivery_time(df1)
        st.plotly_chart(fig,use_container_width=True)

    with st.container():#Tempo médio de entrega por cidade e tipo de tráfego e desvio padrão (raio de sol)
        st.markdown('#### Tempo médio de entrega por cidade e tipo de tráfego e desvio padrão')
        fig = time_avg_del_city_traffic(df1)
        st.plotly_chart(fig, use_container_width=True)

        
        
        
