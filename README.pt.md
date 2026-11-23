# Lisboa Subterrânea 3D

[English](README.md) · **Português**

Uma vista 3D interativa do que existe debaixo de Lisboa: o metro, a ferrovia e galerias históricas, desenhados sob o relevo e os edifícios da cidade. Feito por curiosidade pelo desenho urbano, para partilhar com quem se interessa por perceber como a cidade funciona abaixo do nível da rua.

**Experimente online: <https://rob-sss.github.io/lisbon-underground-3d/?lang=pt>** ([English version](https://rob-sss.github.io/lisbon-underground-3d/?lang=en))

Ou descarregue `lisbon-underground-3d.html` e abra-o em qualquer navegador. Funciona sem ligação à Internet: sem servidor, sem instalação, sem conta.

A página está disponível em português europeu e em inglês. Segue o idioma do navegador; use o botão **PT / EN** (canto superior direito) para mudar, ou acrescente `?lang=pt` ou `?lang=en` ao endereço. Acrescente `&buildings=1` para abrir a página com os edifícios já ligados, por exemplo <https://rob-sss.github.io/lisbon-underground-3d/?lang=pt&buildings=1>.

## O que contém

- As 4 linhas do Metropolitano de Lisboa e as suas 50 estações, construídas a partir de dados abertos oficiais
- Relevo interpolado a partir de amostras de cota do EU-DEM
- Cerca de 52 000 edifícios do OpenStreetMap, com as suas alturas (desligados de início: toque em **Edifícios (OSM)** para os carregar)
- Camadas que se podem ligar e desligar: metro, ferrovia, aqueduto (Galeria do Loreto), Galerias Romanas, túneis de drenagem
- Um controlo de exagero vertical e um modo de **escala real (1:1)**
- Toque ou clique em qualquer elemento para ver os detalhes

## Leia isto antes de usar

Isto é um **esquema didático, não um levantamento topográfico**.

- **As profundidades são estimativas, não medições.** Não foi encontrado nenhum conjunto de dados aberto com a profundidade dos túneis do metro, por isso as profundidades das estações em `data/depths.json` são estimativas grosseiras feitas para este esquema, sem base em nenhuma fonte. Servem apenas para dar à vista 3D uma forma plausível. As profundidades das camadas desenhadas à mão também são estimativas.
- **Relevo aproximado.** A cota é amostrada a cada cerca de 1,4 km, mais a altitude de cada uma das 50 estações, e depois interpolada. Os pormenores pequenos (por exemplo, o vale da Baixa) ficam suavizados. O EU-DEM é um modelo de *superfície*, por isso inclui edifícios e vegetação.
- **A altura dos edifícios é muitas vezes estimada.** Cerca de 18% dos edifícios têm altura no OpenStreetMap e cerca de 18% têm número de pisos (contados como 3 m cada). Para os restantes ~64%, a altura é uma estimativa: 12 m, ou 3 m para estruturas pequenas como garagens e quiosques. Toque num edifício para ver qual é o caso. Os pátios interiores aparecem preenchidos e faltam os edifícios mapeados depois da data de descarga.
- **Camadas desenhadas à mão.** A ferrovia, o aqueduto, as Galerias Romanas e os túneis de drenagem (TMSA, TCB) são traçados aproximados, desenhados à mão (`data/hand_drawn_layers.json`).

Não o use para decisões de projeto, escavação ou segurança.

## Fontes dos dados e licenças

Verificadas a 22 de novembro de 2026. Volte a confirmar antes de reutilizar os dados.

| Dados | Fonte | Licença |
|---|---|---|
| Posição das 50 estações | Câmara Municipal de Lisboa, Lisboa Aberta, conjunto de dados "Estações de Metro" (recurso GeoJSON `POITransportes`): <https://dadosabertos.cm-lisboa.pt/dataset/estacoes-de-metro> | Creative Commons CC0 (indicada na página do recurso) |
| Ordem e traçado das linhas | GTFS do Metropolitano de Lisboa, cópia no Zenodo: <https://zenodo.org/records/18830433> | CC0 1.0 (autor: Metropolitano de Lisboa, E.P.E.). Nota: a cópia no Zenodo é de 2019 |
| Cotas do terreno | EU-DEM v1.1, 25 m (Copernicus Land Monitoring Service, Comissão Europeia), consultado através da API pública Open Topo Data: <https://www.opentopodata.org> | Acesso livre e aberto, com obrigação de citar a fonte (ver abaixo) |
| Edifícios (contornos, alturas, número de pisos, nomes) | © contribuidores do OpenStreetMap, descarregados através da API Overpass a 23 de novembro de 2026: <https://www.openstreetmap.org> | [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/), com atribuição obrigatória: ver <https://www.openstreetmap.org/copyright> |
| three.js r128 | <https://threejs.org> | MIT (`vendor/THREE-LICENSE.txt`) |

**Atribuição obrigatória para o relevo:** *Contains Copernicus data: EU-DEM v1.1, Copernicus Land Monitoring Service, European Environment Agency / European Commission.* O EU-DEM já não é mantido pelo serviço Copernicus.

As informações sobre as galerias e o aqueduto (Museu da Água / EPAL, Museu de Lisboa, Plano Geral de Drenagem de Lisboa) foram usadas apenas como factos descritivos para desenhar traçados esquemáticos. Não está incluída nenhuma geometria de terceiros.

## Reconstruir tudo a partir dos dados

Requisitos: Python 3.9 ou mais recente. Não é preciso instalar pacotes (apenas a biblioteca padrão).

```bash
# 1. Estações por linha: posições oficiais + ordem das estações a partir do zip do GTFS.
#    Descarregue o zip do GTFS (ver a tabela acima) e depois:
python3 tools/build_data.py --gtfs caminho/para/METRO.zip   # escreve data/lines.json

# 2. Malha do terreno a partir das amostras de cota guardadas no repositório (sem Internet):
python3 tools/build_terrain.py                              # escreve data/terrain.json
#    ...ou descarregue amostras novas da API pública (cerca de 1 pedido por segundo):
python3 tools/build_terrain.py --fetch                      # também reescreve data/elevation_samples.json

# 3. Edifícios do OpenStreetMap: descarregar (cerca de 36 MB, demora um ou dois minutos) e converter:
python3 tools/build_buildings.py --fetch                    # escreve data/buildings.json
#    ...ou converter de novo a partir da descarga guardada em data/raw/osm-buildings.json (fora do git):
python3 tools/build_buildings.py

# 4. Montar as páginas:
python3 tools/build_page.py                                 # escreve index.html e lisbon-underground-3d.html
```

Os passos 2 (sem Internet) e 4 reproduzem exatamente os ficheiros do repositório. O passo 3 com `--fetch` obtém os dados atuais do OpenStreetMap, por isso os edifícios mudam um pouco de cada vez. As amostras de cota guardadas estão arredondadas ao metro, por isso um novo `--fetch` pode dar resultados ligeiramente diferentes.

### Estrutura do projeto

| Caminho | O que é |
|---|---|
| `lisbon-underground-3d.html` | Página final com o three.js e os edifícios incluídos (abre sem Internet, cerca de 3,3 MB) |
| `index.html` | A mesma página, a carregar o three.js de uma CDN e `data/buildings.json` só quando os edifícios são ligados (é a página online) |
| `src/template.html` | Modelo da página: interface (textos em português e inglês), código 3D, marcadores para os dados |
| `data/raw/estacoes-de-metro.geojson` | Estações oficiais (CC0) |
| `data/lines.json` | Estações por ordem em cada linha (gerado por `build_data.py`) |
| `data/depths.json` | Profundidades estimadas (não medidas) abaixo da superfície, por estação |
| `data/elevation_samples.json` | Amostras de cota usadas para o terreno |
| `data/terrain.json` | Malha do terreno (gerada por `build_terrain.py`) |
| `data/hand_drawn_layers.json` | Traçados aproximados: ferrovia, aqueduto, Galerias Romanas, drenagem (nomes e descrições em português e inglês) |
| `data/shoreline.json` | Polígono aproximado do Tejo, usado para a água e para aplanar o terreno |
| `data/buildings.json` | Contornos e alturas dos edifícios do OpenStreetMap, simplificados (gerado por `build_buildings.py`, ODbL) |
| `tools/` | Os quatro scripts de construção |
| `vendor/` | three.js r128 e OrbitControls (MIT) |

### Alterações fáceis

- **Profundidades reais:** substitua os valores em `data/depths.json` (as chaves são os nomes das estações sem acentos, em minúsculas) e depois execute os passos 1 e 4.
- **Um traçado novo ou corrigido:** edite `data/hand_drawn_layers.json` (`[latitude, longitude, profundidade em metros abaixo da superfície]`; indique `name` e `desc` em `pt` e em `en`) e depois execute o passo 4.
- **Textos da interface:** todos os textos estão no objeto `I18N`, no início do script em `src/template.html`, com um bloco por idioma. Depois execute o passo 4.
- **Edifícios mais recentes:** execute o passo 3 com `--fetch` e depois o passo 4. As alturas acrescentadas ao OpenStreetMap (etiquetas `height` e `building:levels`) aparecem aqui na atualização seguinte.
- **Estações novas ou um GTFS mais recente:** execute o passo 1 com os ficheiros novos. Se um traçado do GTFS saltar uma estação, o script insere-a onde acrescenta menos comprimento e mostra uma mensagem.

## Ideias para melhorar

- Substituir as profundidades estimadas por dados reais (perfis longitudinais das linhas do metro)
- Usar um modelo de elevação mais fino
- Acrescentar a rede ferroviária real (conjunto de dados "Rede Ferroviária" no Lisboa Aberta)
- Acrescentar a Linha Circular e as estações mais recentes
- Melhorar a altura dos edifícios acrescentando `height` ou `building:levels` aos edifícios de Lisboa no OpenStreetMap, o que também ajuda todos os outros que usam o mapa

As contribuições são bem-vindas, em português ou em inglês. Se alterar algum texto, atualize os dois idiomas (a página, `data/hand_drawn_layers.json` e os dois README).

## Licença

- **Código** (`src/`, `tools/`): MIT, ver `LICENSE`.
- **Dados criados para este projeto** (`data/depths.json`, `data/hand_drawn_layers.json`, `data/shoreline.json`): [Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.pt). Pode reutilizá-los e adaptá-los, também para fins comerciais, desde que indique "Lisbon Underground 3D contributors" e uma ligação para este repositório.
- **Dados de outras fontes** (`data/raw/`, e `data/lines.json`, `data/elevation_samples.json` e `data/terrain.json`, que derivam deles): continuam a aplicar-se as licenças das fontes indicadas acima, incluindo a atribuição Copernicus.
- **Edifícios** (`data/buildings.json`, e a cópia dentro de `lisbon-underground-3d.html`): © contribuidores do OpenStreetMap, [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Se reutilizar estes dados, indique o OpenStreetMap; o que construir a partir deles e partilhar como base de dados tem de estar também sob ODbL.
- **three.js** (`vendor/`): MIT, ver `vendor/THREE-LICENSE.txt`.
