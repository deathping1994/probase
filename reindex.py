from elasticsearch import Elasticsearch,helpers

try:
    body= {}
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    # es.create(index="github",body=body,doc_type="projects")
    print ("index Created, Starting reindexing")
    print helpers.reindex(es,source_index="github_repos",chunk_size=10000,target_index="github")

except Exception as e:
    print str(e)
    pass
__author__ = 'gaurav'
