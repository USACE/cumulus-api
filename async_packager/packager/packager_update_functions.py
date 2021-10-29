import requests
import config as CONFIG

#-----------------------------------------------------
# Update the download status using the API
# Default value of file=None allows a status update with or without a file
# i.e. update progress percent only, or update progress percent and add file URL
def update_status_api(id, status_id, progress, file=None):
    try:
        r = requests.put(
            f'{CONFIG.CUMULUS_API_URL}/downloads/{id}?key={CONFIG.APPLICATION_KEY}',
            json={"id":id, "status_id": status_id, "progress": int(progress), "file": file}
        )
    except Exception as e:
        print(e)

    return