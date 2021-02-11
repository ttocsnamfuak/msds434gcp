


from google.cloud import automl

# TODO(developer): Uncomment and set the following variables
project_id = 'my-project-434-gcp'
# compute_region = 'COMPUTE_REGION_HERE'
model_display_name = 'google_automl_20210210105125'
inputs = {'adjclose': '574.78', 'Band_1': '574.0373494475505',
        'Band_2': '586.5313028961996', 'dist_from_mean': '-4.764428710937523', 'formatted_date': '2014-09-29', 'high': '576.60693359375',
        'low': '569.6061401367188', 'ON_returns_signal_down': '1', 'ON_returns_signal_up': '0', 'open': '570.1845703125'}

#from google.cloud import automl_v1beta1 as automl
#import google.cloud.automl_v1beta1 as automl
#f

#client = automl.TablesClient(project=project_id)
# Get the full path of the model.
model_full_id = automl.AutoMlClient.model_path(
    project_id, "us-central1", model_display_name
)

print(model_full_id)

client = automl.PredictionServiceClient()

response = client.predict(
        name=model_full_id, params=inputs)


print("Prediction results:")

for result in response.payload:
    print(
        "Predicted class name: {}".format(result.tables.value)
    )
    print("Predicted class score: {}".format(result.tables.score))

    if feature_importance:
        # get features of top importance
        feat_list = [
            (column.feature_importance, column.column_display_name)
            for column in result.tables.tables_model_column_info
        ]
        feat_list.sort(reverse=True)
        if len(feat_list) < 10:
            feat_to_show = len(feat_list)
        else:
            feat_to_show = 10

        print("Features of top importance:")
        for feat in feat_list[:feat_to_show]:
            print(feat)


#from google.cloud import automl

# TODO(developer): Uncomment and set the following variables
# project_id = "YOUR_PROJECT_ID"
# model_id = "YOUR_MODEL_ID"
# file_path = "path_to_local_file.jpg"

#

# Get the full path of the model.
#model_full_id = automl.AutoMlClient.model_path(
#    project_id, "us-central1", model_id
#)

# Read the file.
#with open(file_path, "rb") as content_file:
#    content = content_file.read()

#image = automl.Image(image_bytes=content)
#payload = automl.ExamplePayload(image=image)

# params is additional domain-specific parameters.
# score_threshold is used to filter the result
# https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#predictrequest
#params = {"score_threshold": "0.8"}

#request = automl.PredictRequest(
 #   name=model_full_id,
 #   payload=payload,
 #   params=params
#)
#

#print("Prediction results:")
#for result in response.payload:
#    print("Predicted class name: {}".format(result.display_name))
#    print("Predicted class score: {}".format(result.classification.score))