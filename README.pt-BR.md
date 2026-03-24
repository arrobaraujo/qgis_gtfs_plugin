# GTFS 2 GIS

[English](README.md) | **Português**

[![QGIS Version](https://img.shields.io/badge/QGIS-3.4+-green.svg)](https://qgis.org/) 
[![Version](https://img.shields.io/badge/version-0.3.4-blue.svg)](https://plugins.qgis.org/plugins/qgis_gtfs_plugin/)
[![License](https://img.shields.io/badge/License-GPL%20v3-red.svg)](LICENSE)

O **GTFS 2 GIS** é um plugin para QGIS desenvolvido para visualização e análise de redes de transporte público a partir de arquivos GTFS (General Transit Feed Specification).

---

## 🚀 Funcionalidades Principais

- **Shapes Otimizados**: Agrupa viagens por `shape_id` para evitar linhas sobrepostas, com larguras de linha baseadas na frequência.
- **Inteligência de Paradas**:
    - Lista todas as linhas que passam por um ponto.
    - Identifica terminais e quais linhas encerram ali.
    - Ícones por tipo de transporte (🚌 Ônibus, 🚇 Metrô, 🚄 Trem, ⛴️ Barca).
- **Dados Financeiros**: Extrai preços de tarifas vinculados às rotas.
- **Estilização Automática**: Aplica as cores oficiais das rotas definidas nos dados GTFS.
- **Painel de Analytics**: Dashboard em tempo real com estatísticas (km totais, densidade de pontos, frotas, etc.).
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
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles\default\python\plugins\`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
4. Habilite o plugin no Gerenciador de Plugins.

---

## 📖 Como Usar

1. Vá em **Plugins** -> **GTFS 2 GIS** -> **Load GTFS...**.
2. Selecione um arquivo `.zip` de GTFS.
3. As camadas de linhas e pontos serão criadas com todos os metadados.
4. Use o painel **GTFS Analytics** para filtros e ferramentas avançadas.

---

## 🤖 Desenvolvimento e CI/CD

Este projeto utiliza **GitHub Actions** para automação de publicação.
- Cada nova **Tag** (ex: `0.3.4`) dispara um workflow que valida os metadados e publica automaticamente no repositório oficial do QGIS.

Se desejar contribuir, sinta-se à vontade para abrir um **Pull Request** ou relatar bugs no [Issue Tracker](https://github.com/arrobaraujo/qgis_gtfs_plugin/issues).

---

## ⚖ Licença

GNU GPL v3.

Desenvolvido por **[Erick Araujo - @arrobaraujo](https://github.com/arrobaraujo)**.
