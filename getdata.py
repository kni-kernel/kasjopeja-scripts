import requests
import json

try:
    from pymongo import MongoClient
except ImportError:
    raise ImportError('PyMongo is not installed')


class MongoDB(object):
    def __init__(self, host='localhost', port=27017, database_name=None, collection_name=None):
        try:
            self._connection = MongoClient(host=host, port=port, maxPoolSize=200)
        except Exception as error:
            raise Exception(error)
        self._database = None
        self._collection = None
        if database_name:
            self._database = self._connection[database_name]
        if collection_name:
            self._collection = self._database[collection_name]

    def insert(self, post):
        post_id = self._collection.insert_one(post).inserted_id
        return post_id

wydzialy = ['wgig', 'wimiip', 'weaiiib', 'wieit', 'wimir', 'wggios', 'wggiis', 'wimic', 'wo', 'wmn', 'wwnig', 'wz', 'wms', 'wh', 'wfiis']

urlBase = 'https://syllabuskrk.agh.edu.pl/current_annual/magnesite/api/faculties/'

kierunkiDoPob = {}

w = wydzialy[len(wydzialy) - 1]
url = urlBase + '{}/study_plans'.format(w)

response = requests.get(url)
data = json.loads(response.text) if response.text is not None else None

if data is not None:
    for t in data['syllabus']['study_types']:
        levelsName = []
        for l in t['levels']:
            kierName = []
            for s in l['study_programmes']:
                name = s['url'].split('/')
                nameMain = name[len(name) - 1]
                kierName.append({'name': nameMain, 'shortName': s['name']})
            levelsName.append({'stopien': l['level'], 'kierunki': kierName})
        kierunkiDoPob[w] = levelsName

przedmiotyNaKier = []

for key, item in kierunkiDoPob.items():
    for i,stopnie in enumerate(item):
        for j,k in enumerate(stopnie['kierunki']):
            urlP = urlBase + '{}/study_plans/{}'.format(key, k['name'])
            responseP = requests.get(urlP)
            dataP = json.loads(responseP.text) if responseP.text is not None else None
            for sem in dataP['syllabus']['study_plan']['semesters']:
                for g in sem['groups']:
                    if 'modules' in g.keys():
                        for m in g['modules']:
                            przedmiotyNaKier.append({'name': m['name'], 'ects': m['ects_credits'],
                                'module': k['shortName'], 'semester': sem['number'], 
                                'hours': {h['name']:h['classes_hours'] for h in m['form_of_classes']}})
                    elif 'groups' in g.keys():
                        for go in g['groups']:
                            for mo in go['modules']:
                                print(mo)

print('[*] Pushing data to MongoDB ')
mongo_db = MongoDB(database_name='KasjopejaDB', collection_name=w)

for collection in przedmiotyNaKier:
    print('[!] Inserting - ', collection)
    mongo_db.insert(collection)