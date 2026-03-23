# Carregador GTFS

Plugin para QGIS focado na visualização técnica de redes de transporte a partir de arquivos ZIP de GTFS.

## 🚀 Funcionalidades Principais

- **Shapes Otimizados**: Agrupa viagens por `shape_id` para evitar centenas de linhas sobrepostas.
- **Inteligência de Paradas**: 
    - Lista todas as linhas que passam no ponto (`linhas`).
    - Identifica se o ponto é terminal (**ponto final**) de alguma linha.
    - Lista quais linhas terminam naquele local (`linhas_pf`).
- **Dados Financeiros**: Extrai preços de tarifa (`tarifa`) vinculados às rotas.
- **Interface Localizada**: Atributos em português (`linha`, `operador`, `destino`, `sentido`, `plataforma`, etc.).
- **Estilização Automática**: Aplica as cores oficiais das rotas e permite configuração de rótulos.

## 🛠 Instalação

1. Garanta que todos os arquivos do plugin estejam dentro de uma pasta chamada **`Carregador_GTFS`**.
2. Copie essa pasta para o diretório de plugins do QGIS de acordo com seu sistema:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

3. Reinicie o QGIS e ative em **Complementos** -> **Gerenciar e Instalar Complementos**.

## 📖 Uso

1. Use o menu **Complementos** -> **Carregar Shapes & Paradas GTFS**.
2. Selecione o ZIP do GTFS.
3. As camadas "Linhas" e "Paradas" serão criadas com todos os metadados.

## ⚙ Configuração de Rótulos

Os rótulos vêm desabilitados por padrão para manter o mapa limpo. Para habilitar, edite `gtfs_loader.py` e descomente as linhas indicadas com o comentário `# PARA DESATIVAR RÓTULOS...` (linhas **287** e **355**).

## ⚖ Licença

GNU GPL v3.
