# Carregador GTFS

Plugin para QGIS que permite carregar formas (shapes) e paradas (stops) a partir de um arquivo ZIP de GTFS.

## Funcionalidades

- **Carregamento Automático**: Lê `shapes.txt`, `stops.txt`, `trips.txt`, `routes.txt` e `agency.txt` diretamente de um ZIP.
- **Geometria por Forma**: Consolida viagens por `shape_id` para evitar sobreposições desnecessárias.
- **Estilização Dinâmica**: Aplica automaticamente a cor da rota (`route_color`) às linhas.
- **Metadados Completos**: Atributos detalhados para linhas (operador, destino, sentido, tipo) e paradas (plataforma, tipo, estação pai, descrição).
- **Interface Intuitiva**: Diálogo simples para seleção do arquivo.

## Instalação

1. Baixe ou clone este repositório.
2. Copie a pasta `Carregador_GTFS` para o diretório de plugins do QGIS:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
3. Reinicie o QGIS.
4. Vá em **Complementos** -> **Gerenciar e Instalar Complementos** e ative o **Carregador GTFS**.

## Uso

1. Acesse o menu **Complementos** -> **Carregador GTFS** -> **Carregar Shapes & Paradas GTFS**.
2. Selecione o arquivo ZIP do GTFS.
3. Clique em **OK**.

## Licença

Este projeto está licenciado sob a [GNU GPL v3](LICENSE).
