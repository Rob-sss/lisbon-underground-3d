# Contributing

**English** · [Português](CONTRIBUTING.pt.md)

Thank you for your interest in Lisbon Underground 3D. You don't need to know how to code to help: reporting a mistake or pointing to a good data source is just as valuable. You can write in English or Portuguese.

## Ways to help

### Report a mistake or suggest an idea (no code)

Open an [issue](https://github.com/Rob-sss/lisbon-underground-3d/issues/new/choose) and pick the form that fits:

- **Something doesn't work:** the page doesn't load, a button does nothing, it is very slow on your device.
- **Data correction:** a station, route, depth or building is wrong or missing. Say where, what is wrong, and if possible how you know (a link, a document, a photo).
- **Idea:** a new layer, a better data source, a feature.

### Improve building heights (no code, through OpenStreetMap)

About two thirds of the buildings have an *estimated* height, because OpenStreetMap doesn't have one for them yet. If you know Lisbon, you can fix this at the source, and it helps every map that uses OpenStreetMap:

1. Create a free account on <https://www.openstreetmap.org>, zoom to a building and click **Edit**.
2. Add `building:levels` (number of floors above ground) or `height` (in metres), if you know it.
3. Follow OpenStreetMap's rules: use your own knowledge, a survey, or sources OpenStreetMap allows. **Never copy from Google Maps or other copyrighted maps.** See <https://wiki.openstreetmap.org/wiki/Beginners%27_guide>.

Your edits appear here the next time the buildings are refreshed (see "Rebuild" in the [README](README.md#rebuild-everything-from-the-data)).

### Real tunnel depths (the most wanted data)

The metro depths in `data/depths.json` are rough guesses, not measurements. If you know of a public source with real depths (longitudinal profiles of the lines, technical reports, station plans), please open a **Data correction** issue with a link. We can only use it if its licence allows reuse (see [Data rules](#data-rules)).

### Check the Portuguese text

The page and documents are in English and **European Portuguese**. Native speakers are very welcome to correct wording, either with an issue or a pull request.

## Data rules

Everything in this repository must be legal to share. Before adding data:

- **Only open data.** Accepted: public domain / CC0, CC BY 4.0, and the ODbL for OpenStreetMap data (buildings only). If you are not sure about a licence, ask in an issue first.
- **Never copy** from Google Maps, Apple Maps, Bing, other commercial maps, or copyrighted plans and books. Facts (for example "this gallery is about 10 m deep, according to the Museu da Água") may be used to draw an approximate route; drawings and geometry may not be copied.
- **Say where it comes from.** Add the source and its licence to the table in both READMEs ("Data sources and licences").
- **Be honest about precision.** If a value is estimated or approximate, the page and the READMEs must say so, as they do for the depths and building heights.

## Changing the code or data files

Requirements: Python 3.9 or newer and a web browser. No packages to install.

### Important: edit the sources, not the generated pages

`index.html` and `lisbon-underground-3d.html` are **generated**. Do not edit them by hand: edit the files below and rebuild.

| To change | Edit | Then run |
|---|---|---|
| Interface text, layout, 3D code | `src/template.html` (all text is in the `I18N` object, one block per language) | `python3 tools/build_page.py` |
| A hand-drawn route (railway, aqueduct, galleries, drainage) | `data/hand_drawn_layers.json` (give `name` and `desc` in both `en` and `pt`) | `python3 tools/build_page.py` |
| Station depths | `data/depths.json` | `tools/build_data.py`, then `tools/build_page.py` (see the README) |
| Buildings | nothing by hand: they come from OpenStreetMap | `python3 tools/build_buildings.py --fetch`, then `python3 tools/build_page.py` |
| Build scripts | `tools/*.py` (standard library only, please: no extra packages) | the script you changed, then `tools/build_page.py` |

Commit both the source you changed **and** the regenerated `index.html` and `lisbon-underground-3d.html`, so the online page and the download stay in sync. Never commit `data/raw/osm-buildings.json` (it is large and ignored by git).

### Keep both languages in sync

Every visible text exists in English and Portuguese: in `src/template.html`, in `data/hand_drawn_layers.json`, in `README.md` / `README.pt.md` and in `CONTRIBUTING.md` / `CONTRIBUTING.pt.md`. If you change one language and can't write the other, say so in your pull request and someone will translate it. Use European Portuguese (for example *comboio*, *ecrã*, *ficheiro*), not Brazilian.

### Test before opening a pull request

1. **Offline page:** open `lisbon-underground-3d.html` in your browser.
2. **Online version:** run `python3 -m http.server 8000` in the project folder and open <http://localhost:8000/?buildings=1> (stop the server with Ctrl+C).
3. In both: switch EN / PT, turn layers on and off (including **Buildings**), click a station, a tunnel, a building and the terrain, move the exaggeration slider, try "True scale".
4. Make the window narrow (about phone width) and check that nothing overlaps.
5. If you changed a script, run it and check that it finishes without errors.

### Open a pull request

1. Fork the repository and create a branch with a short name (for example `fix-rossio-tunnel`).
2. Make your change; keep each pull request about one thing.
3. Write a clear commit message, in English or Portuguese.
4. Open the pull request and fill in the checklist. Add a screenshot if the page looks different.

New to GitHub? See <https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project>.

## Licence of contributions

By contributing, you agree that your contribution is published under the licences of this project:

- code: MIT (`LICENSE`);
- data created for the project: CC BY 4.0;
- building data: ODbL (it comes from OpenStreetMap).

Only contribute work that you have the right to share.

## Be kind

This is a small hobby project made out of curiosity about the city. Be respectful and patient with everyone, whatever their experience, language or background. Criticise ideas, not people. Harassment or insulting behaviour is not accepted, and the maintainer may remove such comments or block their authors.
