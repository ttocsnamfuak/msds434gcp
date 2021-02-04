import gcloud
from gcloud import storage

client = storage.Client()
bucket = client.get_bucket('my-new-bucket-holyshit')
blob = bucket.blob('my-test-file2.txt')
