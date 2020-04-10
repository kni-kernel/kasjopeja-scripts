import requests
import json

try:
    from pymongo import MongoClient
except ImportError:
    raise ImportError('PyMongo is not installed')

class MongoDBClient(object):
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

departments = ['wgig', 'wimiip', 'weaiiib', 'wieit', 'wimir', 'wggios', 'wggiis', 'wimic', 'wo', 'wmn', 'wwnig', 'wz', 'wms', 'wh', 'wfiis']

urlBase = 'https://syllabuskrk.agh.edu.pl/current_annual/magnesite/api/faculties/'

coursesForDownload = {}

w = departments[len(departments) - 1]
url = urlBase + '{}/study_plans'.format(w)

headers = {'Accept-Language': 'pl'}
response = requests.get(url, headers=headers)
data = json.loads(response.text) if response.text is not None else None

if data is not None:
    for t in data['syllabus']['study_types']:
        levelsName = []
        for l in t['levels']:
            courseName = []
            for s in l['study_programmes']:
                name = s['url'].split('/')
                nameMain = name[len(name) - 1]
                courseName.append({'name': nameMain, 'shortName': s['name']})
            levelsName.append({'level': l['level'], 'courseName': courseName})
        coursesForDownload[w] = levelsName

subjectForCourse = []

for key, item in coursesForDownload.items():
    for i,singleLevel in enumerate(item):
        for j,k in enumerate(singleLevel['courseName']):
            urlP = urlBase + '{}/study_plans/{}'.format(key, k['name'])
            responseP = requests.get(urlP, headers=headers)
            dataP = json.loads(responseP.text) if responseP.text is not None else None
            for sem in dataP['syllabus']['study_plan']['semesters']:
                for g in sem['groups']:
                    if 'modules' in g.keys():
                        for m in g['modules']:
                            subjectForCourse.append({'name': m['name'], 'ects': m['ects_credits'],
                                'fieldOfStudy': k['shortName'], 'semester': sem['number'], 
                                'hours': {h['name'].lower():h['classes_hours'] for h in m['form_of_classes']}})
                    elif 'groups' in g.keys():
                        for go in g['groups']:
                            for mo in go['modules']:
                                print(mo)

print('[*] Pushing data to MongoDB ')
mongodbClient = MongoDBClient(database_name='KasjopejaDB', collection_name=w)

for collection in subjectForCourse:
    print('[!] Inserting - ', collection)
    mongodbClient.insert(collection)