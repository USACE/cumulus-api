import os
import requests
import json
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

apiBaseURL = 'https://cumulus-api.rsgis.dev'

start = '2020-11-01T17:00:00'
end   = '2020-12-10T17:00:00'

r = requests.get(f'{apiBaseURL}/cumulus/v1/products', verify=True)
products = r.json()

sql = ''

for product in products:          

    print(f"\n##### {product['name']} ##### ID: {product['id']}")

    r = requests.get(f"{apiBaseURL}/cumulus/v1/products/{product['id']}/files?before={end}&after={start}", verify=True)
    productFiles = r.json()

    if len(productFiles) > 0:

        sql += f"\n\n-- Product: {product['name']}  Count: {len(productFiles)}"
        sql += "\nINSERT INTO productfile (id, file, datetime, product_id) VALUES"

        last_pf = len(productFiles)

        for idx, pf in enumerate(productFiles):
            # print(record)        
            file = pf['file'].replace('https://api.rsgis.dev/', '')
            sql += f"\n('{pf['id']}', '{file}', '{pf['datetime']}', '{product['id']}')"
            
            # handle last set of values
            if idx+1 == last_pf:
                sql += ';'
            else:
                sql += ','

        
        print(sql)
    else:
        print('No product files.')

sql += '\n'

with open(f'{os.path.dirname(os.path.realpath(__file__))}/sql/31-seed_prodfiles.sql', 'w+') as outfile:
    print(f'\nWriting output to {outfile.name}')
    outfile.write(sql)

exit()
