from datetime import date, timedelta, datetime
import datetime
import random
import uuid

subs = [
    '57329df6-9f7a-4dad-9383-4633b452efab',
    'f320df83-e2ea-4fe9-969a-4e0239b8da51',
    '89aa1e13-041a-4d15-9e45-f76eba3b0551',
    '405ab7e1-20fc-4d26-a074-eccad88bf0a9',
    '81c77210-6244-46fe-bdf6-35da4f00934b',
    'f056201a-ffec-4f5b-aec5-14b34bb5e3d8',
    '9effda27-49f7-4745-8e55-fa819f550b09',
    '37407aba-904a-42fa-af73-6ab748ee1f98',
    'c0fd72ae-cccc-45c9-ba1d-4353170c352d',
    'be549c16-3f65-4af4-afb6-e18c814c44dc',
    '8dde311e-1761-4d3f-ac13-a458d17fe432',
]

watersheds = [  
    '01313583-8fed-4235-8cf2-df5fe23b4b2a',
    '03206ff6-fe91-426c-a5e9-4c651b06f9c6',
    '048ce853-6642-4ac4-9fb2-81c01f67a85b',
    '0573081e-c72c-4bf9-9709-7f62ecd80a64',
    '070204a3-66d9-471c-bd6e-ab59ea0858bb',
    '074ff6ed-69b1-4958-87a5-9cd68fde7030',
    '08ee0918-b869-46c5-b9fd-e02f88ceff64',
    '0c06e6d6-68f3-4943-a95e-22ef82696e7e',
    '0d53c4da-8712-4e99-9824-1695e3e1966c',
    '0f065e6a-3380-4ac3-b576-89fae7774b9f',
    '11cddcb1-aca6-4398-b5bd-f10e19826c16',
    '11e92768-81ed-4b62-9179-1f010ac9bb97',
    '14c56e44-c8aa-4f89-a226-3e99e181d522',
    '14eb04fc-7eb8-4322-a2a0-999e371ca989',
    '151d8075-a6b7-45f2-92ed-360b4f7f7b47',
    '1572c0a6-e9b9-420a-85dc-ae9d9ac8f958',
    '15e50ede-337b-4bbf-a6fa-1be57d1b8715',
    '1731a851-8813-458f-8e3c-ef7e0bb0a285',
    'ec1494d2-bcca-437c-9a3f-bea84f0b63db',
    '1a629fac-82c9-4b3e-b7fc-6a891d944140'
]

products = [

'30a6d443-80a5-49cc-beb0-5d3a18a84caa',
'7c7ba37a-efad-499e-9c3a-5354370b8e9e',
'0ac60940-35c2-4c0d-8a3b-49c20e455ff5',
'5e6ca7ed-007d-4944-93aa-0a7a6116bdcd',
'1ba5498c-d507-4c82-a80b-9b0af952b02f',
'c500f609-428f-4c38-b658-e7dde63de2ea',
'002125d6-2c90-4c24-9382-10a535d398bb',
'64756f41-75e2-40ce-b91a-fda5aeb441fc',
'6357a677-5e77-4c37-8aeb-3300707ca885',
'62e08d34-ff6b-45c9-8bb9-80df922d0779',
'e4fdadc7-5532-4910-9ed7-3c3690305d86'
]

def random_sub():
    return subs[random.randrange(len(subs))]

def random_watershed():
    return watersheds[random.randrange(len(watersheds))]

def random_product():
    return products[random.randrange(len(products))]


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = datetime.datetime(2021, 3, 25, 12, 0, 0)
end_date = datetime.datetime(2021, 10, 20, 12, 0, 0)


dl_sql = 'INSERT into cumulus.download (id, datetime_start, datetime_end, progress, status_id, watershed_id, file, processing_start, processing_end, sub) VALUES\n'
dl_prod_sql = 'INSERT into cumulus.download_product (download_id, product_id) VALUES\n'

for single_date in daterange(start_date, end_date):

    # print(single_date.strftime("%Y-%m-%d %H:%I:%M")) 

    # Multiple downloads per day
    for x in range(0,20):
    
        download_id = str(uuid.uuid4())
        datetime_start = (single_date-timedelta(hours=random.randint(3, 168))).strftime("%Y-%m-%d %H:%I:%M")
        datetime_end = (single_date+timedelta(days=3)).strftime("%Y-%m-%d %H:%I:%M")
        progress = 100
        status_id = '94727878-7a50-41f8-99eb-a80eb82f737a'
        watershed_id = random_watershed()
        file = 'cumulus/test-watershed/download.dss'
        processing_start = single_date.strftime("%Y-%m-%d %H:%I:%M")
        processing_end = (single_date+timedelta(minutes=random.randint(1, 5))).strftime("%Y-%m-%d %H:%I:%M")
        sub = random_sub()

        dl_sql += "('{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}'),\n".format(download_id, datetime_start, datetime_end, progress, status_id, watershed_id, file, processing_start, processing_end, sub)

        product_id = random_product()
        dl_prod_sql += "('{}', '{}'),\n".format(download_id, product_id)


print('ALTER TABLE cumulus.download DISABLE TRIGGER notify_new_download;\n')

# semi-colon on last line
dl_sql = dl_sql[0:-2]+';'
print(dl_sql)

print('\n\n')

# semi-colon on last line
dl_prod_sql = dl_prod_sql[0:-2]+';'
print(dl_prod_sql)

print('\n')

# Not sure why Postgres won't set "progress", "file" or "processing_end" since I am specifying the values above
print("UPDATE cumulus.download SET progress = {};".format(progress))
print("UPDATE cumulus.download SET file = '{}';".format(file))
print("UPDATE cumulus.download SET processing_end = processing_start + ({} * interval '1 minute');".format(random.randint(1, 5)))

print('\nALTER TABLE cumulus.download DISABLE TRIGGER notify_new_download;')
