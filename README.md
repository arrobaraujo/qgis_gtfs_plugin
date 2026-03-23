# Carregador GTFS

Plugin para QGIS que permite carregar linhas e paradas a partir de um arquivo ZIP de GTFS, com foco em visualização limpa e dados enriquecidos.

## 🚀 Funcionalidades

- **Leitura Direta de ZIP**: Processa `shapes.txt`, `stops.txt`, `trips.txt`, `routes.txt`, `agency.txt`, `fare_attributes.txt` e `fare_rules.txt`.
- **Geometria Otimizada**: Agrupa dados por `shape_id` para evitar excesso de linhas sobrepostas.
- **Dados de Tarifas**: Inclui o preço da tarifa diretamente nos atributos das linhas.
- **Linhas por Parada**: Identifica e lista quais linhas atendem cada ponto de parada.
- **Estilização Automática**: Aplica as cores das rotas e permite configuração de rótulos.
- **Atributos em Português**: Campos como `linha`, `nome`, `operador`, `destino`, `sentido`, `tarifa` e `plataforma`.

## 🛠 Instalação

1. Baixe os arquivos do plugin.
2. Copie a pasta `Carregador_GTFS` para o diretório de plugins do QGIS:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
3. Reinicie o QGIS.
4. Ative o plugin em **Complementos** -> **Gerenciar e Instalar Complementos**.

## 📖 Como Usar

1. Acesse **Complementos** -> **Carregar Shapes & Paradas GTFS**.
2. Selecione o arquivo ZIP do seu GTFS.
3. O plugin gerará as camadas "Linhas" e "Paradas" automaticamente.

## ⚙ Configuração

Caso queira habilitar ou desabilitar os **rótulos automáticos**, edite o arquivo `gtfs_loader.py` e procure pelos comentários explicativos nas linhas **287** e **355**.

## ⚖ Licença

Este projeto está licenciado sob a [GNU GPL v3](LICENSE).
