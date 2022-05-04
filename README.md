# covipy
Big data analysis of the Covid-19 / Wuhan-virus pandemic based on python


## Data
You should get your own local `timeseries_by_country.csv` file from:
  - https://covid19datahub.io/

See `notebooks/data_description.ipynb` for more information about the contents of data.

The `country_data.csv` was taken from UN population estimations as of 2020.

The `country_gdp_data.csv` was taken from https://databank.worldbank.org/reports.aspx?source=2&series=NY.GDP.MKTP.CD&country=


## Notebooks
You will find some jupyter notebooks in the `notebooks` directory that have a coded prefix indicating what kind of notebook it is:
  - D: data description.
  - P: data preparation from original to the version used in this project.
  - RQ: Research Questions. The resulting investigations of this project.
  - T: showcase the different techniques that can be used for the studies/research questions. Many of them been developed for this project.

## Research Questions
Several research questions are proposed in `notebooks/research_questions.ipynb` and each one of them are responded in the `notebooks/RQX.ipynb` where "X" is the number of the question at hand.
