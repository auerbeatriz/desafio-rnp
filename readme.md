# Introdução

Autora: Beatriz Auer Mariano

Esse repositório foi criado com o objetivo de estudar o uso de aprendizado de máquina para engenharia de tráfego de redes de computadores. Utilizamos o dataset com dados de redes reais disponibilizado pela RNP.

A descrição do desafio pode ser acessada atráves [desse link](https://drive.google.com/file/d/1EQm_2uubv6H1QxpNis8rYSrRCWaVkX4E/view?pli=1).

# Descrição do Problema

# Hipótese

# Descrição do dataset

# Esse repositório

Dentro de `analysis/rj/rj-es` estão os arquivos com dados tratados obtidos do dataset. Estão listados:

- Topologia da rede, tanto em .png quanto em .gml
- Relatório sobre o caminho analisado, contendo:

  - Número de nós e arestas na subtopologia analisada
  - Número de caminhos possíveis e medidos (que temos dados) na subtopologia
  - Descrição dos caminhos medidos (número de saltos, ip dos nós, quantidade de dados obtidos)
  - Estatísticas de latência para cada caminho medido
  - Listagem de todos os nós na subtopologia

- Latência medida em cada caminho por timestamp (latency.json)

  (!) Apenas 1 caminho foi medido em cada timestamp

- Matriz de latência em todos os caminhos ao longo do tempo

- Matriz de latência em todos os caminhos ao longo do tempo com dados faltantes preenchidos com interpolação temporal (pandas.interpolation() - interpolação linear)

- Outros arquivos de medidas de latências do caminho para análise auxiliar