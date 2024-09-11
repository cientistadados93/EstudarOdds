import streamlit as st
import pandas as pd

# Função para carregar dados CSV
@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    data['Score'] = data['FTHG'].astype(str) + 'x' + data['FTAG'].astype(str)
    return data

# Função para filtrar os dados por odds
def filter_data_by_odds(data, min_odds, max_odds, team_type):
    if team_type == 'Casa':
        filtered_data = data[(data['B365H'] >= min_odds) & (data['B365H'] <= max_odds)]
    else:
        filtered_data = data[(data['B365A'] >= min_odds) & (data['B365A'] <= max_odds)]
    return filtered_data

# Função para filtrar por ligas
def filter_data_by_leagues(data, selected_leagues):
    if 'Todas' in selected_leagues or not selected_leagues:
        return data
    else:
        filtered_data = data[data['Div'].isin(selected_leagues)]
        return filtered_data


# Função para filtrar por equipe
def filter_data_by_teams(data, selected_teams, team_type):
    if 'Todas' in selected_teams or not selected_teams:
        return data
    else:
        if team_type == 'Casa':
            filtered_data = data[data['HomeTeam'].isin(selected_teams)]
        else:
            filtered_data = data[data['AwayTeam'].isin(selected_teams)]
        return filtered_data


# Função para calcular estatísticas adicionais
def calculate_additional_stats(data, team_type):
    if team_type == 'Casa':
        goals_for = data['FTHG'].mean()
        goals_against = data['FTAG'].mean()
        shots_total = data['HS'].mean()
        shots_on_target = data['HST'].mean()
        corners = data['HC'].mean()
        shots_conceded_total = data['AS'].mean()
        shots_conceded_on_target = data['AST'].mean()
        corners_conceded = data['AC'].mean()
    else:
        goals_for = data['FTAG'].mean()
        goals_against = data['FTHG'].mean()
        shots_total = data['AS'].mean()
        shots_on_target = data['AST'].mean()
        corners = data['AC'].mean()
        shots_conceded_total = data['HS'].mean()
        shots_conceded_on_target = data['HST'].mean()
        corners_conceded = data['HC'].mean()

    finishing_efficiency = (shots_on_target / shots_total) * 100 if shots_total > 0 else 0
    shots_per_goal = shots_total / goals_for if goals_for > 0 else 0
    shots_ontarget_per_goal = shots_on_target / goals_for if goals_for > 0 else 0
    defensive_efficiency = (shots_conceded_on_target / shots_conceded_total) * 100 if shots_conceded_total > 0 else 0
    shots_conceded_per_goal = shots_conceded_total / goals_against if goals_against > 0 else 0
    shots_conceded_on_target_per_goal = shots_conceded_on_target / goals_against if goals_against > 0 else 0
    total_goals_mean = (goals_for + goals_against)
    total_corners_mean = (corners + corners_conceded)

    stats = {
        'Média de Gols Feitos': goals_for,
        'Média de Gols Sofridos': goals_against,
        'Média de Finalizações': shots_total,
        'Média de Finalizações no Gol': shots_on_target,
        'Eficiência de Finalização (%)': finishing_efficiency,
        'Média de Finalizações por Gol': shots_per_goal,
        'Médias de Finalizações No Gol Por Gol': shots_ontarget_per_goal,
        'Média de Escanteios': corners,
        'Média de Finalizações Sofridas': shots_conceded_total,
        'Média de Finalizações no Gol Sofridas':  shots_conceded_on_target,
        'Média de Escanteios Sofridos': corners_conceded,
        'Média de Chutes Sofridos por Gol': shots_conceded_per_goal,
        'Média de Chutes no Gol Sofridos por Gol': shots_conceded_on_target_per_goal,
        'Eficiência Defensiva (%)': defensive_efficiency,
        'Média de Gols Totais': total_goals_mean,
        'Médias de Escanteios Totais': total_corners_mean
    }
    return stats


# Função para contar os resultados
def count_results(data):
    total_games = len(data)
    home_wins = len(data[data['FTR'] == 'H'])
    draws = len(data[data['FTR'] == 'D'])
    away_wins = len(data[data['FTR'] == 'A'])

    results = {
        'Vitórias da Casa': {
            'Contagem': home_wins,
            'Porcentagem': (home_wins / total_games) * 100 if total_games > 0 else 0,
            'Odds Decimais': 1 / (home_wins / total_games) if home_wins > 0 else 0
        },
        'Empates': {
            'Contagem': draws,
            'Porcentagem': (draws / total_games) * 100 if total_games > 0 else 0,
            'Odds Decimais': 1 / (draws / total_games) if draws > 0 else 0
        },
        'Vitórias do Visitante': {
            'Contagem': away_wins,
            'Porcentagem': (away_wins / total_games) * 100 if total_games > 0 else 0,
            'Odds Decimais': 1 / (away_wins / total_games) if away_wins > 0 else 0
        },
    }
    return results

def count_score_frequencies(data):
    score_counts = data['Score'].value_counts().reset_index()
    score_counts.columns = ['Score', 'Frequência']
    score_counts['Porcentagem'] = (score_counts['Frequência'] / len(data)) * 100
    return score_counts

def criar_colunas_over_under_gols(data):
    # Criar a coluna 'Total Gols'
    data['Total Gols'] = data['FTHG'] + data['FTAG']
    
    # Criar colunas de Over e Under Gols de 0.5 até 7.5
    for over in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]:
        data[f'Over_{over}'] = (data['Total Gols'] > over).astype(int)
        data[f'Under_{over}'] = (data['Total Gols'] < over).astype(int)
    
    return data

def analisar_over_under_gols(data):
    resultados_over_under_gols = {}
    total_jogos = len(data)
    
    for over in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]:
        resultados_over_under_gols[f'Over_{over}'] = {
            'Ocorrência': data[f'Over_{over}'].sum(),
            'Frequência (%)': round(data[f'Over_{over}'].mean() * 100,2),
            'Odds': round(1 / data[f'Over_{over}'].mean(), 2) if data[f'Over_{over}'].mean() > 0 else 0
        }
        resultados_over_under_gols[f'Under_{over}'] = {
            'Ocorrência': data[f'Under_{over}'].sum(),
            'Frequência (%)': round(data[f'Under_{over}'].mean() * 100,2),
            'Odds': round(1 / data[f'Under_{over}'].mean(), 2) if data[f'Under_{over}'].mean() > 0 else 0
        }
    
    return resultados_over_under_gols

st.set_page_config(layout="wide")
st.title('Análise de Futebol Pré Live com Odds')
st.subheader('Dados das temporadas européias entre 2016-2024')

data = load_data('FootballData.csv')

# Sidebar
with st.sidebar:
    st.subheader('Filtre por Liga(s)')
    leagues = ['Todas'] + sorted(data['Div'].unique().tolist())
    selected_leagues = st.multiselect('Selecione uma ou mais ligas', leagues, default=['Todas'])

    st.subheader('Selecione o mando de campo da(s) equipe(s) analisada(s)')
    team_type = st.radio('Casa ou Visitante para análise', ['Casa', 'Visitante'], horizontal=True)

    st.subheader('Filtre por Equipe(s)')
    if 'Todas' in selected_leagues or not selected_leagues:
        teams = ['Todas'] + sorted(data['HomeTeam'].unique().tolist() if team_type == 'Casa' else data['AwayTeam'].unique().tolist())
    else:
        filtered_data_leagues = filter_data_by_leagues(data, selected_leagues)
        teams = ['Todas'] + sorted(filtered_data_leagues['HomeTeam'].unique().tolist() if team_type == 'Casa' else filtered_data_leagues['AwayTeam'].unique().tolist())

    selected_teams = st.multiselect('Selecione uma ou mais equipes', teams, default=['Todas'])

    st.subheader('Filtre por uma faixa de odds \n Odds de referência da BET 365')
    min_odds = st.number_input('Odd mínima', min_value=1.01, value=1.01)
    max_odds = st.number_input('Odd máxima', min_value=1.01, value=1000.0)

    
# Filtrando os dados
filtered_data = filter_data_by_leagues(data, selected_leagues)
filtered_data = filter_data_by_teams(filtered_data, selected_teams, team_type)
filtered_data = filter_data_by_odds(filtered_data, min_odds, max_odds,team_type)
results = count_results(filtered_data)
additional_stats = calculate_additional_stats(filtered_data, team_type)

# Função para exibir uma métrica com cores personalizadas
def colored_metric(label, value, color):
    value_display = f"{value:.2f}" if value is not None else "N/A"
    st.markdown(
        f"""
        <div style="text-align: center;background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <h5 style="color: white;font-size: 18px; margin-bottom: 5px;">{label}</h5>
            <p style="color: white; font-size: 22px; margin: 0;">{value_display}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def create_metric(title, value, frequency, odds, color):
    return f"""
    <div style="background-color: {color}; padding: 10px; border-radius: 5px; text-align: center;">
        <h3 style="font-size: 24px; margin: 0;">{title}</h3>
        <p style="font-size: 22px; margin: 5px 0;">{value} jogos</p>
        <p style="font-size: 22px; margin: 5px 0;">{frequency}</p>
        <p style="font-size: 22px; margin: 5px 0;">Odd: {odds}</p>
    </div>
    """

def display_score_results(score_counts):

    st.subheader('Frequências dos Resultados Corretos')

    # Cria colunas para exibir os resultados em uma grade horizontal
    num_cols = 5  # Número de colunas na grade
    num_rows = (len(score_counts) + num_cols - 1) // num_cols  # Calcula o número de linhas necessárias

    cols = st.columns(num_cols)  # Cria as colunas para exibir os resultados

    # Calcula a intensidade de cor com base na porcentagem máxima
    max_percentage = score_counts['Porcentagem'].max()

    for i in range(num_rows):
        for j in range(num_cols):
            index = i * num_cols + j
            if index < len(score_counts):
                score = score_counts.iloc[index]['Score']
                frequency = score_counts.iloc[index]['Frequência']
                percentage = score_counts.iloc[index]['Porcentagem']

                # Calcula a cor com base na porcentagem
                color_intensity = int((percentage / max_percentage) * 255)
                color = f'rgb({255 - color_intensity}, {color_intensity}, 0)'

                with cols[j]:
                    st.markdown(
                        f"""
                        <div style="text-align: center; background-color: {color}; color: white; width: 180px; height: 120px; 
                        text-align: center; justify-content: center; margin: 5px; font-size: 22px; border-radius: 10px; padding: 10px;">
                            <strong>{score}</strong><br>
                            <span style="font-size: 18px;">Frequência: {frequency}<br> {percentage:.2f}%</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# Exibir o total de jogos filtrados em uma métrica destacada
total_games = len(filtered_data)
st.markdown(f"""
    <div style="text-align: center; padding: 10px; background-color: #061c96; border-radius: 5px;">
        <h4 style="color: white;;font-size: 24px">Total de Jogos Filtrados</h4>
        <h1 style="color: white;; font-size: 35px;">{total_games}</h1>
    </div>
""", unsafe_allow_html=True)

# Exibir Resultados com uma apresentação melhorada
st.subheader("Resultados para Análise")

# Criar colunas para exibir os resultados horizontalmente
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div style="text-align: center; background-color: #061c96; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="color: white; margin-bottom: 5px;">Vitórias da Casa</h4>
            <p style="color: white; font-size: 24px; margin: 0;">{results['Vitórias da Casa']['Contagem']}</p>
            <p style="color: white;font-size: 20px; margin: 0;"> {results['Vitórias da Casa']['Porcentagem']:.2f}%</p>
            <p style="color: white;font-size: 20px; margin: 0;"> Odd Justa: {results['Vitórias da Casa']['Odds Decimais']:.2f}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="text-align: center;background-color:#061c96; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="color: white; margin-bottom: 5px;">Empates</h4>
            <p style="color: white; font-size: 24px; margin: 0;"> {results['Empates']['Contagem']}</p>
            <p style="color: white;font-size: 20px; margin: 0;"> {results['Empates']['Porcentagem']:.2f}%</p>
            <p style="color: white; font-size: 20px; margin: 0;"> Odd Justa: {results['Empates']['Odds Decimais']:.2f}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="text-align: center;background-color: #061c96; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <h4 style="color: white; margin-bottom: 5px;">Vitórias do Visitante</h4>
            <p style="color: white; font-size: 24px; margin: 0;"> {results['Vitórias do Visitante']['Contagem']}</p>
            <p style="color: white;font-size: 20px; margin: 0;">  {results['Vitórias do Visitante']['Porcentagem']:.2f}%</p>
            <p style="color: white;font-size: 20px; margin: 0;"> Odd Justa: {results['Vitórias do Visitante']['Odds Decimais']:.2f}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Exibir Métricas Ofensivas e Defensivas
st.subheader("Médias de Ataque e Defesa")

# Criar colunas para exibir as métricas ofensivas e defensivas verticalmente
col1, col2, col3 = st.columns([1, 1, 1])

# Ofensivas
with col1:
    st.markdown("**Ataque**")
    st.markdown("<div style='display: flex; flex-direction: column;'>", unsafe_allow_html=True)
    colored_metric("Média de Gols Feitos", additional_stats['Média de Gols Feitos'], "#04b846")
    colored_metric("Média de Finalizações", additional_stats['Média de Finalizações'], "#04b846")
    colored_metric("Média de Finalizações no Gol", additional_stats['Média de Finalizações no Gol'], "#04b846")
    colored_metric("Eficiência de Finalização (%) (no gol/total finalizações)", additional_stats['Eficiência de Finalização (%)'], "#04b846")
    colored_metric("Média de Finalizações para 1 Gol", additional_stats['Média de Finalizações por Gol'], "#04b846")
    colored_metric("Médias de Finalizações em  Gol para 1 Gol", additional_stats['Médias de Finalizações No Gol Por Gol'], "#04b846")
    colored_metric("Média de Escanteios a favor", additional_stats['Média de Escanteios'], "#04b846")
    st.markdown("</div>", unsafe_allow_html=True)

# Defensivas
with col2:
    st.markdown("**Defesa**")
    st.markdown("<div style='display: flex; flex-direction: column;'>", unsafe_allow_html=True)
    colored_metric("Média de Gols Sofridos", additional_stats['Média de Gols Sofridos'], "#FF6347")
    colored_metric("Média de Finalizações Sofridas", additional_stats['Média de Finalizações Sofridas'], "#FF6347")
    colored_metric("Média de Finalizações no Gol Sofridas", additional_stats['Média de Finalizações no Gol Sofridas'], "#FF6347")
    colored_metric("Eficiência de Finalização do Adversário (%) (no gol/total finalizações)", additional_stats['Eficiência Defensiva (%)'], "#FF6347")     
    colored_metric("Médias de Finalizações Sofridas para 1 Gol Sofrido", additional_stats['Média de Chutes Sofridos por Gol'], "#FF6347")
    colored_metric("Médias de Finalizações Sofridas em Gol para 1 Gol Sofrido", additional_stats['Média de Chutes no Gol Sofridos por Gol'], "#FF6347")
    colored_metric("Média de Escanteios contra", additional_stats['Média de Escanteios Sofridos'], "#FF6347")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("**Totais**")
    st.markdown("<div style='display: flex; flex-direction: column;'>", unsafe_allow_html=True)
    colored_metric("Média de Gols Totais", additional_stats['Média de Gols Totais'], "#4503ad")
    colored_metric("Médias de Escanteios Totais", additional_stats['Médias de Escanteios Totais'], "#4503ad")
    st.markdown("</div>", unsafe_allow_html=True)


# Calcular e exibir a tabela de resultados mais frequentes
score_counts = count_score_frequencies(filtered_data)
display_score_results(score_counts)

OverGolsdata = criar_colunas_over_under_gols(filtered_data)
resultados_over_under_gols = analisar_over_under_gols(OverGolsdata)

st.header('Análise de Over e Under Gols')

# Seção de Over Gols
st.subheader('Análise de Over Gols')
cols_over = st.columns(4)
for i, over in enumerate([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]):
    with cols_over[i % 4]:  # Distribuindo as colunas em múltiplas linhas
        color = "#04b846"  # Gradiente de cor
        st.markdown(create_metric(
            f"Over {over}",
            f"{resultados_over_under_gols[f'Over_{over}']['Ocorrência']}",
            f"{resultados_over_under_gols[f'Over_{over}']['Frequência (%)']}%",
            f"{resultados_over_under_gols[f'Over_{over}']['Odds']}",
            color
        ), unsafe_allow_html=True)

# Seção de Under Gols
st.subheader('Análise de Under Gols')
cols_under = st.columns(4)
for i, under in enumerate([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]):
    with cols_under[i % 4]:  # Distribuindo as colunas em múltiplas linhas
        color = "#FF6347"  # Gradiente de cor
        st.markdown(create_metric(
            f"Under {under}",
            f"{resultados_over_under_gols[f'Under_{under}']['Ocorrência']}",
            f"{resultados_over_under_gols[f'Under_{under}']['Frequência (%)']}%",
            f"{resultados_over_under_gols[f'Under_{under}']['Odds']}",
            color
        ), unsafe_allow_html=True)

# Exibir dados filtrados
st.subheader('Dados filtrados')
st.dataframe(filtered_data)

# Opção para download dos dados filtrados
st.subheader('Baixar dados filtrados')
csv = filtered_data.to_csv(index=False).encode('utf-8')
st.download_button(label="Baixar CSV", data=csv, file_name='dados_filtrados.csv', mime='text/csv')
