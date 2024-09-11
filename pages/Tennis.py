import streamlit as st
import pandas as pd

# Carregar os dados do arquivo CSV
@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    return data

data = load_data('tennisdata.csv')

# Substituir vírgulas por pontos nas colunas de odds
data['B365W'] = data['B365W'].str.replace(',', '.')
data['B365L'] = data['B365L'].str.replace(',', '.')

# Converter as colunas de odds para tipo numérico
data['B365W'] = data['B365W'].astype(float)
data['B365L'] = data['B365L'].astype(float)

# Título da aplicação
st.subheader("Análise de Odds em Partidas de Tênis - ATP (2010-2023)")

# Sidebar para filtros
st.sidebar.header("Filtros de Odds")
odd_min = st.sidebar.number_input("Odd Mínima", min_value=1.01, value=1.01, step=0.1)
odd_max = st.sidebar.number_input("Odd Máxima", min_value=1.01, value=100.0, step=0.1)

# Filtrar os dados para vitórias e derrotas com base nas odds
filterVitorias = data[(data['B365W'] >= odd_min) & (data['B365W'] <= odd_max)]
filterDerrotas = data[(data['B365L'] >= odd_min) & (data['B365L'] <= odd_max)]

# Cálculo da frequência de vitórias e derrotas
vitorias = len(filterVitorias)
derrotas = len(filterDerrotas)

if odd_min == 1.01 and odd_max == 100.0:
    total_partidas = vitorias
    vitorias = 0
    derrotas= 0
else:
    total_partidas = vitorias + derrotas

# Calcular a porcentagem de vitórias e derrotas
if total_partidas > 0:
    vitorias_pct = (vitorias / total_partidas) * 100
    derrotas_pct = (derrotas / total_partidas) * 100

    # Calcular odd implícita para vitórias e derrotas
    odd_vitoria = 100 / vitorias_pct if vitorias_pct > 0 else 0
    odd_derrota = 100 / derrotas_pct if derrotas_pct > 0 else 0
else:
    vitorias_pct = derrotas_pct = 0
    odd_vitoria = odd_derrota = 0

# Exibir o total de partidas analisadas acima das colunas
st.markdown(f"""
    <div style='text-align: center;'>
        <div style='background-color: #f0f0f0; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h4 style='font-size: 22px; color: black;'>Total de Partidas Analisadas</h4>
            <p style='font-size: 22px; color: black;'>{total_partidas}</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Criar duas colunas para vitórias e derrotas
col1, col2 = st.columns(2)

# Exibir vitórias na primeira coluna
with col1:
    st.markdown(f"""
        <div style='background-color: green; padding: 20px; border-radius: 10px; margin-bottom: 10px; text-align: center;'>
            <h4 style='color: white;'>Vitórias</h4>
            <p style='font-size: 22px; color: white;'>{vitorias} ({vitorias_pct:.2f}%)</p>
            <p style='font-size: 22px; color: white;'>Odd: {odd_vitoria:.2f}</p>
        </div>
    """, unsafe_allow_html=True)

# Exibir derrotas na segunda coluna
with col2:
    st.markdown(f"""
        <div style='background-color: red; padding: 20px; border-radius: 10px; margin-bottom: 10px;text-align: center;'>
            <h4 style='color: white;'>Derrotas</h4>
            <p style='font-size: 22px; color: white;'>{derrotas} ({derrotas_pct:.2f}%)</p>
            <p style='font-size: 22px; color: white;'>Odd: {odd_derrota:.2f}</p>
        </div>
    """, unsafe_allow_html=True)
