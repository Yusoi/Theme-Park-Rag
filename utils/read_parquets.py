import duckdb

con = duckdb.connect()

# First person to enter the park out of every single day along with their gender

df = con.execute("""
    SELECT e.id, e.datetime AS time_of_entry, c.gender
    FROM read_parquet('events/**/*.parquet') e
    JOIN read_parquet('customers/**/*.parquet') c
    ON e.id = c.id
    WHERE e.event_type = 'park_entry'
    ORDER BY e.datetime
    LIMIT 1;
""").df()

print(df.head())
