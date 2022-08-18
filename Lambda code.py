import boto3
import cv2
from botocore.exceptions import ClientError
import numpy as np
import time
import json
import os

def lambda_handler(event, context):
    data = event['name'] +' '+ event['password']
    if event['password'] == os.environ['PASSWORD']:
        region = boto3.Session().region_name
        client = boto3.resource('dynamodb')
        table = client.Table("dynamodb-distraction")
        s3 = boto3.client('s3')
        runtime=boto3.Session().client('sagemaker-runtime')
        kvs = boto3.client("kinesisvideo")
        endpoint = kvs.get_data_endpoint(
            APIName="GET_HLS_STREAMING_SESSION_URL",
            StreamName=os.environ['STREAM_NAME']
        )['DataEndpoint']
        kvam = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint)
        url = kvam.get_hls_streaming_session_url(
            StreamName=os.environ['STREAM_NAME'],
            PlaybackMode="LIVE"
        )['HLSStreamingSessionURL']
        mqtt = boto3.client('iot-data', region_name='eu-central-1')
        cap = cv2.VideoCapture(url)
        labels = ['drinking', 'hair_and_makeup', 'operating_the_radio', 'reaching_behind', 'safe_driving', 
        'talking_left_hand', 'talking_right_hand', 'talking_to_passenger', 'texting_left_hand', 'texting_right_hand']
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) 
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_id = 0
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out2 = cv2.VideoWriter('/tmp/output.avi', fourcc, 2, (int(width), int(height)))
        while True:
            frame_id += 1
            success,img = cap.read()
            if not success:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            if cv2.waitKey(1) == ord('q'):
                break
            if frame_id % 20 == 0 or frame_id == 1:
                success2, encoded_image = cv2.imencode('.jpg', img)
                new_img = encoded_image.tobytes()
                new_img = bytearray(new_img)
                prediction = runtime.invoke_endpoint(EndpointName=os.environ['SAGEMAKER_ENDPOINT'], ContentType= 'application/x-image', Body=new_img)
                probabilities = json.loads(prediction['Body'].read().decode())
                predicted_category_index = np.argmax(probabilities) 
                confidence = probabilities[predicted_category_index]
                timestr = time.strftime("%r")
                if predicted_category_index != 4:
                    metadata = timestr+' '+str(event['name'])+' frame: '+str(frame_id)
                    table.put_item(Item= {'frame': metadata,'prediction':  labels[predicted_category_index]})
                    mqtt.publish(    
                      topic='distraction-alerts',
                      qos=0,
                      payload=json.dumps({"Be careful!":labels[predicted_category_index]})
                    )
                timestr = time.strftime("%r")
                print("Time of detection: ", timestr)
                print(f"Result: label -  {labels[predicted_category_index]}, probability - {confidence}")
        cap.release()
        out2.release()
        cv2.destroyAllWindows()
        timestr = time.strftime("%Y%m%d-%H%M%S")
        with open("/tmp/output.avi", "rb") as f:
            s3.upload_fileobj(f, "kinesis-distraction-outputs", "{}.avi".format(timestr))
        return {
            'statusCode': 0,
            'body': json.dumps('Stream ended for ' + event['name'])
        }
    else:
        return {
            'statusCode': 0,
            'body': json.dumps('Wrong password!')
        }