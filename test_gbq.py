import pandas_gbq

# TODO: Set project_id to your Google Cloud Platform project ID.
project_id = "my-project-434-gcp"

query = "SELECT avg(volume) FROM `my-project-434-gcp.google2.googleData` LIMIT 1000"

sql = query
df = pandas_gbq.read_gbq(sql, project_id=project_id)
