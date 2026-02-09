# Análise de Grupo WhatsApp - Cedros

Visualização interativa em D3.js e análise de dados sobre padrões de conversas do grupo de WhatsApp.

## Funcionalidades

- **Mapa de Calor**: Visualização Hora × Dia da semana
- **Análise Temporal**: Padrões horários, diários e mensais
- **Ranking de Participantes**: 40 membros ordenados por atividade
- **Gráficos Interativos**: Tooltips com estatísticas detalhadas

## Capturas de Ecrã

![Pré-visualização do Dashboard](docs/preview.png)

## Como começar

### Pré-requisitos

- Python 3.x (para servidor local)
- Navegador moderno
- Exportação de chat WhatsApp (formato CSV)

### Execução local

1. Clonar o repositório:

    ```bash
    git clone https://github.com/AlexandreXavier/analysis-whatsapp.git
    cd analysis-whatsapp
    ```

2. Colocar o CSV exportado como `../w.csv` (diretório pai)

3. Iniciar um servidor local:

    ```bash
    python -m http.server 8000
    ```

4. Abrir no navegador: `http://localhost:8000/activity-visualization.html`

## Formato de Dados

Formato CSV esperado:

```csv
date (YYYY-MM-DD),time (hh:mm),name,text
22-02-18,20:22,John Doe,"Hello everyone!",
```

## Ficheiros

- `activity-visualization.html` - Dashboard interativo principal em D3.js
- `whatsapp_analysis.ipynb` - Notebook Jupyter com análise em Python
- `CLAUDE.md` - Orientações de desenvolvimento para assistentes de IA

## Principais Conclusões

- **9 470 mensagens** de **40 participantes** ao longo de ~4 anos
- **Pico de atividade**: Hora de almoço (13:00) e terças-feiras
- **Top 10 contribuintes** representam ~70% das mensagens
- Cultura do grupo: Parabéns e cumprimentos calorosos ("abraço")

## Tecnologias

- D3.js v7 para visualizações
- Pandas para análise de dados
- JavaScript puro (sem frameworks)
- Pytest para testes do agregador

## Privacidade

Projeto concebido para uso pessoal. O `.gitignore` exclui:

- Ficheiros CSV com dados pessoais
- Capturas com informação privada
- Quaisquer ficheiros com números de telefone ou nomes

## Licença

Licença MIT

## Testes

1. Criar e ativar um ambiente Python (opcional, mas recomendado).
2. Instalar dependências mínimas:

    ```bash
    pip install pytest
    ```

3. Executar os testes:

    ```bash
    pytest
    ```
