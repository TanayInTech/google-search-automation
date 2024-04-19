

# Create table if not exists
create_table_query = '''
CREATE TABLE IF NOT EXISTS IPLnews1(
    id SERIAL PRIMARY KEY,
    keyword TEXT,
    year INT,
    result_text TEXT,
    execution_time TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
)
'''