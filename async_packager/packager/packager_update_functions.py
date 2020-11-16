import psycopg2
import psycopg2.extras
import requests
from datetime import datetime

import config as CONFIG

def db_connection():
    
    return psycopg2.connect(
        user=CONFIG.CUMULUS_DBUSER,
        host=CONFIG.CUMULUS_DBHOST,
        dbname=CONFIG.CUMULUS_DBNAME,
        password=CONFIG.CUMULUS_DBPASS
    )

#-----------------------------------------------------
# Update the download status directly using the database connection
# Default value of file=None allows a status update with or without a file
# i.e. update progress percent only, or update progress percent and add file URL
def updateStatus_db(id, status_id, progress, file=None):
    
    processing_end = None

    if progress == 100:
        now = datetime.now() # current date and time
        processing_end = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    try:
        conn = db_connection()
        c = conn.cursor()
        c.execute("""UPDATE download set progress = %s, status_id = %s, file=%s, 
            processing_end=%s WHERE id = %s""", 
            (progress, status_id, file, processing_end, id))
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        c.close()
        conn.close()

    return
#-----------------------------------------------------
# Update the download status using the API
# Default value of file=None allows a status update with or without a file
# i.e. update progress percent only, or update progress percent and add file URL
def updateStatus_api(id, status_id, progress, file=None):
    try:
        requests.put(
            CONFIG.CUMULUS_API_URL+'/development/cumulus/downloads/{id}',
            json = {
                "id"
                "status_id": status_id,
                "progress": int(progress)
            }
        )
    except Exception as e:
        print(e)

    return