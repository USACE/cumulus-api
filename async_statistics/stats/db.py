import psycopg2

import config as CONFIG

def db_connection():
    
    return psycopg2.connect(
        user=CONFIG.CUMULUS_DBUSER,
        host=CONFIG.CUMULUS_DBHOST,
        dbname=CONFIG.CUMULUS_DBNAME,
        password=CONFIG.CUMULUS_DBPASS
    )

def get_basin(basin_id):
    
    try:
        conn = db_connection()
        c = conn.cursor()
        c.execute(
            """SELECT ST_AsText(geometry) AS geometry
               FROM v_basin_5070
               WHERE id=%s 
            """, 
            (basin_id,)
        )
        return c.fetchone()
    except Exception as e:
        print(e)
    finally:
        c.close()
        conn.close()
    
    return
