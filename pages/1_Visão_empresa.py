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
    page_title="Visão empresa",
    page_icon="📊",
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

def order_metric(df1):
            """ Esta função tem a responsabilidade de:
        
        1.Contar o número de entregas por dia
        2.E mostrar em um gráfico de barras
        
        Input: Dataframe
        Output: Gráfico de barras"""
            df_aux = df1.loc[:,['ID','Order_Date']].groupby('Order_Date').count().reset_index()
            fig = px.bar(df_aux, x='Order_Date', y='ID',color_discrete_sequence=['#FF93A5'])
            
            return fig

def traffic_order_share(df1):
            """ Esta função tem a responsabilidade de:
        
        1.Calcular a quantidade de entregas por tipo de trânsito
        2.Calculo dp percentual
        3.Gráfico de pizza
        
        Input: Dataframe
        Output: Dataframe"""
            
            df_aux = df1.loc[:,['ID','Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux['percentual_entregas'] = df_aux['ID']/ df_aux ['ID'].sum()
            fig = px.pie(df_aux, values='percentual_entregas', names='Road_traffic_density',color_discrete_sequence=['pink','black'])

            return fig

def traffic_order_city(df1):
            """ Esta função tem a responsabilidade de:
               
        1.Calcular o número de entregas por cidade e por densidade de trânsito
        2.Mostra em um gráfico de barras agrupadas
        
        Input: Dataframe
        Output: Gráfico de barras"""
            
            df_aux = df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
            fig = px.bar(df_aux, x='City', y='ID', color='Road_traffic_density', barmode='group',labels={'City': 'Cidades','ID': 'Volume de pedidos','Road_traffic_density': 'Densidades de Tráfego'},color_discrete_sequence=["#E29ACA",'#FF3355',"#FFFFFF","#333333"] )
            
            return fig

def order_by_week(df1):
            """ Esta função tem a responsabilidade de:
        
        1.Criar uma coluna de semanas
        2.Calcular quantas entregas foram feitas por semana
        3.Mostrar em um gráfico de linhas

        Input: Dataframe
        Output: Gráfico de linhas"""
            df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
            df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
            fig = px.line(df_aux, x='week_of_year', y='ID',color_discrete_sequence=['pink'])
            
            return fig

def order_share_by_week(df1):
            """ Esta função tem a responsabilidade de:
        
        1.Calcular a quantidade de entregas por semana
        2.Calcular quantos entregadores únicos tem por semana
        3.Unir os dois dataframes
        4.Criar uma coluna contendo o resultado da quantidade de entregas por semana / quantos entregadores únicos tem por semana
        5.Mostrar em um gráfico de linhas
        
        Input: Dataframe
        Output: Gráfico de linhas"""
            df_aux1 = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
            df_aux2 = df1.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
            df_aux = pd.merge(df_aux1,df_aux2, how='inner')
            df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
            fig = px.line(df_aux, x='week_of_year', y='order_by_delivery',color_discrete_sequence=['#FF3355'])
            
            return fig

def country_maps(df1):
            """ Esta função tem a responsabilidade de:
        
        1.Calcular a mediana das coordenadas dos locais centrais de entrega
        2.Agrupando por cidade e tipo de densidade de trânsito
        3.E mostrar em um mapa com os pontos dos locais no mapa
    
        
        Input: Dataframe
        Output: Gráfico de linhas"""
            df_aux = df1.loc[:,['City','Road_traffic_density','Delivery_location_longitude','Delivery_location_latitude']].groupby(['City','Road_traffic_density']).median().reset_index()

            m = folium.Map()

            for i in range(len(df_aux)):
                folium.Marker([df_aux.loc[i,'Delivery_location_latitude'], df_aux.loc[i,'Delivery_location_longitude']]).add_to (m)
            
            folium_static(m, width=1300, height=600)

            return None
#=======================================================================================================#

#---------------------------------Início da estrutura lógica do código-----------------------------------------

#Importando dados
df = pd.read_csv('dataset/train.csv')

#Limpar o código
df1 = clean_code(df)

# ====================================================================================
#Barra lateral no Streamlit (código do streamlit)
# ====================================================================================

st.title('Marketplace - Visão Empresa')

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

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""___""")

weatherconditions_options = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    ['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'],
    default=['conditions Cloudy','conditions Fog', 'conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'])

st.sidebar.markdown("""___""")

city_options = st.sidebar.multiselect(
    'Quais as regiões?',
    ['Urban','Semi-urban','Metropolitian'],
    default=['Urban','Semi-urban','Metropolitian'])
    
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

#Filtro de Cidade
linhas_selecionadas = df1['City'].isin(city_options)
df1 = df1.loc[linhas_selecionadas,:]

# ====================================================================================
#Layout no Streamlit (código do streamlit)
# ====================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        # Order metric        
        st.markdown('#### Quantidade de pedidos por dia')
        fig= order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)        
        
    with st.container():
        # Traffic Order Share        
        st.markdown("""___""")
        st.markdown('#### Distribuição de pedidos por tipo de tráfego')
        fig= traffic_order_share(df1)
        st.plotly_chart(fig, use_container_width=True)
                            
    with st.container():
        # Traffic Order City
        st.markdown("""___""")
        st.markdown('#### Volume de pedidos por cidade e tipo de tráfego')
        fig = traffic_order_city(df1)       
        st.plotly_chart(fig, use_container_width=True)
        
with tab2:
    with st.container():
        # Order by week
        st.markdown('#### Quantidade de pedidos por semana')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        # Order Share by week
        st.markdown("""___""")
        st.markdown('#### Quantidade de pedidos por entregador por semana')
        fig= order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
               
with tab3:
    with st.container():
        # Country Maps
        st.markdown('#### Localização central de cada cidade por tipo de tráfego')
        country_maps(df1)
        
        

