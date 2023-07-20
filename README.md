# MDH (MyDataHelps) export application
This project was written as part of the every growing eco-system of SensorFabric under the umbrella of University of Arizona's 
Sensor Analysis and Smart Platform initiative.
* Link to [UAHS CB2](https://cb2.uahs.arizona.edu/)
* Link to [Care Evolution MyDataHelps](https://careevolution.com/mydatahelps/)

## Assumptions
This assumes that Fitbit has been enabled for your project. In a future release will add the ability to automatically detect fitbit tables,
and disable fitbit exports if the project does not contain fitbit data. (Pull requests welcomed, and I can credit them here).

## Why did I write this application?
While MDH has a very good data exporter, along with an export explorer it lacks the ability to export CSV and Parquet files from 
a CLI interface. This is useful when running this as part of an fully automated export workflow. The application / tool does the following -
* Generates CSV and Parquet files for each table that is being exported. **CAREFUL-Depending on your tables, this can contain PHI data**
* Generate CSV file for Surveys, titled <surveyname.csv>, where the id's are automatically replaced with text based questiona and answers.
* Generates a set of Fitbit Summary csv files, that can be used to gather compliance information.

## Tell me more about the processed survey exports.
Traditional Electronic Data Capture systems make use of id's to reference survey responses; for instance a surevey result might contain 
id's for survey question, survey variable, survey version etc. For PI's to quickly take a look at the responses, they have to chain all these
various id's together to get a (question, answer) pair. This exporter tools simplies this process by automatically generating a seperate csv
file for each survey (named after the survey it was generated from), and also populating it with the following fields -
* `participantidentifier`
* `question` - The question text corresponding to the latest version of the survey.
* `startdate`
* `enddate`
* `resultidentifier`
* `answer` - Text based answer corresponding to this question.

These csv files are stored inside the folder `SurveyProcessed`

### Hold on, what is catch with this auto-processing?
A few things to remember -
* This is only meant for review / quick view.
* If a survey's name has changed over the course of the study, then 1 file will be generated for each of the survey names. You will need to manually concat them.
* Only the question corresponding to the latest version of the survey is displayed. If there where multiple versions of the survey throughout the course of this study then only the latest version of the survey will be displayed.

## How do I install this?
Assuming you have cloned this repository using `git clone` you can follow the below instructions to setup the exporter tool and use it.
```bash
cd mdh-export
python3 -m venv .env
source .env/bin/activate
pip3 install -r requirements.txt
```
The installation makes use of python virtual environment to keep things clean. You will need activiate and deactivate (`deactivate`) the environment accordingly.

## Setting up the configuration file
In order for this tool to work you must update the values insisde `config.example.ini`. I also highly recommend changing the file name to `config.ini` since this has already been added to `.gitignore`.
This way you don't accidentally push the keys to git (if you make changes on your seperate fork) and give your hardworking IT reps a mild stroke!
All the values for the configuration file can be found from inside `MDH Project Settings -> Export Explorer -> External Explorer -> Create Credentials (click this button)`.

## But what if I want to use this on my own AWS dataset?
You might have realized that the keys used inside `config.ini` are the ones that correspond to standard AWS Security Key for users, along with credentials for AWS Athena Data Catalog
If you wish to use this tool to connect to your own AWS Data Catalog instead of MDH, then you can do so by changing the key values to match those of your IAM user and Data Catalog.
**Note** - Unless you also have fitbit tables with the same names as the MDH Catalog, I would recommend commenting out `exportFitbitSummary` and `exportProcessedSurveys` from `main.py`

## How can I run this tool
Like this!
```bash
(.env) demoshell>>python3 main.py config.ini output
Could not find output folder. Automatically making one.
```
Remember to have activated your python virtual environment you made earilier.

## What is the folder structure?
The folder structure has been named in a self-explanatory way. Here is a quick overview -
```
output
├── FitbitSummary : Fitbit Summary Data - Activity, HRV, Sleep, Resting HR
├── RawCSv : Each table in db is exported as a raw CSV.
├── RawParquet : Each table in db is exported as parquet.
└── SurveyProcessed : A csv file for each survey name (can have multiple versions of the same survey if the name changed).
```

## Wishlist of features to be added
* Auto-detect if the project supports Fitbit and enable / disable fitbit export.
* Add support for AppleWatch and Garmin summary.
* Support multiple profiles inside the `config.ini` file so the tool can be used for multiple projects.
* Add this to a bigger workflow, where the keys inside config file are auto poppulated using MDH service keys and API.

## Bugs and Requests
If you find bugs (including spelling or grammer erros in this README) please raise an gitbub issue, or submit a patch.
If you think of something you would like in this tool, please submit a pull request.

## Links to other useful repositories under SensorFabric
* Fitbit compliance Dash application - https://github.com/nextgensh/sensorfabric-fitbitcompliance.git
* SensorFabric Library - https://github.com/UArizonaCB2/sensorfabric-py.git
* Examples of using MDH Serivce API (with sensor demo for steps) - https://github.com/nextgensh/MDH-Service-Examples.git

Thats all folks! Happy Hacking.

## Changelog
1. 7.20.2023 - Added an option to skip tables for the full export in the config.ini file. Useful to exclude intraday fitbit data exports.
