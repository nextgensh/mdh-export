#!/usr/bin/env python3

"""
Author : Shravan Aras <shravanaras@arizona.edu>
Creation Date : 5/30/2023
This application connects directly to the MDH backend and is used to download all the tables from the
data exporter as a CSV file.
"""

import os
import pyathena
from pyathena import connect
from pyathena.pandas.cursor import PandasCursor
import pandas as pd
import configparser
import sys
from Fitbit import Fitbit

"""
Map of the directory structure used in the output folder.
"""
dirStructure = {
    'raw_csv' : 'RawCSv',
    'raw_parquet' : 'RawParquet',
    'survey_processed' : 'SurveyProcessed',
    'fitbit_summary' : 'FitbitSummary'
}

def main(argv:list):
    """
    Main application method.
    """

    if len(argv) < 3:
        print('Usage:\n python3 main.py <config file path> <output folder>')
        exit()

    fname = argv[1]
    if not os.path.isfile(fname):
        return E('Config file not found. Check path or permissions.')

    outputFolder = argv[2]
    if os.path.isdir(outputFolder):
        print('Output folder already exists. Beware all files will be overwriten inside it.')
        createOutputStructure(outputFolder, createFolder=False)
    else:
        print('Could not find output folder. Automatically making one.')
        createOutputStructure(outputFolder, createFolder=True)

    config = configparser.ConfigParser()
    config.read(argv[1])

    if not ('default' in config):
        return E('default profile not found inside the configuration file.')

    default = config['default']

    cursor = connect(aws_access_key_id=default['aws_access_key_id'],
                aws_secret_access_key=default['aws_secret_access_key'],
                aws_session_token=default['aws_session_token'],
                s3_staging_dir=default['s3_staging_dir'],
                region_name=default['region_name'],
                schema_name=default['schema_name'],
                work_group=default['work_group'],
                cursor_class=PandasCursor
                ).cursor()

    tableFrame = getTables(cursor)
    tables = tableFrame['tab_name'].values
    #exportToCsv(tables, cursor, outputFolder+'/'+dirStructure['raw_csv'])
    #exportToParquet(tables, cursor, outputFolder+'/'+dirStructure['raw_parquet'])
    exportProcessedSurveys(cursor, outputFolder+'/'+dirStructure['survey_processed'])
    #exportFitbitSummary(cursor, outputFolder+'/'+dirStructure['fitbit_summary'])

def createOutputStructure(outputFolder:str, createFolder=False):
    """
    Method which creates the output folder (createFolder=True) and the directory
    structure inside it.
    """
    if createFolder:
        os.mkdir(outputFolder)

    # Create the directory structure inside the output folder.
    for k in dirStructure.keys():
        path = outputFolder+'/'+dirStructure[k]
        if not(os.path.isdir(path)):
            os.mkdir(outputFolder+'/'+dirStructure[k])

def exportToParquet(tables:list, cursor:pyathena.pandas.cursor, outputPrefix:str):
    """
    Method which exports all the data from the tables into a parquet file.
    """
    for table in tables:
        frame = cursor.execute('SELECT * FROM  {table}'.format(table=table)).as_pandas()
        frame.to_csv(outputPrefix+'/table_{table}.parquet'.format(table=table), index=False)

def exportToCsv(tables:list, cursor:pyathena.pandas.cursor, outputPrefix:str):
    """
    Method which exports all the data from the tables into a csv file.
    """
    for table in tables:
        frame = cursor.execute('SELECT * FROM  {table}'.format(table=table)).as_pandas()
        frame.to_csv(outputPrefix+'/table_{table}.csv'.format(table=table), index=False)

def exportProcessedSurveys(cursor:pyathena.pandas.cursor, outputPrefix:str):
    """
    Method which creates csv files for surveys based on their survey data.
    Note that the question text it fills out is extracted from the latest version of the survey.
    """

    """
    Given that survey names can change during the study, we look at surveyresults instead of surveydefinations
    to get the names of the surveys.
    """
    surveyNames = cursor.execute('select surveyname, surveykey from surveyresults group by surveyname, surveykey order by surveyname asc').as_pandas()

    query = """
        WITH surveyresult AS (
            SELECT surveyresultkey
            FROM surveyresults
            WHERE surveykey = '{key}'
        )
        SELECT surveyquestionresults.participantidentifier,
        (
            SELECT questiontext
            FROM surveydictionary
            WHERE resultidentifier = surveyquestionresults.resultidentifier
                AND surveykey = '{key}'
                AND surveyversion >= (
                    SELECT MAX(surveyversion) as max_version
                    FROM surveydictionary
                    WHERE surveykey = '{key}'
                    GROUP BY surveyname
                )
        ) AS question,
        surveyquestionresults.startdate,
        surveyquestionresults.enddate,
        surveyquestionresults.resultidentifier,
        surveyquestionresults.answers [ 1 ] AS answer
            FROM surveyquestionresults
        INNER JOIN surveyresult ON surveyresult.surveyresultkey = surveyquestionresults.surveyresultkey
    """
    for surveyName, surveyKey in zip(surveyNames['surveyname'], surveyNames['surveykey']):
        frame = cursor.execute(query.format(key=surveyKey)).as_pandas()
        frame.to_csv(outputPrefix+'/{survey}.csv'.format(survey=surveyName), index=False)

def exportFitbitSummary(cursor:pyathena.pandas.cursor, outputPrefix:str):
    """
    Generate and export fitbit summary data into csv files.
    """
    fa = Fitbit(cursor)
    fa.getActivity().to_csv(outputPrefix+'/activity.csv', index=False)
    fa.getHRV().to_csv(outputPrefix+'/hrv.csv', index=False)
    fa.getRestingHR().to_csv(outputPrefix+'/restinghr.csv', index=False)
    fa.getSleep().to_csv(outputPrefix+'/sleep.csv', index=False)

def getTables(cursor:pyathena.pandas.cursor)->pd.DataFrame:
    """
    Get all the tables from the database.
    """
    return cursor.execute('SHOW TABLES').as_pandas()

def E(message : str):
    """
    Utility method to raise an exception.
    """
    raise Exception(message)

if __name__ == '__main__':
    main(sys.argv)
