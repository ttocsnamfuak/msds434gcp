from google.cloud import aiplatform

def predict_custom_model_sample(endpoint: str, instance: dict, parameters_dict: dict):
    client_options = dict(api_endpoint="us-central1-prediction-aiplatform.googleapis.com")
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    from google.protobuf import json_format
    from google.protobuf.struct_pb2 import Value

    # The format of the parameters must be consistent with what the model expects.
    parameters = json_format.ParseDict(parameters_dict, Value())

    # The format of the instances must be consistent with what the model expects.
    instances_list = [instance]
    instances = [json_format.ParseDict(s, Value()) for s in instances_list]
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )

    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    predictions = response.predictions
    print("predictions")
    for prediction in predictions:
        print(" prediction:", dict(prediction))


predict_custom_model_sample(
    "projects/369021937856/locations/us-central1/endpoints/2786426347575050240",
    { "instance_key_1": "value", ... },
    { "parameter_key_1": "value", ... }
)



{
  "instances": [
    { “high”: “242.77”, “low”: “238.67”, “open”: “238.92”,“volume”: “5371057”,“adjclose”: “241.519”,“formated_date”: “7/30/10”,“SMA”: “235.67”,“Std_20”: “9.79”,“Band_1”: “225.67”,“Band_2”: “245.67”,“dist_from_mean”: “6.285”,“vix_data”: “24.1299”,“ON_returns_signal_down”: “1”,“ON_returns_signal_up”: “0”, “stock_move”: “Buy”}
  ]
}