# Shipping data
This repository contains a public collection of shipping data from South America to The Netherlands and Belgium, and the tools for obtaining this data.

## Repository structure
The repository is structured as follows:
 - [`webscrapers`](webscrapers) contains the Python file for each webscraper.
 - [`docs`](docs) contains all the specific documentation for each webscraper.
 - [`notebooks`](notebooks) contains (parts of the) webscrapers in Notebook format.
 - [`pickles`](pickles) contains Pickle files for all data in Python (mostly Pandas DataFrames).
 - [`data`](data) contains all other data (mostly CSVs).
 - [`scripts`](scripts) contains helper Python scripts to merge data for example.
 - [`utils`](utils) contains utility files and notebooks, for example with UN-LOCODES for ports.
 - [`.github/workflows`](.github/workflows) contains GitHub Actions workflow files for automation.

And less importantly:
 - [`drivers`](drivers) has a chromedriver file.
 - [`administration`](administration) contains some administrative documents.

## The webscrapers
In this section the current webscrapers are globally explained.

### Routescanner

The Routescanner webscraper scans planned container connections from https://www.routescanner.com/voyages. The webscraper is available at [`webscrapers/routescanner_automated.py`](webscrapers/routescanner_automated.py) and runs each morning thanks to the [`routescanner_daily.yml`](.github/workflows/routescanner_daily.yml) GitHub Actions workflow. It's currently configured to scrape all connections between 26 departure ports in South America and Vietnam, and 5 arrival ports in The Netherlands and Belgium. For these 130 port-combinations around 1400 connections are found each run, while not all unique.

Daily run data is saved in [`data/routescanner_daily`](data/routescanner_daily) in CSV form and in [`pickles/routescanner_daily`](pickles/routescanner_daily) using [pickles](https://docs.python.org/3/library/pickle.html), which each contain a Pandas DataFrame. The [`scripts/combine_routescanner.py`](scripts/combine_routescanner.py) can be used to merge all the DataFrames, of which the resulting combined data can be found in [`pickles/routescanner_connections_combined.pickle`](pickles/routescanner_connections_combined.pickle) and [`data/routescanner_connections_combined.csv`](data/routescanner_connections_combined.csv).

A Jupyter Notebook is also available at [`notebooks/scraping_routescanner.ipynb`](notebooks/scraping_routescanner.ipynb).

The ports are listed in [UN/LOCODE](https://unece.org/trade/cefact/unlocode-code-list-country-and-territory), for example `NLRTM` for the Port of Rotterdam in The Netherlands. The [`utils`](utils) folder contains a two CSV files with all UN/LOCODEs and a Jupyter Notebook to load those into a Pandas Dataframe.

For the full documentation, see [`docs/routescanner.md`](docs/routescanner.md), as well as the inline comments.

### MSC

An initial version of the MSC webscraper is available at [`webscrapers/msc_automated.py`](webscrapers/msc_automated.py). It scraped the same 130 port-combinations as the Routescanner scraper from the MSC schedule (https://www.msc.com/en/search-a-schedule).

Initial data is available in CSV and Pickle form at [`data/msc_daily`](data/msc_daily) and [`pickles/msc_daily`](pickles/msc_daily). An experimental notebook can be found at [`notebooks/scraping_msc.ipynb`](notebooks/scraping_msc.ipynb).

A script to combine the data from multiple days is available at [`scripts/combine_msc.py`](scripts/combine_msc.py). The combined data itself is available as CSV and Pickle at [`data/msc_connections_combined.csv`](data/msc_connections_combined.csv) and [`pickles/msc_connections_combined.pickle`](pickles/msc_connections_combined.pickle).

It's in prototype state, with a lot of open bugs and unwanted behaviour. Data collected will be incomplete.

## License
As for now, all code in this repository is licensed under the GPL-3.0 license. At a later moment in this project this may change to a more permissive license.

See the [`LICENSE`](LICENSE) file.
