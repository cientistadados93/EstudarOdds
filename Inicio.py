import streamlit as st

# Configuração da página
st.set_page_config(page_title="Meu Aplicativo de Análise Esportiva", layout="wide")

# Título da página
st.title("Bem-vindo ao Estudar Odds!")

# Introdução
st.markdown("""
Este aplicativo oferece análises de futebol e tênis baseadas em dados históricos e estatísticas avançadas. Use o menu lateral para navegar entre as funcionalidades.
""")

# Seção da Página 'Backtest Futebol'
st.header("Backtest Futebol")
st.markdown("""
Na página **Backtest Futebol**, você pode avaliar a performance de estratégias aplicadas a resultados passados, com base em métricas como:

- **Retorno de Estratégias:** Teste e otimize estratégias com base em dados históricos.

Essas análises são feitas para otimizar suas decisões futuras com base em estratégias bem testadas.
""")

# Seção da Página 'Futebol'
st.header("Análises de Futebol")
st.markdown("""
Na página **Futebol**, você encontrará análises detalhadas sobre:
- **Médias de Gols:** Verifique o desempenho ofensivo e defensivo de equipes.
- **Odds Históricas:** Explore padrões de odds e descubra tendências para futuros jogos.
- **Placares Frequentes:** Identifique os resultados mais comuns em diversas ligas.
- **Eficiência nas Finalizações:** Analise a eficácia das equipes em transformar finalizações em gols.

Essas informações ajudam a prever tendências e possíveis comportamentos em jogos futuros.
""")

# Seção da Página 'Partidas Futebol'
st.header("Previsão de Partidas de Futebol")
st.markdown("""
Na página **Partidas Futebol**, você pode prever resultados com base na **Distribuição de Poisson**:
- **Previsão de Gols:** Use as médias de gols para calcular a probabilidade de diferentes placares.
- **Poisson:** Esta técnica estatística estima as chances de uma equipe marcar 0, 1, 2 ou mais gols, com base em sua média histórica.

""")

# Seção da Página 'Tennis'
st.header("Análise de Partidas de Tênis")
st.markdown("""
Na página **Tennis**, você encontrará:

- **Odds de Partidas:** Veja como as odds evoluem e influenciam as previsões de resultados.

Use essas análises para tomar decisões mais informadas sobre apostas ou prever resultados de partidas de tênis.
""")

# Seção de Instruções
st.header("Como Usar")
st.markdown("""
1. **Use o menu lateral:** Navegue entre as páginas **Backtest Futebol**, **Futebol**, **Partidas Futebol** e **Tennis**.
2. **Analise os dados:** Utilize as ferramentas para uma análise profunda das partidas e odds.
3. **Faça previsões:** Baseie suas decisões nas previsões e análises oferecidas.

Aproveite a plataforma para insights detalhados em esportes!
""")
