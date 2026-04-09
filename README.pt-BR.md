# GTFS 2 GIS - Plugin QGIS (v1.1.1)

[English](README.md) | **Português**

[![QGIS Version](https://img.shields.io/badge/QGIS-3.40--4.0-green.svg)](https://qgis.org/) 
[![Version](https://img.shields.io/badge/version-1.1.1-blue.svg)](https://plugins.qgis.org/plugins/qgis_gtfs_plugin/)
[![License](https://img.shields.io/badge/License-GPL%20v3-red.svg)](LICENSE)

O **GTFS 2 GIS** é um plugin para QGIS desenvolvido para visualização e análise de redes de transporte público a partir de arquivos GTFS estáticos e feeds dinâmicos de GTFS-Realtime.

Versões suportadas do QGIS: **3.44 até 4.0**.

---

## 🚀 Funcionalidades Principais

- **Shapes Otimizados**: Agrupa viagens por `shape_id` para evitar linhas sobrepostas, com larguras de linha baseadas na frequência e cálculo automático de `shape_ext` (distância elipsoidal em metros).
- **Inteligência de Paradas**:
    - Lista todas as linhas que passam por um ponto.
    - Identifica terminais e quais linhas encerram ali.
    - Ícones por tipo de transporte (🚌 Ônibus, 🚇 Metrô, 🚄 Trem, ⛴️ Barca).
- **Dados Financeiros**: Extrai preços de tarifas vinculados às rotas.
- **Estilização Automática**: Aplica as cores oficiais das rotas definidas nos dados GTFS.
- **Painel de Analytics**: Dashboard com estatísticas (km totais, densidade de pontos, frotas, etc.).
- **Rastreamento GTFS-Realtime**: 
    - Visualização de veículos em tempo real a partir de feeds Protobuf.
    - Instalação automática de dependências (pip install protobuf).
    - URLs e intervalos de atualização customizáveis.
    - Rotação de ícones baseada no rumo (bearing) do veículo.
- **Filtro por Período**: Filtre linhas por horários (Pico Manhã, Entrepico, Pico Tarde, Noite).

---

## 🔧 Ferramentas de Análise

- **Mapa de Calor de Frequência**: Camadas graduadas pela intensidade da frequência.
- **Cobertura Populacional**: Calcula a população atendida em raios de caminhada (usando dados IBGE).
- **Desertos de Trânsito**: Identifica áreas populosas com pouco ou nenhum acesso a transporte.
- **Acessibilidade**: Cria buffers de 400m e análise de isócronas reais por rede viária.

---

## 🛠 Instalação

### Via Repositório Oficial do QGIS (Recomendado)
1. No QGIS, vá em **Plugins** -> **Gerenciar e Instalar Plugins**.
2. Procure por **"GTFS 2 GIS"** e clique em **Instalar**.

### Instalação Manual
1. Baixe o código deste repositório.
2. Certifique-se de que o conteúdo do plugin está dentro de uma pasta chamada `qgis_gtfs_plugin`.
3. Copie a pasta para o diretório de plugins do QGIS:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
    - **Windows (QGIS 4)**: `%APPDATA%\QGIS\QGIS4\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles\default\python\plugins\`
    - **Linux (QGIS 4)**: `~/.local/share/QGIS/QGIS4/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
    - **macOS (QGIS 4)**: `~/Library/Application Support/QGIS/QGIS4/profiles/default/python/plugins/`
4. Habilite o plugin no Gerenciador de Plugins.

---

## 📖 Como Usar

1. Vá em **Plugins** -> **GTFS 2 GIS** -> **Load GTFS...**.
2. Selecione um arquivo `.zip` de GTFS.
3. As camadas de linhas e pontos serão criadas com todos os metadados.
4. Abra o painel **GTFS Analytics** (`F7` ou pela Barra de Ferramentas).
5. Na seção **Real-Time Tracking**:
    - Se necessário, clique em **Install Dependencies** para configurar o Protobuf.
    - Insira a URL do feed GTFS-RT (ex: Belo Horizonte: `http://realtime4.mobilibus.com/web/4ch6j/vehicle-positions?accesskey=982a57efd77a9462bf1665696fb25984`).
    - Clique em **Start Tracking** para visualizar os veículos no mapa.

---

## 🤖 Desenvolvimento e CI/CD

Este projeto utiliza **GitHub Actions** para automação de publicação.
- Cada nova **Tag** (ex: `0.3.8`) dispara um workflow que valida os metadados e publica automaticamente no repositório oficial do QGIS.

Se desejar contribuir, sinta-se à vontade para abrir um **Pull Request** ou relatar bugs no [Issue Tracker](https://github.com/arrobaraujo/qgis_gtfs_plugin/issues).

---

## ⚖ Licença

GNU GPL v3.

Desenvolvido por **[Erick Araujo - @arrobaraujo](https://github.com/arrobaraujo)**.
