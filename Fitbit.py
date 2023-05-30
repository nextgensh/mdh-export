import pyathena

class Fitbit():
    """
    Methods which get various fitbit summary statistics.
    """
    def __init__(self, cursor:pyathena.pandas.cursor):
        self.cursor = cursor

    def getSleep(self):
        query = """
        SELECT participantidentifier,
        date_format(min(startdate), '%Y-%m-%d') as start_date,
        date_format(max(enddate),'%Y-%m-%d') as end_date,
        count(DISTINCT(date_format(startdate, '%Y-%m-%d'))) as days_recorded,
        count(participantidentifier) as sleep_sessions,
        CAST(split_part(CAST(max(enddate) - min(startdate) as varchar), ' ', 1) as INT) + 1 as calendar_days
            FROM fitbitsleeplogs WHERE duration > 0
            GROUP BY participantidentifier
            ORDER BY start_date ASC
        """

        return self.cursor.execute(query).as_pandas()

    def getActivity(self):
        query = """
        SELECT participantidentifier,
        date_format(min(date), '%Y-%m-%d') as start_date,
        date_format(max(date), '%Y-%m-%d') as end_date,
        count(date) as days_recorded,
        CAST(split_part(CAST(max(date) - min(date) as varchar), ' ', 1) as int) + 1 as calendar_days,
        AVG(calories) avg_calories,
        AVG(steps) avg_steps,
        AVG(spo2avg) avg_spo2,
        AVG(tempcore) avgtempcore,
        AVG(tempskin) avgtempskin,
        AVG(distance) avgdistance,
        AVG(activitycalories) avg_actcal
            FROM fitbitdailydata
            WHERE steps > 0
            GROUP BY participantidentifier
        """

        return self.cursor.execute(query).as_pandas()

    def getRestingHR(self):
        query = """
        SELECT participantidentifier,
        date_format(min(date), '%Y-%m-%d') as start_date,
        date_format(max(date), '%Y-%m-%d') as end_date,
        count(date) as days_recorded,
        CAST(split_part(CAST(max(date) - min(date) as varchar), ' ', 1) as int) + 1 as calendar_days,
        avg(restingheartrate) as average_resting_hr, min(restingheartrate) as min_resting_hr, max(restingheartrate) as max_resting_hr
            FROM fitbitrestingheartrates
            WHERE restingheartrate IS NOT NULL
            GROUP BY participantidentifier
        """

        return self.cursor.execute(query).as_pandas()

    def getHRV(self):
        query = """
        SELECT participantidentifier,
        date_format(min(date), '%Y-%m-%d') as start_date,
        date_format(max(date), '%Y-%m-%d') as end_date,
        count(date) as days_recorded,
        CAST(split_part(CAST(max(date) - min(date) as varchar), ' ', 1) as int) + 1 as calendar_days,
        avg(hrvdailyrmssd) as daily_avg_hrv, avg(hrvdeeprmssd) as deep_avg_hrv,
        min(hrvdailyrmssd) as daily_min_hrv, min(hrvdeeprmssd) as deep_min_hrv,
        max(hrvdailyrmssd) as daily_max_hrv, max(hrvdeeprmssd) as deep_max_hrv
            FROM fitbitdailydata
            WHERE hrvdailyrmssd IS NOT NULL
            GROUP BY participantidentifier
        """

        return self.cursor.execute(query).as_pandas()
