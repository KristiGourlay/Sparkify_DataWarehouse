import configparser

# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

ARN = config['IAM_ROLE']['ARN']
LOG_DATA, LOG_JSONPATH, SONG_DATA = config['S3'].values()


# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
    CREATE TABLE IF NOT EXISTS staging_events
        (artist varchar NULL,
        auth varchar NULL,
        first_name varchar NULL,
        gender varchar NULL,
        item_in_session varchar NULL,
        last_name varchar NULL,
        length varchar NULL,
        level varchar NULL,
        location varchar NULL,
        method varchar NULL,
        page varchar NULL,
        registration varchar NULL,
        session_id integer NOT NULL SORTKEY DISTKEY,
        song varchar NULL,
        status varchar NULL,
        ts bigint NOT NULL,
        user_agent varchar NULL,
        user_id integer NULL)
""")

staging_songs_table_create = ("""
    CREATE TABLE IF NOT EXISTS staging_songs
        (num_songs integer NULL,
        artist_id varchar NULL,
        artist_latitude varchar NULL,
        artist_longitude varchar NULL,
        artist_location varchar NULL,
        artist_name varchar NULL,
        song_id varchar NOT NULL SORTKEY DISTKEY,
        title varchar NULL,
        duration float NULL,
        year integer NULL)
""")

songplay_table_create = ("""
    CREATE TABLE IF NOT EXISTS songplays
        (songplay_id integer IDENTITY (1,1) PRIMARY KEY,
        start_time timestamp NOT NULL,
        user_id varchar,
        level varchar NOT NULL,
        song_id varchar,
        artist_id varchar,
        session_id integer NOT NULL,
        location varchar,
        user_agent varchar)
""")

user_table_create = ("""
    CREATE TABLE IF NOT EXISTS users
        (user_id integer NOT NULL PRIMARY KEY,
        first_name varchar,
        last_name varchar,
        gender varchar,
        level varchar)
""")

song_table_create = ("""
    CREATE TABLE IF NOT EXISTS songs
        (song_id varchar NOT NULL PRIMARY KEY,
        title varchar,
        artist_id varchar,
        year integer,
        duration float)
""")

artist_table_create = ("""
    CREATE TABLE IF NOT EXISTS artists
        (artist_id varchar NOT NULL PRIMARY KEY,
        name varchar,
        location varchar,
        latitude Decimal(8,6),
        longitude Decimal(9, 6))
""")

time_table_create = ("""
    CREATE TABLE IF NOT EXISTS time
        (start_time timestamp NOT NULL PRIMARY KEY,
        hour integer,
        day integer,
        week integer,
        month integer,
        year integer,
        weekday integer)
""")

# STAGING TABLES

staging_events_copy = ("""
COPY staging_events FROM '{}'
CREDENTIALS 'aws_iam_role={}'
REGION 'us-west-2'
FORMAT AS json '{}'
""").format(LOG_DATA, ARN, LOG_JSONPATH)

staging_songs_copy = ("""
COPY staging_songs FROM '{}'
CREDENTIALS 'aws_iam_role={}'
REGION 'us-west-2'
JSON 'auto' TRUNCATECOLUMNS
""").format(SONG_DATA, ARN)

# FINAL TABLES

songplay_table_insert = (""" INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT
    TIMESTAMP 'epoch' + e.ts/1000 * INTERVAL '1 second',
    e.user_id,
    e.level,
    s.song_id,
    s.artist_id,
    e.session_id,
    e.location,
    e.user_agent
FROM staging_events AS e
JOIN staging_songs AS s
    ON e.song = s.title
    AND e.artist = s.artist_name
WHERE e.page = 'NextSong'

""")



user_table_insert = (""" INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT
    user_id,
    first_name,
    last_name,
    gender,
    level
FROM staging_events
WHERE page = 'NextSong'

""")

song_table_insert = (""" INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT
    song_id,
    title,
    artist_id,
    year,
    duration
FROM staging_songs

""")

artist_table_insert = (""" INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT
    artist_id,
    artist_name,
    artist_location,
    artist_latitude,
    artist_longitude
FROM staging_songs

""")


time_table_insert = (""" INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT
     TIMESTAMP 'epoch' + ts/1000 * INTERVAL '1 second' AS start_time,
     EXTRACT(hour FROM start_time),
     EXTRACT(day FROM start_time),
     EXTRACT(week FROM start_time),
     EXTRACT(month FROM start_time),
     EXTRACT(year FROM start_time),
     EXTRACT(weekday FROM start_time)
FROM staging_events
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
