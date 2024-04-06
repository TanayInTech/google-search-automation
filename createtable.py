

# Create table if not exists
create_table_query = '''
CREATE TABLE IF NOT EXISTS cricket_news(
    id SERIAL PRIMARY KEY,
    keyword TEXT,
    year INT,
    result_text TEXT,

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''
