import streamlit as st
import pandas as pd
import requests
import numpy as np
import seaborn as sns
from scipy.stats import poisson
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Funções para criar URLs
def url_link1(day_code):
    return f"https://www.soccerstats.com/matches.asp?matchday={day_code}&listing=1"

def url_link2(day_code):
    return f"https://www.soccerstats.com/matches.asp?matchday={day_code}&listing=2"

# Cabeçalho para requisições
header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# Função para ajustar a hora
def ajustar_hora(hora_str):
    try:
        if pd.isna(hora_str):
            return hora_str
        hora = datetime.strptime(hora_str, "%H:%M")
        hora_ajustada = hora - timedelta(hours=4)
        return hora_ajustada.strftime("%H:%M")
    except ValueError:
        return hora_str

@st.cache_data
def fetch_data(day_code):
    r1 = requests.get(url_link1(day_code), headers=header)
    r2 = requests.get(url_link2(day_code), headers=header)
    
    df1 = pd.read_html(r1.text)[8]
    df2 = pd.read_html(r2.text)[8]
    
    # Processamento dos dados
    df1 = df1[['Country', '2.5+', '1.5+', 'GA', 'GF', 'TG', 'GP', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'GP.1', 'TG.1', 'GF.1', 'GA.1', '1.5+.1', '2.5+.1']]
    df1.columns = ['Country','Over25_H','Over15_H','GolsSofridos_H','GolsMarcados_H','MediaGols_H','Jogos_H','Home','Hora','Away','Jogos_A','MediaGols_A','GolsMarcados_A','GolsSofridos_A','Over15_A','Over25_A']
    
    df2 = df2[['BTS', 'FTS', 'CS', 'W%', 'CS.1', 'FTS.1', 'BTS.1', 'W%.1']]
    df2.columns = ['BTTS_H','FTS_H','CS_H','%W_H','CS_A','FTS_A','BTTS_A','%W_A']
    
    allmatches = pd.concat([df1, df2], axis=1)
    allmatches = allmatches[['Country','Hora','%W_H','Home','Away','%W_A','Over15_H','Over25_H','Over15_A','Over25_A','BTTS_H','BTTS_A','GolsMarcados_H','GolsSofridos_H','GolsMarcados_A','GolsSofridos_A','MediaGols_H','MediaGols_A','Jogos_H','Jogos_A']]
    
    # Ajuste de hora
    allmatches['Hora'] = allmatches['Hora'].apply(ajustar_hora)

    return allmatches

def calcular_poisson(media, max_gols=5):
    x = np.arange(0, max_gols + 1)
    poisson_probs = np.exp(-media) * np.power(media, x) / np.array([np.math.factorial(i) for i in x])
    return poisson_probs


# Função para calcular a probabilidade usando Poisson
def poisson_prob(lam, k):
    return poisson.pmf(k, lam)

# Função para gerar o heatmap dos top placares
def gerar_heatmap_top_placares(home_avg, away_avg, home_team, away_team):
    match_probs = []
    for home_goals in range(6):  # Limite até 5 gols para cada time
        for away_goals in range(6):
            prob = poisson_prob(home_avg, home_goals) * poisson_prob(away_avg, away_goals)
            match_probs.append((home_goals, away_goals, prob))

    if match_probs:
        df_probs = pd.DataFrame(match_probs, columns=['HomeGoals', 'AwayGoals', 'Probability'])
        df_probs['HomeTeam'] = home_team
        df_probs['AwayTeam'] = away_team

        # Remover linhas com valores NaN (se houver)
        df_probs = df_probs.dropna()

        # Verificar se há dados após a remoção de NaN
        if not df_probs.empty:
            # Adicionar os 10 resultados mais prováveis
            top_results = df_probs.nlargest(10, 'Probability')

            # Criando o HTML para exibir os resultados
            st.subheader("Top 10 Resultados Mais Prováveis")
            rows = []
            max_prob = top_results['Probability'].max()
            min_prob = top_results['Probability'].min()
            for _, row in top_results.iterrows():
                prob = row['Probability']
                color_intensity = (prob - min_prob) / (max_prob - min_prob)  # Normalizar entre 0 e 1
                green_intensity = int(255 * color_intensity)  # Verde mais intenso para maior probabilidade
                red_intensity = int(255 * (1 - color_intensity))  # Vermelho mais intenso para menor probabilidade
                color = f'rgb({red_intensity}, {green_intensity}, 0)'  # Gradiente de vermelho para verde
                rows.append(f'<div style="background-color: {color}; color: black; padding: 10px; margin: 5px; border-radius: 5px; text-align: center; font-size: 22px;">'
                        f'{row["HomeGoals"]} x {row["AwayGoals"]}<br>'
                        f'<span style="font-size: 18px;">{prob:.2%}</span>'
                        f'</div>')
            
    

            # Exibir os resultados em uma grid
            grid_html = '<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;">' + ''.join(rows) + '</div>'
            st.markdown(grid_html, unsafe_allow_html=True)

            # Criando a matriz de probabilidades usando pivot_table
            pivot_table = df_probs.pivot_table(values='Probability', index='HomeGoals', columns='AwayGoals', fill_value=0)
            st.subheader(f"Probabilidade de Resultados para {home_team} vs {away_team}")


            # Plotando o heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(pivot_table, annot=True, fmt=".2%", cmap="RdYlGn", cbar_kws={'label': 'Probabilidade'})
            plt.xlabel(f'{away_team}')
            plt.ylabel(f'{home_team}')
            plt.gca().invert_yaxis()  # Inverter o eixo y
            st.pyplot(plt)
        else:
            st.error("Nenhuma combinação de resultados válida foi gerada.")
    else:
        st.error("Nenhuma combinação de resultados foi gerada.")


# Função para gerar o gráfico detalhado
def gerar_detalhes_jogo(hora, home_team, away_team, stats):
    return f"""
    <div style="font-size:24px; margin-bottom: 5px;">Horário da partida: {hora}</div>
        
    <div style="display: flex; justify-content: space-between; text-align: center;">
        <div style="width: 48%; padding: 10px; background-color: #061c96; border-radius: 5px; color: #fff;">
            <div style="font-size: 22px; font-weight: bold; margin-bottom: 5px;">{home_team}</div>
            <div></div>
            <div style="font-size: 20px;"><strong>Partidas:</strong> {stats['Jogos_H']}</div>
            <div style="font-size: 20px;"><strong>Média de Gols Marcados:</strong> {stats['GolsMarcados_H']}</div>
            <div style="font-size: 20px;"><strong>Média de Gols Sofridos:</strong> {stats['GolsSofridos_H']}</div>
        </div>
        <div style="width: 48%; padding: 10px; background-color: #061c96; border-radius: 5px; color: #fff;">
            <div style="font-size: 22px; font-weight: bold; margin-bottom: 5px;">{away_team}</div>
            <div></div>
             <div style="font-size: 20px;"><strong>Partidas:</strong> {stats['Jogos_A']}</div>
            <div style="font-size: 20px;"><strong>Média de Gols Marcados:</strong> {stats['GolsMarcados_A']}</div>
            <div style="font-size: 20px;"><strong>Média de Gols Sofridos:</strong> {stats['GolsSofridos_A']}</div>
        </div>
    </div>
    """

# Configuração da interface do Streamlit
st.header(" Análise de Partidas - Fonte: Soccer Stats")


team_type = st.radio('Considerar dados de Total na competição ou Casa/Visitante para análise', ['Total', 'Casa/Visitante'], horizontal=True)

if team_type == 'Total':
    # Checkboxes para selecionar o dia
        options = {
        "Hoje": 101,
        "Amanhã": 102,
        "3 Dias": 103,
        "4 Dias": 104,
        "5 Dias": 105
        }
elif team_type == 'Casa/Visitante':
     options = {
        "Hoje": 1,
        "Amanhã": 2,
        "3 Dias": 3,
        "4 Dias": 4,
        "5 Dias": 5
        }

selected_days = st.multiselect("Selecione o(s) dia(s):", options.keys())

if selected_days:
    all_data = pd.DataFrame()
    
    # Coleta dos dados para os dias selecionados
    for day in selected_days:
        data = fetch_data(options[day])
        all_data = pd.concat([all_data, data])
    
    # Seleção de país
    selected_country = st.selectbox("Selecione o país:", all_data['Country'].unique())
    
    if selected_country:
        country_data = all_data[all_data['Country'] == selected_country]
        
        # Adiciona uma coluna para seleção do jogo
        country_data['Selecionar'] = country_data.apply(lambda row: f"{row['Home']} vs {row['Away']}", axis=1)
        selected_game = st.selectbox("Selecione o jogo:", country_data['Selecionar'].unique())
        
        if selected_game:
            # Filtra os dados para o jogo selecionado
            selected_game_data = country_data[country_data.apply(lambda row: f"{row['Home']} vs {row['Away']}" == selected_game, axis=1)]
            
            if not selected_game_data.empty:
                game_info = selected_game_data.iloc[0]
                home_team = game_info['Home']
                away_team = game_info['Away']
                hora = game_info['Hora']

                game_info = game_info.fillna(0)                
                # Dados para a função de distribuição de Poisson
                stats = {
                    'Jogos_H': int(game_info['Jogos_H']),
                    'Jogos_A':int(game_info['Jogos_A']),
                    'GolsMarcados_H': game_info['GolsMarcados_H'],
                    'GolsSofridos_H': game_info['GolsSofridos_H'],
                    'GolsMarcados_A': game_info['GolsMarcados_A'],
                    'GolsSofridos_A': game_info['GolsSofridos_A']
                }
                
                # Geração dos detalhes do jogo
                st.subheader("Detalhes da Partida")
                markdown_text = gerar_detalhes_jogo(hora, home_team, away_team, stats)
                st.markdown(markdown_text, unsafe_allow_html=True)
                
                home_avg = (game_info['GolsMarcados_H']*0.75)+(game_info['GolsSofridos_A']*0.25)
                away_avg= (game_info['GolsMarcados_A']*0.75)+(game_info['GolsSofridos_H']*0.25)

                # Geração do heatmap e Top 10 placares
                top_placares_probs = gerar_heatmap_top_placares(
                    home_avg=home_avg,
                    away_avg=away_avg,
                    home_team = home_team,
                    away_team=away_team
                )
else:
    st.write("Por favor, selecione ao menos um dia.")
