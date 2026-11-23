# Como contribuir

[English](CONTRIBUTING.md) · **Português**

Obrigado pelo interesse no Lisboa Subterrânea 3D. Não é preciso saber programar para ajudar: assinalar um erro ou indicar uma boa fonte de dados é igualmente valioso. Pode escrever em português ou em inglês.

## Formas de ajudar

### Assinalar um erro ou sugerir uma ideia (sem código)

Abra uma [issue](https://github.com/Rob-sss/lisbon-underground-3d/issues/new/choose) e escolha o formulário adequado:

- **Algo não funciona:** a página não abre, um botão não faz nada, fica muito lenta no seu dispositivo.
- **Correção de dados:** uma estação, um traçado, uma profundidade ou um edifício está errado ou em falta. Diga onde, o que está errado e, se possível, como sabe (uma ligação, um documento, uma fotografia).
- **Ideia:** uma nova camada, uma fonte de dados melhor, uma funcionalidade.

### Melhorar a altura dos edifícios (sem código, através do OpenStreetMap)

Cerca de dois terços dos edifícios têm uma altura *estimada*, porque o OpenStreetMap ainda não a tem. Se conhece Lisboa, pode corrigir isto na origem, o que ajuda todos os mapas que usam o OpenStreetMap:

1. Crie uma conta gratuita em <https://www.openstreetmap.org>, aproxime-se de um edifício e clique em **Editar**.
2. Acrescente `building:levels` (número de pisos acima do solo) ou `height` (em metros), se souber.
3. Siga as regras do OpenStreetMap: use o seu próprio conhecimento, observação no local ou fontes que o OpenStreetMap permite. **Nunca copie do Google Maps nem de outros mapas protegidos por direitos de autor.** Ver <https://wiki.openstreetmap.org/wiki/Pt:Guia_de_Iniciante>.

As suas edições aparecem aqui na próxima atualização dos edifícios (ver "Reconstruir" no [README](README.pt.md#reconstruir-tudo-a-partir-dos-dados)).

### Profundidades reais dos túneis (os dados mais procurados)

As profundidades do metro em `data/depths.json` são estimativas grosseiras, não medições. Se conhece uma fonte pública com profundidades reais (perfis longitudinais das linhas, relatórios técnicos, plantas das estações), abra uma issue de **Correção de dados** com a ligação. Só a podemos usar se a licença permitir a reutilização (ver [Regras para os dados](#regras-para-os-dados)).

### Rever o texto em português

A página e os documentos estão em inglês e em **português europeu**. Falantes nativos são muito bem-vindos para corrigir a redação, através de uma issue ou de um pull request.

## Regras para os dados

Tudo neste repositório tem de poder ser partilhado legalmente. Antes de acrescentar dados:

- **Só dados abertos.** Aceites: domínio público / CC0, CC BY 4.0 e a ODbL para dados do OpenStreetMap (apenas edifícios). Se tiver dúvidas sobre uma licença, pergunte primeiro numa issue.
- **Nunca copie** do Google Maps, Apple Maps, Bing, outros mapas comerciais, nem de plantas e livros protegidos por direitos de autor. Factos (por exemplo "esta galeria fica a cerca de 10 m de profundidade, segundo o Museu da Água") podem ser usados para desenhar um traçado aproximado; desenhos e geometrias não podem ser copiados.
- **Indique a origem.** Acrescente a fonte e a licença à tabela dos dois README ("Fontes dos dados e licenças").
- **Seja honesto quanto à precisão.** Se um valor é estimado ou aproximado, a página e os README têm de o dizer, como já fazem para as profundidades e a altura dos edifícios.

## Alterar o código ou os ficheiros de dados

Requisitos: Python 3.9 ou mais recente e um navegador. Não é preciso instalar pacotes.

### Importante: edite as fontes, não as páginas geradas

`index.html` e `lisbon-underground-3d.html` são **gerados**. Não os edite à mão: edite os ficheiros abaixo e reconstrua.

| Para alterar | Edite | Depois execute |
|---|---|---|
| Textos da interface, disposição, código 3D | `src/template.html` (todos os textos estão no objeto `I18N`, um bloco por idioma) | `python3 tools/build_page.py` |
| Um traçado desenhado à mão (ferrovia, aqueduto, galerias, drenagem) | `data/hand_drawn_layers.json` (indique `name` e `desc` em `pt` e em `en`) | `python3 tools/build_page.py` |
| Profundidades das estações | `data/depths.json` | `tools/build_data.py` e depois `tools/build_page.py` (ver o README) |
| Edifícios | nada à mão: vêm do OpenStreetMap | `python3 tools/build_buildings.py --fetch` e depois `python3 tools/build_page.py` |
| Scripts de construção | `tools/*.py` (apenas biblioteca padrão, por favor: sem pacotes extra) | o script que alterou e depois `tools/build_page.py` |

Faça commit tanto da fonte que alterou **como** do `index.html` e `lisbon-underground-3d.html` regenerados, para que a página online e a descarga fiquem iguais. Nunca faça commit de `data/raw/osm-buildings.json` (é grande e o git ignora-o).

### Mantenha os dois idiomas iguais

Todo o texto visível existe em português e em inglês: em `src/template.html`, em `data/hand_drawn_layers.json`, em `README.md` / `README.pt.md` e em `CONTRIBUTING.md` / `CONTRIBUTING.pt.md`. Se alterar um idioma e não conseguir escrever o outro, diga-o no pull request e alguém fará a tradução. Use português europeu (por exemplo *comboio*, *ecrã*, *ficheiro*), não brasileiro.

### Teste antes de abrir um pull request

1. **Página sem Internet:** abra `lisbon-underground-3d.html` no navegador.
2. **Versão online:** execute `python3 -m http.server 8000` na pasta do projeto e abra <http://localhost:8000/?buildings=1> (pare o servidor com Ctrl+C).
3. Nas duas: mude entre EN / PT, ligue e desligue as camadas (incluindo **Edifícios**), clique numa estação, num túnel, num edifício e no terreno, mova o controlo de exagero, experimente a "Escala real".
4. Torne a janela estreita (cerca da largura de um telemóvel) e verifique que nada se sobrepõe.
5. Se alterou um script, execute-o e verifique que termina sem erros.

### Abrir um pull request

1. Faça um fork do repositório e crie um ramo com um nome curto (por exemplo `corrige-tunel-rossio`).
2. Faça a alteração; cada pull request deve tratar de uma só coisa.
3. Escreva uma mensagem de commit clara, em português ou em inglês.
4. Abra o pull request e preencha a lista de verificação. Acrescente uma captura de ecrã se a página ficar diferente.

Nunca usou o GitHub? Ver <https://docs.github.com/pt/get-started/exploring-projects-on-github/contributing-to-a-project>.

## Licença das contribuições

Ao contribuir, aceita que a sua contribuição seja publicada sob as licenças deste projeto:

- código: MIT (`LICENSE`);
- dados criados para o projeto: CC BY 4.0;
- dados dos edifícios: ODbL (vêm do OpenStreetMap).

Contribua apenas com trabalho que tenha o direito de partilhar.

## Seja simpático

Este é um pequeno projeto pessoal, feito por curiosidade pela cidade. Seja respeitoso e paciente com todos, qualquer que seja a sua experiência, língua ou origem. Critique ideias, não pessoas. Não é aceite assédio nem comportamento insultuoso, e o responsável pelo projeto pode remover esses comentários ou bloquear os seus autores.
