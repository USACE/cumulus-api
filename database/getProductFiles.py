import os
import requests
import json
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

apiBaseURL = 'https://cumulus-api.rsgis.dev'

start = '2018-10-01T01:00:00'
end   = '2021-03-31T23:00:00'

r = requests.get(f'{apiBaseURL}/products', verify=True)
products = r.json()

sql = ''

for product in products:

    if product['name'] not in ['wpc_qpf_2p5km']:         

        print(f"\n##### {product['name']} ##### ID: {product['id']}")

        r = requests.get(f"{apiBaseURL}/products/{product['id']}/files?before={end}&after={start}", verify=True)
        productFiles = r.json()

        if len(productFiles) > 0:

            sql += f"\n\n-- Product: {product['name']}  Count: {len(productFiles)}"
            sql += "\nINSERT INTO productfile (id, file, datetime, product_id, version) VALUES"

            last_pf = len(productFiles)

            for idx, pf in enumerate(productFiles):
               
                # print(record)        
                file = pf['file'].replace('https://api.rsgis.dev/', '')
                sql += f"\n('{pf['id']}', '{file}', '{pf['datetime']}', '{product['id']}', '1111-11-11T11:11:11.11Z')"
                
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
