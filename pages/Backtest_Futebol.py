import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Carregar os dados do CSV
@st.cache_data
def load_data():
    data = pd.read_csv('FootballData.csv')
    return data

data = load_data()

# Filtro de ligas (com opção "Todas")
ligas = ['Todas'] + list(data['Div'].unique())
ligas_selecionadas = st.sidebar.multiselect(
    'Selecione as Ligas', 
    options=ligas, 
    default='Todas'
)

# Lógica de seleção de ligas
if 'Todas' in ligas_selecionadas:
    data_filtrada = data
else:
    data_filtrada = data[data['Div'].isin(ligas_selecionadas)]

# Checkbox para aplicar filtro de aposta
aplicar_filtro_aposta = st.sidebar.checkbox('Aplicar filtro de aposta por tipo de equipe e odds')

if aplicar_filtro_aposta:
    tipo_aposta = st.sidebar.radio("Aposta em Equipe:", ('Casa', 'Visitante'))
    odd_min = st.sidebar.number_input('Odd Mínima', min_value=1.01, max_value=50.0, value=1.01)
    odd_max = st.sidebar.number_input('Odd Máxima', min_value=1.02, max_value=100.0, value=100.0)
    
    if tipo_aposta == 'Casa':
        data_filtrada = data_filtrada[(data_filtrada['B365H'] >= odd_min) & (data_filtrada['B365H'] <= odd_max)]
    elif tipo_aposta == 'Visitante':
        data_filtrada = data_filtrada[(data_filtrada['B365A'] >= odd_min) & (data_filtrada['B365A'] <= odd_max)]

# Cálculo da odd média com base nos valores de odd mínima e máxima inseridos
if aplicar_filtro_aposta:
    odd_media = (odd_min + odd_max) / 2
    st.sidebar.write(f"Odd Média Usada para Filtro: {odd_media:.2f}")

# --- Configurações de Backtest ---
st.sidebar.header('Configurações de Backtest')

# Tipo de aposta no mercado de Moneyline (1, X, 2)
mercado_aposta = st.sidebar.radio("Selecione a opção de aposta:", ('1 (Casa)', 'X (Empate)', '2 (Visitante)'))

# Banca inicial e unidade apostada
banca_inicial = st.sidebar.number_input('Banca Inicial', value=1000.0)
tipo_aposta_valor = st.sidebar.radio('Tipo de Valor Apostado:', ('Valor Fixo', 'Porcentagem da Banca'))
if tipo_aposta_valor == 'Valor Fixo':
    valor_aposta = st.sidebar.number_input('Valor da Aposta Fixa', value=10.0)
else:
    porcentagem_aposta = st.sidebar.slider('Porcentagem da Banca por Aposta', 1, 100, 10)
    valor_aposta = banca_inicial * (porcentagem_aposta / 100)

# Função para calcular o backtest
def calcular_backtest(data, mercado, banca_inicial, valor_aposta, valor_fixo=True):
    banca = banca_inicial
    total_apostas = 0
    apostas_ganhas = 0
    apostas_perdidas = 0
    evolucao_banca = [banca_inicial]  # Lista para registrar a evolução da banca

    for index, row in data.iterrows():
        odd = 0
        resultado = row['FTR']  # FTR: Full Time Result (H, D, A)
        
        # Definir a odd com base no mercado escolhido
        if mercado == '1 (Casa)':
            odd = row['B365H']
            aposta_vencedora = (resultado == 'H')  # H = vitória do time da casa
        elif mercado == 'X (Empate)':
            odd = row['B365D']
            aposta_vencedora = (resultado == 'D')  # D = empate
        elif mercado == '2 (Visitante)':
            odd = row['B365A']
            aposta_vencedora = (resultado == 'A')  # A = vitória do time visitante

        # Calcular o valor da aposta
        if not valor_fixo:  # Se for aposta percentual, recalcula a cada iteração
            valor_aposta = banca * (porcentagem_aposta / 100)

        # Realizar a aposta
        if aposta_vencedora:
            ganho = valor_aposta * (odd - 1)
            banca += ganho
            apostas_ganhas += 1
        else:
            banca -= valor_aposta
            apostas_perdidas += 1

        total_apostas += 1
        evolucao_banca.append(banca)  # Registrar a banca após cada aposta

    roi = round(((banca - banca_inicial) / banca_inicial) * 100, 2)
    return banca, total_apostas, apostas_ganhas, apostas_perdidas, roi, evolucao_banca

# Função para analisar a lucratividade por liga
def analisar_lucratividade_por_liga(data, mercado, banca_inicial, valor_aposta, valor_fixo=True):
    ligas = data['Div'].unique()
    resultados = []
    
    for liga in ligas:
        data_liga = data[data['Div'] == liga]
        banca_final, total_apostas, apostas_ganhas, apostas_perdidas, roi, evolucao_banca = calcular_backtest(
            data_liga, mercado, banca_inicial, valor_aposta, valor_fixo
        )
        resultados.append({
            'Liga': liga,
            'Banca Final': banca_final,
            'ROI': roi,
            'Apostas Ganhas': apostas_ganhas,
            'Apostas Perdidas': apostas_perdidas,
            'Zerou Banca': any(b <= 0 for b in evolucao_banca)
        })
    
    return pd.DataFrame(resultados)

# Função para estilizar a tabela de lucratividade
def estilizar_lucratividade(df_lucratividade):
    # Ordenar por ROI
    df_lucratividade = df_lucratividade.sort_values(by='ROI', ascending=False)
    
    # Função para aplicar o gradiente de cores
    def aplicar_gradiente(valor):
        if pd.isna(valor):
            return ''
        if valor >= 0:
            return f'background-color: rgba(0, 255, 0, {valor/100})'  # Verde
        else:
            return f'background-color: rgba(255, 0, 0, {-valor/100})'  # Vermelho

    # Aplicar duas casas decimais para os campos de ROI e Banca Final
    df_lucratividade = df_lucratividade.style.applymap(aplicar_gradiente, subset=['ROI', 'Banca Final']) \
        .format({'ROI': '{:.2f}', 'Banca Final': '{:.2f}'})

    return df_lucratividade

# Função para estilizar a tabela de ligas
def estilizar_ligas(df_ligas):
    df_ligas = df_ligas.sort_values(by='Banca Final', ascending=False)
    
    # Função para aplicar o gradiente de cores
    def aplicar_gradiente_banca(valor):
        if pd.isna(valor):
            return ''
        if valor >= banca_inicial:
            return f'background-color: rgba(0, 255, 0, {valor/banca_inicial})'  # Verde
        else:
            return f'background-color: rgba(255, 0, 0, {(banca_inicial-valor)/banca_inicial})'  # Vermelho
    
    df_ligas = df_ligas.round({'Banca Final': 2})
    return df_ligas.style.applymap(aplicar_gradiente_banca, subset=['Banca Final'])


# Função para plotar a distribuição das odds usando Plotly
def plot_distribuicao_odds(data):
    # Criar o DataFrame com as odds relevantes
    odds_df = data[['B365H', 'B365D', 'B365A']].melt(var_name='Tipo', value_name='Odds')

    # Plotar o histograma interativo com Plotly
    fig = px.histogram(odds_df, x='Odds', color='Tipo', 
                       nbins=30, title='Distribuição das Odds',
                       labels={'Odds': 'Odd', 'count': 'Frequência'})
    fig.update_layout(bargap=0.1)  # Ajusta o espaçamento entre as barras

    # Exibir no Streamlit
    st.plotly_chart(fig)


# Função para plotar o gráfico de dispersão entre odds e resultados
def plot_odds_vs_resultado(data):
    fig = px.scatter(data, x='B365H', y='FTR', color='FTR',
                     labels={'B365H': 'Odd Casa', 'FTR': 'Resultado'},
                     title='Odds de Vitória x Resultado')
    st.plotly_chart(fig)

# Função para plotar o gráfico de barras da lucratividade por liga
def plot_lucratividade_por_liga(df_lucratividade):
    fig = px.bar(df_lucratividade, x='Liga', y='Banca Final', color='ROI',
                 labels={'Liga': 'Liga', 'Banca Final': 'Banca Final'},
                 title='Lucratividade por Liga')
    st.plotly_chart(fig)

# --- Aplicar o Backtest ---
if st.button('Aplicar Backtest'):
    banca_final, total_apostas, apostas_ganhas, apostas_perdidas, roi, evolucao_banca = calcular_backtest(
        data_filtrada, mercado_aposta, banca_inicial, valor_aposta, valor_fixo=(tipo_aposta_valor == 'Valor Fixo')
    )
    
    # Exibição dos resultados com retângulos coloridos e fonte preta
    st.subheader('Resultados do Backtest')

    # Estilo dos retângulos com cor da fonte preta
    st.markdown(f"""
    <div style="background-color:#f0f0f0;color:black;padding:10px;border-radius:10px;margin-bottom:10px;">
        <strong>Banca Final:</strong> {banca_final:.2f}
    </div>
    <div style="background-color:#e0f7fa;color:black;padding:10px;border-radius:10px;margin-bottom:10px;">
        <strong>Total de Apostas:</strong> {total_apostas}
    </div>
    <div style="background-color:#c8e6c9;color:black;padding:10px;border-radius:10px;margin-bottom:10px;">
        <strong>Apostas Ganhas:</strong> {apostas_ganhas}
    </div>
    <div style="background-color:#ffcdd2;color:black;padding:10px;border-radius:10px;margin-bottom:10px;">
        <strong>Apostas Perdidas:</strong> {apostas_perdidas}
    </div>
    <div style="background-color:#ffecb3;color:black;padding:10px;border-radius:10px;margin-bottom:10px;">
        <strong>ROI:</strong> {roi:.2f}%
    </div>
""", unsafe_allow_html=True)


    # Mostrar a evolução da banca
    st.line_chart(evolucao_banca)

    df_lucratividade = analisar_lucratividade_por_liga(data_filtrada, mercado_aposta, banca_inicial, valor_aposta, valor_fixo=(tipo_aposta_valor == 'Valor Fixo'))
    
    # Tabela de lucratividade por liga
    plot_lucratividade_por_liga(df_lucratividade) 
    st.dataframe(estilizar_lucratividade(df_lucratividade))

    # Plotar gráficos adicionais
    st.subheader('Distribuição das Odds')
    plot_distribuicao_odds(data_filtrada)
