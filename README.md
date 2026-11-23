# Lisbon Underground 3D

**English** · [Português](README.pt.md)

An interactive 3D view of what lies beneath Lisbon: the metro, the railway and historic galleries, drawn under the city's terrain and buildings. Made out of curiosity about urban design, to share with anyone interested in how the city works below street level.

**Try it online: <https://rob-sss.github.io/lisbon-underground-3d/>** ([versão portuguesa](https://rob-sss.github.io/lisbon-underground-3d/?lang=pt))

Or download `lisbon-underground-3d.html` and open it in any browser. It works offline: no server, no install, no account.

The page is available in English and European Portuguese. It follows your browser's language; use the **PT / EN** button (top right) to switch, or add `?lang=en` or `?lang=pt` to the address. Add `&buildings=1` to open the page with the buildings already switched on, for example <https://rob-sss.github.io/lisbon-underground-3d/?lang=en&buildings=1>.

## What's inside

- The 4 Lisbon Metro lines and their 50 stations, built from official open data
- Terrain interpolated from EU-DEM elevation samples
- About 52,000 buildings from OpenStreetMap, with their heights (off by default: tap **Buildings (OSM)** to load them)
- Toggleable layers: metro, railway, aqueduct (Galeria do Loreto), Roman galleries, drainage tunnels
- A vertical-exaggeration slider and a **true scale (1:1)** mode
- Tap or click any element for details

## Read this before using it

This is an **educational sketch, not a surveyed map**.

- **Depths are estimates, not measurements.** No open dataset with metro tunnel depths was found, so the station depths in `data/depths.json` are rough guesses made for this sketch, not taken from any source. They only give the 3D view a plausible shape. The depths of the hand-drawn layers are estimates too.
- **Coarse terrain.** Elevation is sampled about every 1.4 km, plus the height of each of the 50 stations, then interpolated. Small features (for example the Baixa valley) are smoothed out. EU-DEM is a *surface* model, so it includes buildings and vegetation.
- **Building heights are often estimated.** About 18% of the buildings have a height in OpenStreetMap and about 18% have a number of floors (counted as 3 m each). For the other ~64% the height is a guess: 12 m, or 3 m for small structures such as garages and kiosks. Tap a building to see which case applies. Courtyards are filled in, and buildings mapped after the download date are missing.
- **Hand-drawn layers.** Railway, aqueduct, Roman galleries and the drainage tunnels (TMSA, TCB) are approximate, hand-drawn routes (`data/hand_drawn_layers.json`).

Do not use it for design, excavation or safety decisions.

## Data sources and licences

Checked on 22 Nov 2026. Please re-check before reusing the data.

| Data | Source | Licence |
|---|---|---|
| Position of the 50 stations | Câmara Municipal de Lisboa, Lisboa Aberta, dataset "Estações de Metro" (GeoJSON resource `POITransportes`): <https://dadosabertos.cm-lisboa.pt/dataset/estacoes-de-metro> | Creative Commons CC0 (stated on the resource page) |
| Order and route of the lines | Metropolitano de Lisboa GTFS, copy on Zenodo: <https://zenodo.org/records/18830433> | CC0 1.0 (creator: Metropolitano de Lisboa, E.P.E.). Note: the Zenodo copy dates from 2019 |
| Terrain elevation | EU-DEM v1.1, 25 m (Copernicus Land Monitoring Service, European Commission), queried through the public Open Topo Data API: <https://www.opentopodata.org> | Free and open, source must be credited (see below) |
| Buildings (outlines, heights, number of floors, names) | © OpenStreetMap contributors, downloaded through the Overpass API on 23 Nov 2026: <https://www.openstreetmap.org> | [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/), credit required: see <https://www.openstreetmap.org/copyright> |
| three.js r128 | <https://threejs.org> | MIT (`vendor/THREE-LICENSE.txt`) |

**Required attribution for the terrain:** *Contains Copernicus data: EU-DEM v1.1, Copernicus Land Monitoring Service, European Environment Agency / European Commission.* EU-DEM is no longer maintained by the Copernicus service.

Information on the galleries and aqueduct (Museu da Água / EPAL, Museu de Lisboa, Lisbon Drainage Plan) was used only as descriptive facts to draw schematic routes. No third-party geometry is included.

## Rebuild everything from the data

Requirements: Python 3.9 or newer. No packages to install (standard library only).

```bash
# 1. Stations per line: official station positions + station order from the GTFS zip.
#    Download the GTFS zip yourself (see the table above), then:
python3 tools/build_data.py --gtfs path/to/METRO.zip        # writes data/lines.json

# 2. Terrain mesh from the elevation samples stored in the repository (offline):
python3 tools/build_terrain.py                              # writes data/terrain.json
#    ...or download fresh samples from the public API (about 1 request per second):
python3 tools/build_terrain.py --fetch                      # also rewrites data/elevation_samples.json

# 3. Buildings from OpenStreetMap: download them (about 36 MB, takes a minute or two) and convert:
python3 tools/build_buildings.py --fetch                    # writes data/buildings.json
#    ...or convert again from the download kept in data/raw/osm-buildings.json (not in git):
python3 tools/build_buildings.py

# 4. Assemble the pages:
python3 tools/build_page.py                                 # writes index.html and lisbon-underground-3d.html
```

Steps 2 (offline) and 4 reproduce the committed files exactly. Step 3 with `--fetch` gets the current OpenStreetMap data, so the buildings will differ a little each time. The stored elevation samples are rounded to whole metres, so a fresh `--fetch` may differ very slightly.

### Project layout

| Path | What it is |
|---|---|
| `lisbon-underground-3d.html` | Finished page with three.js and the buildings included (opens offline, about 3.3 MB) |
| `index.html` | Same page, loading three.js from a CDN and `data/buildings.json` only when the buildings are switched on (this is the online page) |
| `src/template.html` | Page template: UI (English and Portuguese text), 3D code, placeholders for the data |
| `data/raw/estacoes-de-metro.geojson` | Official stations (CC0) |
| `data/lines.json` | Stations in order for each line (generated by `build_data.py`) |
| `data/depths.json` | Estimated (not measured) depths below the surface, by station |
| `data/elevation_samples.json` | Elevation samples used for the terrain |
| `data/terrain.json` | Terrain mesh (generated by `build_terrain.py`) |
| `data/hand_drawn_layers.json` | Approximate routes: railway, aqueduct, Roman galleries, drainage (names and descriptions in English and Portuguese) |
| `data/shoreline.json` | Rough Tagus polygon, used for the water and to flatten the terrain |
| `data/buildings.json` | Building outlines and heights from OpenStreetMap, simplified (generated by `build_buildings.py`, ODbL) |
| `tools/` | The four build scripts |
| `vendor/` | three.js r128 and OrbitControls (MIT) |

### Easy things to change

- **Real depths:** replace the values in `data/depths.json` (keys are station names without accents, lower case), then run steps 1 and 4.
- **A new or corrected route:** edit `data/hand_drawn_layers.json` (`[latitude, longitude, depth in metres below the surface]`; give `name` and `desc` in both `en` and `pt`), then run step 4.
- **Interface text:** all labels are in the `I18N` object at the top of the script in `src/template.html`, one block per language. Then run step 4.
- **Newer buildings:** run step 3 with `--fetch`, then step 4. Better heights in OpenStreetMap (the `height` and `building:levels` tags) show up here at the next refresh.
- **New stations or a newer GTFS:** run step 1 with the new files. If a GTFS shape skips a station, the script inserts it where it adds the least length, and prints a message.

## Ideas for improvement

- Replace the estimated depths with real data (longitudinal profiles of the metro lines)
- Use a finer elevation model
- Add the real railway network (the "Rede Ferroviária" dataset on Lisboa Aberta)
- Add the Circular line and the newer stations
- Improve building heights by adding `height` or `building:levels` to Lisbon buildings in OpenStreetMap, which also helps everyone else who uses the map

Contributions are welcome, in English or Portuguese. If you change any text, please update both languages (the page, `data/hand_drawn_layers.json`, and both READMEs).

## Licence

- **Code** (`src/`, `tools/`): MIT, see `LICENSE`.
- **Data created for this project** (`data/depths.json`, `data/hand_drawn_layers.json`, `data/shoreline.json`): [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You may reuse and adapt it, also commercially, as long as you credit "Lisbon Underground 3D contributors" and link to this repository.
- **Data from other sources** (`data/raw/`, and `data/lines.json`, `data/elevation_samples.json` and `data/terrain.json`, which are derived from them): the licences of their sources listed above still apply, including the Copernicus attribution.
- **Buildings** (`data/buildings.json`, and the copy inside `lisbon-underground-3d.html`): © OpenStreetMap contributors, [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). If you reuse this data, credit OpenStreetMap; anything you build from it and share as a database must also be under ODbL.
- **three.js** (`vendor/`): MIT, see `vendor/THREE-LICENSE.txt`.
