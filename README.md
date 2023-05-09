[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ruijis/ashrae-db-II/HEAD)
# ASHRAE Global Thermal Comfort Database

The ASHRAE Global Thermal Comfort Database II combines sets of objective indoor
environmental measurements with accompanying "right-here-right-now" subjective evaluations
by occupants from buildings around the world. The database is intended to support diverse
inquiries about thermal comfort in field settings. This is the official repository which
contains the code used to maintain the Database II from version 2.1 onward. You can
download the latest version of the database from the [Github repository](https://github.com/CenterForTheBuiltEnvironment/ashrae-db-II) or [Dryad](https://datadryad.org/stash/dataset/doi:10.6078/D1F671).

This repository contains the source code we used to generate each new version of the
dataset. This allows you to track the changes we have implemented. We encourage you to
submit an issue if you spot any errors or you would like us to implement some changes. The
repository comprises different folders, each containing the source code and data we used
to generate a new version of the database.

## Columns names and description

### Database Metadata

| _parameter_         | _description_                                                                                                                                                                                   |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `building_id`       | Unique building identifier [integer]                                                                                                                                                            |
| `building_id_inf`   | Flag indicating if unique building identifier was from original data source [no] or inferred [yes] from unique groupings of publication, country, city, season, building type, and cooling type |
| `contributor`       | Principal contact person regarding the data                                                                                                                                                     |
| `publication`       | Published paper describing the project from where the data was collected                                                                                                                        |
| `region`            | Region of field study                                                                                                                                                                           |
| `country`           | Country of field study                                                                                                                                                                          |
| `city`              | City of field study                                                                                                                                                                             |
| `lat`               | Latitude of city [°]                                                                                                                                                                            |
| `lon`               | Latitude of city [°]                                                                                                                                                                            |
| `climate`           | Type of climate according to Köppen climate classification                                                                                                                                      |
| `building_type`     | Type of building [office, multifamily housing, classroom, senior center, other]                                                                                                                 |
| `cooling_type`      | Cooling strategy of building [air conditioned, mixed mode, naturally ventilated]                                                                                                                |
| `year`              | Year of field study [yyyy]                                                                                                                                                                      |
| `records`           | Number of records for that building ID                                                                                                                                                          |
| `has_age`           | Flag indicating if there age was recorded [yes, no] and if it was a categorical variable in the original data source [categorical]                                                              |
| `has_ec`            | Flag indicating if environmental controls were in the original data source [yes, no]                                                                                                            |
| `has_timestamp`     | Flag indicating if measurement timestamp was in the original data source [yes, no]                                                                                                              |
| `timezone`          | IANA time zone of field study                                                                                                                                                                   |
| `met_source`        | Source of meteorological data for `t_out` and `rh_out` [`ghcn_d` = from GHCN-D, `original_data` = from original data source; `rp884` = from RP884 database]                                     |
| `isd_station`       | ISD station code for `t_out_isd`, `rh_out_isd` and `t_mot_isd`                                                                                                                                  |
| `isd_distance`      | Estimated distance of ISD station to city of field study [km]                                                                                                                                   |
| `database`          | Version of database when data source was added [1, 2, 2.1]                                                                                                                                      |
| `quality_assurance` | Flag indicating if dataset from contributor passed automated quality assurance check [pass, fail]                                                                                               |

### Database Measurements

| _parameter_                  | _description_                                                                                                                                                                                                                                                                                                                                                    |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `building_id`                | Unique building identifier [integer]. Note: some building IDs are inferred - see `building_id_inf` in metadata table                                                                                                                                                                                                                                             |
| `timestamp`                  | Timestamp of measurement [yyyy-mm-dd]                                                                                                                                                                                                                                                                                                                            |
| `season`                     | Season measurement was made [summer, winter, hot/wet, cool/dry]. Note: based on the following assumptions when timestamp and location are known: northern hemisphere latitudes <20 are `hot/wet` from May-Oct and `cool/dry` from Nov-Apr; northern hemisphere latitudes >=20 are `summer` May-Oct and `winter` from Nov-Apr; vice versa for Southern Hemisphere |
| `subject_id`                 | Unique subject identifier for future studies with repeat samples [integer]                                                                                                                                                                                                                                                                                       |
| `age`                        | Age of subject [years]. Note: some studies used age ranges instead of years - see `has_age` in metadata table                                                                                                                                                                                                                                                    |
| `gender`                     | Gender of subject [female, male]                                                                                                                                                                                                                                                                                                                                 |
| `ht`                         | Height of subject [m]                                                                                                                                                                                                                                                                                                                                            |
| `wt`                         | Weight of subject [kg]                                                                                                                                                                                                                                                                                                                                           |
| `ta`                         | Air temperature measured in the occupied zone [°C]                                                                                                                                                                                                                                                                                                               |
| `ta_h`                       | Air temperature measured at 1.1 m above the floor [°C]                                                                                                                                                                                                                                                                                                           |
| `ta_m`                       | Air temperature measured at 0.6 m above the floor [°C]                                                                                                                                                                                                                                                                                                           |
| `ta_l`                       | Air temperature measured at 0.1 m above the floor [°C]                                                                                                                                                                                                                                                                                                           |
| `top`                        | Operative temperature calculated for the occupied zone [°C]                                                                                                                                                                                                                                                                                                      |
| `tr`                         | Radiant temperature measured in the occupied zone [°C]                                                                                                                                                                                                                                                                                                           |
| `tg`                         | Globe temperature measured in the occupied zone [°C]                                                                                                                                                                                                                                                                                                             |
| `tg_h`                       | Globe temperature measured at 1.1 m above the floor [°C]                                                                                                                                                                                                                                                                                                         |
| `tg_m`                       | Globe temperature measured at 0.6 m above the floor [°C]                                                                                                                                                                                                                                                                                                         |
| `tg_l`                       | Globe temperature measured at 0.1 m above the floor [°C]                                                                                                                                                                                                                                                                                                         |
| `rh`                         | Relative humidity [%]                                                                                                                                                                                                                                                                                                                                            |
| `vel`                        | Air speed measured in the occupied zone [m/s]                                                                                                                                                                                                                                                                                                                    |
| `vel_h`                      | Air speed measured at 1.1 m above the floor [m/s]                                                                                                                                                                                                                                                                                                                |
| `vel_m`                      | Air speed measured at 0.6 m above the floor [m/s]                                                                                                                                                                                                                                                                                                                |
| `vel_l`                      | Air speed measured at 0.1 m above the floor [m/s]                                                                                                                                                                                                                                                                                                                |
| `vel_r`                      | [Relative air speed](https://pythermalcomfort.readthedocs.io/en/latest/reference/pythermalcomfort.html#relative-air-speed) used to calculate the PMV [m/s]                                                                                                                                                                                                       |
| `met`                        | Average metabolic rate of the subject [met]                                                                                                                                                                                                                                                                                                                      |
| `clo`                        | Intrinsic clothing ensemble insulation of the subject [clo]                                                                                                                                                                                                                                                                                                      |
| `clo_d`                      | [Dynamic clothing](https://pythermalcomfort.readthedocs.io/en/latest/reference/pythermalcomfort.html#dynamic-clothing), used to calculate the PMV [clo]                                                                                                                                                                                                          |
| `activity_10`                | Average metabolic rate of the subject in the last 10 minutes [met]                                                                                                                                                                                                                                                                                               |
| `activity_20`                | Average metabolic rate of the subject in the last 20 minutes [met]                                                                                                                                                                                                                                                                                               |
| `activity_30`                | Average metabolic rate of the subject in the last 30 minutes [met]                                                                                                                                                                                                                                                                                               |
| `activity_60`                | Average metabolic rate of the subject in the last 60 minutes [met]                                                                                                                                                                                                                                                                                               |
| `thermal_sensation`          | Vote on the ASHRAE thermal sensation scale [-3 (cold) to 0 (neutral) +3 (hot)]                                                                                                                                                                                                                                                                                   |
| `pmv`                        | Predicted mean vote, calculated in compliance with the ISO 7730                                                                                                                                                                                                                                                                                                  |
| `pmv_ce`                     | Predicted mean vote, calculated in compliance with the ASHRAE 55 2020                                                                                                                                                                                                                                                                                            |
| `ppd`                        | Predicted percentage dissatisfied [%] calculated in compliance with the ISO 7730                                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                           |
| `ppd_ce`                     | Predicted percentage dissatisfied [%] calculated in compliance with the ASHRAE 55 2020                                                                                                                                                                                                                                                                           |
| `set`                        | Standard effective temperature [°C]                                                                                                                                                                                                                                                                                                                              |
| `thermal_acceptability`      | Thermal acceptability [acceptable, unacceptable]                                                                                                                                                                                                                                                                                                                 |
| `thermal_preference`         | Thermal preference [cooler, no change, warmer]                                                                                                                                                                                                                                                                                                                   |
| `thermal_comfort`            | Thermal comfort [1 (very uncomfortable) to 6 (very comfortable)]                                                                                                                                                                                                                                                                                                 |
| `air_movement_acceptability` | Air movement acceptability [acceptable, unacceptable]                                                                                                                                                                                                                                                                                                            |
| `air_movement_preference`    | Air movement preference [less, no change, more]                                                                                                                                                                                                                                                                                                                  |
| `blind_curtain`              | State of blinds or curtains [0 = open; 1 = closed]                                                                                                                                                                                                                                                                                                               |
| `fan`                        | State of fan [0 = off, 1 = on]                                                                                                                                                                                                                                                                                                                                   |
| `window`                     | State of window [0 = open, 1 = closed]                                                                                                                                                                                                                                                                                                                           |
| `door`                       | State of doors [0 = open, 1 = closed]                                                                                                                                                                                                                                                                                                                            |
| `heater`                     | State of heater [0 = off, 1 = on]                                                                                                                                                                                                                                                                                                                                |
| `t_out `                     | Outdoor air temperature from original dataset [°C]                                                                                                                                                                                                                                                                                                               |
| `rh_out`                     | Outdoor relative humidity from original dataset [%]                                                                                                                                                                                                                                                                                                             |
| `t_out_isd`                  | Average daily outdoor air temperature from ISD [°C]                                                                                                                                                                                                                                                                                                              |
| `rh_out_isd`                 | Average relative humidity from ISD [%]                                                                                                                                                                                                                                                                                                              |
| `t_mot_isd`                  | Calculated 7-day running mean outdoor temperature [°C]                                                                                                                                                                                                                                                                                                           |

## Contributing

You can contribute to the project by sending us your dataset. Please clean and collate the
data into a single .csv file that matches the existing DBII structure outlined. This
simple [web tool](https://databaseqc.shinyapps.io/submission/) will help error check and
format the data. It also has a downloadable .csv template file. Note that this tool
reflects the old database format - we will work to update the tool soon.

### Reporting issues

You can report issues with the database by
using [this link](https://github.com/FedericoTartarini/ashrae-db-II/issues)

## Changelog

### Version 2.1

This is the first major update to the ASHRAE Global Thermal Comfort Database II since it
was published in 2018. In the time since release, it has been used by hundreds of
researchers who have found errors and requested new features. This update aims to address
some of those while improving operability with other resources. As a result, there are
breaking changes.

The major updates to the database are:

1. 6,566 new records from field studies in India, Malaysia, Italy, Japan, Indonesia,
   Singapore, and Cyprus. Thanks to Hasim Altan (Arkin University of Creative Arts and
   Design), Siti Aisyah Damiati (University of Adelaide), Harimi Djamila (Universiti
   Malaysia Sabah), Jeetika Malik (Lawrence Berkeley National Laboratory), Bertug
   Ozarisoy (University of East London), Elisabetta Maria Patane (University of Bath), and
   Rajan Rawal (CEPT University) for kindly sharing their data with the community.
2. Improvements to the meteorological data. In the earlier version of the database, the
   source and quality of the meteorological data was unclear in some cases. We now use the
   NOAA Integrated Surface Database (ISD) for meteorological data where possible. Thanks
   to Peixian Li (Tongji University) for adding the timestamps from the original
   datasets (where available). Meteorological data from either the original dataset or the
   ISD are now included along with the relevant metadata.
3. The database is now split into a metadata table and a measurements table. This should
   make working with the full dataset quicker and easier due to smaller file sizes and new
   fields in the metadata table.

There are many other changes included in this update. The full change log is below:

- Added building ID from RP-884 dataset
- Added timestamp from RP-884 dataset
- Added meteorological data from RP-884 dataset
- Added timestamp to datasets where known [Ariel Li - Tongji University]
- Added 6,566 measurements from new data contributions
- Split database into metadata and measurement tables
- Recalculated PMV/PPD using [pythermalcomfort](https://pythermalcomfort.readthedocs.io/en/latest/readme.html)
- Performed simple quality assurance on measurement database
- Shared python code used to calculate PMV/PPD
- Shared R code with an example analysis of adaptive thermal comfort
- Dropped records with missing `ta`
- Recoded many categorical scale variables to standardised English label text
- Dropped all imperial units
- Renamed headers to remove spaces and special characters
- Renamed headers for PMV inputs to align with software
  packages [[Federico Tartarini](https://federicotartarini.github.io/) - BEARS; Marcel Schweiker - RWTH Aachen University]
- Recoded cooling types `Mechanically ventilated`; and `Mixed (hybrid)` into `mixed mode`
- Recoded season when timestamp and location is known
- Added average daily temperature calculated from ISD data
- Added running mean outdoor temperature from ISD data
- Added inferred building id based on unique groupings of publication, country, city,
  season, building type, and cooling type
- Added inferred building ID flag to metadata table
- Added sample size for each building ID to metadata table
- Added approximate coordinates to metadata table
- Added time zone to metadata table
- Added source of meteorological data to metadata table
- Added ISD station number and distance to metadata table
- Added categorical age field flag to metadata
  table [Jing Xiong - The University of Sydney]
- Added environmental control flag to metadata table
- Added timestamp flag to metadata table
- Added region to metadata table
- Added quality assurance flag to metadata table
- Replaced full reference in metadata table with DOI where known
- Standardised country names in metadata table
- Fixed season in Oseland dataset [Carlucci; Matteo Favero - NTNU]
- Added building ID in Oseland dataset
- Fixed asv and building type in Zhangeri
  dataset [Salvatore Carlucci - The Cyprus Institute; Matteo Favero - Norwegian University of Science and Technology]
- Added building ID in Zhangeri dataset
- Removed thermal comfort vote for Zhangeri
  dataset [Salvatore Carlucci - The Cyprus Institute; Matteo Favero - Norwegian University of Science and Technology]
- Added unique identifier for records (`record_id`) to help error reporting
- Added new column (`subject_id`) for future submissions with repeated measures
