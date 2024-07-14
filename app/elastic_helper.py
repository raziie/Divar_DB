from elasticsearch import Elasticsearch
from app.mysql_db import *
import datetime



class ElasticSearchDB:
    def __init__(self):
        password = Config.ELASTIC_PASS
        self.elastic_client = Elasticsearch(
            hosts=['http://localhost:9200/'],
            http_auth=('elastic', 'tFWtV627')
        )

        # Test the connection
        if self.elastic_client.ping():
            print("Connected to Elasticsearch")
        else:
            print("Could not connect to Elasticsearch")

        # define index
        self.index_name = 'advertisements'

        # create index mapping (schema type that data is saved in)
        self.index_mapping = {
            'mappings': {
                'properties': {
                    'AdID': {'type': 'integer'},
                    'Title': {'type': 'text'},
                    'Price': {'type': 'float'},
                    'AdCatID': {'type': 'integer'},
                    'DaysPast': {'type': 'text'},
                    'ImagePath': {'type': 'keyword'},
                    'statID': {'type': 'integer'}
                }
            }
        }

        self.counter = 0
        self.create_index()
        # self.create_initial_documents()

    def create_index(self):
        if not self.elastic_client.indices.exists(index=self.index_name):
            # self.elastic_client.indices.delete(index=self.index_name)
            self.elastic_client.indices.create(index=self.index_name, body=self.index_mapping)
            print(f'Index "{self.index_name}" created')
            self.create_initial_documents()

    # initial documents where all advertises are added to elastic
    def create_initial_documents(self):
        recent_ads = execute_read_query("SELECT DISTINCT(Advertise.AdID) AS AdID, AdCatID, Title, Price, CreatedAt ,"
                                        "Images.ImagePath FROM divar.Advertise LEFT JOIN divar.Images "
                                        "ON Advertise.AdID = Images.AdID Order BY CreatedAt DESC", True)

        # print(len(recent_ads))
        # print(recent_ads)

        for i in range(len(recent_ads)):
            adStat = execute_read_query("SELECT * FROM AdStatus WHERE AdStatus.AdID = {}".
                                        format(recent_ads[i]['AdID']), False)
            # print(adStat)
            delta = datetime.datetime.now() - recent_ads[i]['CreatedAt']
            recent_ads[i]['DaysPast'] = delta.days
            recent_ads[i]['statID'] = adStat['statID']
            del recent_ads[i]['CreatedAt']
            if recent_ads[i]['ImagePath'] is None:
                recent_ads[i]['ImagePath'] = '0.png'

            self.counter += 1
            self.elastic_client.index(index=self.index_name, body=recent_ads[i])
            print(f'Document {i} inserted.')

    def update_create_doc(self, doc):
        self.elastic_client.index(index=self.index_name, id=str(self.counter), body=doc)

    def search_query(self, searched_str, category, price_range, photo, is_admin):
        print('fffffffffffffffffffff')
        s_query = extract_query(searched_str, category, price_range, photo, is_admin)
        search_results = self.elastic_client.search(index=self.index_name, body=s_query)

        # print('search_results', search_results)
        result_docs = []
        # print('in elastic search file:')
        for hit in search_results['hits']['hits']:
            # print('one:')
            # print(hit['_source'])
            result_docs.append(hit['_source'])

        return result_docs


def extract_query(searched_str, in_category, price_range, photo, is_admin):
    print('searched str: ', searched_str, 'category: ', in_category, 'price_range: ',
          price_range, 'photo: ', photo)
    query = {
        'query': {
            'bool': {
                'filter': []
            }
        },
        "from": 0, "size": 1000
    }

    if searched_str != '':
        query['query']['bool']['filter'].append({'match': {'Title': searched_str}})

    if in_category != -1:
        query['query']['bool']['filter'].append({'term': {'AdCatID': in_category}})

    if photo != '':
        query['query']['bool']['filter'].append({'wildcard': {'ImagePath': photo}})

    if not is_admin:
        query['query']['bool']['filter'].append({'term': {'statID': 1}})

    min_price, max_price = price_range
    if min_price is None:
        min_price = float(0)
    if max_price is None:
        max_price = float(100000000000)

    query['query']['bool']['filter'].append({'range': {'Price': {'gte': float(min_price), 'lte': float(max_price)}}})

    if len(query['query']['bool']['filter']) == 0:
        query = {'query': {'match_all': {}}, "from": 0, "size": 1000}

    # print(query)

    return query
