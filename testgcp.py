import gcloud
from gcloud import storage
import pandas as pd


my_df = pd.DataFrame(data=[{1,2,3},{4,5,6}],columns=['a','b','c']).to_csv(sep=",", index=False, quotechar='"', encoding="UTF-8")

client = storage.Client()
bucket = client.get_bucket('my-new-bucket-holyshit')
blob = bucket.blob('my-test-file4.csv')

blob.upload_from_string(data=my_df)

