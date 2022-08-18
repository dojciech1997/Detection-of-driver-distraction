# Detection-of-driver-distraction
Real-time detection of behavioral patterns using AWS

## Problem description

  The proposed approach is based on the concept of the Internet of Things (IoT), in which cameras, which are sensors of the cloud edge node, collect and send data to Amazon Web Services platforms. The media streams are then analyzed in real time to detect behavioral patterns. The calculations are supported by built-in service tools with efficient hardware units. The scope of the work also covers issues related to serverless architecture and artificial neural networks. The project structure includes a graphic interface that allows you to run the mobile application via the HTTP protocol.
 
System architecture:

![obrazek1](https://user-images.githubusercontent.com/49471079/185388617-9e585ca5-1d36-4da5-bc9e-970e429d5eb9.png)

UML diagram:

![obrazek2](https://user-images.githubusercontent.com/49471079/185389235-de2d09a6-2ba1-4896-b864-24c7802fb722.png)

## Requirements

Functional requirements:
• The functions start analyzing the data as soon as it detects a sent request
from the level of the mobile application panel.
• The system collects and processes data from multiple IoT devices in parallel.
• Deep neural network models make inference based on one frame per second, providing real-time information about the detected pattern.
• The user has access to the obtained predictions and its metadata in a dynamic table.
• The user is informed about the threat when distraction is detected via the MQTT protocol.
• Automatic termination of the system operation takes place when the transmission of samples by the last active sensor of the IoT system ceases.

Non-functional requirements:
• The project assumes launching the transmission via Kinesis Video Stream before sending the Lambda function initiation request from the application's user panel.
• The sensors should transmit the image with a frequency of 20 [fps]. The system analyzes every 20 frames, i.e. one per second, which ensures real-time operation of the system.
• Continuity of internet connection with sufficiently high bandwidth is required for the proper operation of the project tools.
• Cameras must be mounted on the passenger side and cover a sufficiently wide area for the driver's head and hands. They should be mounted high so that the passenger does not obstruct the camera's field of view.
• The training data was collected during the daylight hours, so the system should be tested before dark for more accurate predictions.
• The image resolution should be at least 1080p.

## Data samples and ResNet model

The collection consists of 22,424 files in .jpg format and is available on the platform
www.kaggle.com [5]. The files were placed in the S3 container in the appropriate folders. Additionally, the set of training samples includes 50 self-made shots, 5 for each label.
LST files have been created. In the next step, the photos were converted to the application/x-recordio format. The Sagemaker Notebook Instance tool was used to pre-process the data and to create and train the model.
Test data for classifier evaluation were also obtained from the State Farm collection. The collection consists of 79,726 shots, 200 were selected for the project - 20 for each label, which were then manually classified. In addition, a second separate test set was created, consisting of 50 photos taken with the Xiaomi Imilab Webcam.

The photos are divided into 10 categories:
• safe driving
• texting - right hand
• talking on the phone - right hand
• texting - left hand
• talking on the phone - left hand
• operating the radio
• drinking
• reaching behind
• correcting hair and makeup in the front mirror 
• talking to passenger

ResNet model architecture:

<img width="381" alt="Obraz3" src="https://user-images.githubusercontent.com/49471079/185390628-ffbfd628-c733-40f8-b8ba-023e03acbcaf.png">

## Initialization of Lambda functions

The created user interface ensures Lambda function initialization for everyone
from IoT sensors. In order for the system to function properly, at least one active multimedia data stream realized with the Kinesis Video Stream tool is required.
Otherwise, the application will terminate immediately. Communication between the Lambda functions and the mobile application was realized via AWS API Gateway. The REST API interface was created and the POST method for data transfer was defined. Reports are received by providing two values: the name of the person behind the wheel and a unique password. After entering the passenger data and password, the request is sent by clicking the Call API button. After the end of the algorithm execution by the last Lambda function, the application user displays a message with the content informing about the completed video transmission. If the password is incorrect, the message "Wrong password!"

![Obraz4](https://user-images.githubusercontent.com/49471079/185391314-cbc74e76-b82e-4cad-a5bf-2c2fd98d9e5a.png)

## Implementation of system's structure

The image was transmitted in real time using the Kinesis Video Stream tool and the Xiaomi Imilab Webcam. In order for the platform to be able to obtain an image, it was necessary to install and configure the GStreamer Plugin on a VMWare 16 Player virtual machine with Linux Mint 19 operating system. It simplifies the integration of both components by managing the multimedia stream and encoding it to the .H264 format supported by the Kinesis Video Streams Producer development toolkit. SDK. However, the implemented GStreamer plugin causes a slight delay in the transmission of a multimedia data stream. They were reduced to around 5 seconds by switching to Mozilla Firefox, which has an internal video rendering implementation. In line with the serverless structure concept, Lambda functions were created, which due to the quick response during initialization, good bandwidth and stability of the AWS platform constitute a good tool for the implementation of a real-time system, as proved in [52]. Libraries, in this case Numpy and OpenCV, were added as layers, the so-called Lambda Layers by downloading packages to an Amazon Linux 2 virtual machine using an EC2 instance. Global environment variables have been defined: system boot password, Sagemaker endpoint name and Kinesis Video Stream pipe name. Lambda functions are triggered automatically when the start is initiated
from the mobile application via the REST API. 10GB of memory has been manually allocated to the functions to minimize the "cold boot" and to increase the processing speed of the received data, according to [52]. Python version 3.7 interpreter selected. The timeout has been set to a maximum of 15 minutes. Access rights were granted to the following services: AWS Kinesis Video Stream, AWS Sagemaker, AWS S3, AWS DynamoDB and AWS IoT Core. Due to the imposed 20fps limit, artificial intelligence algorithms analyze every 20 frames to keep the system running without latency. The image is decoded and converted into a bit array. Then the functions, using the saved neural network model, make inferences based on the image from the cameras. In case of detecting a distracting pattern of the driver, the prediction together with the time of its detection it is saved to the dynamic table DynamoDB. The data is stored in it for a maximum of 24 hours, which ensures economical storage of memory.

## Alerts

<img width="454" alt="Obraz6" src="https://user-images.githubusercontent.com/49471079/185391828-a042263c-40c9-409d-addf-7115e5c616f9.png">

The user is informed about the threat by means of AWS IoT Core, where the MQTT message broker is available. It acts as the server that clients connect to to publish information. The data is displayed in it in real time. The message is sent by the sender, i.e. one of the Lambda functions, to the proxy. The recipient can view published messages by subscribing to a topic called distraction-alerts. After the transmission is completed, the functions are interrupted, and the frames from each of the IoT sensors with the label displayed in the upper left corner are saved in the S3 container in the .mp4 format files - this enables the system operation analysis.

<img width="284" alt="Obraz5" src="https://user-images.githubusercontent.com/49471079/185391909-9aa941a0-3420-440f-8ca8-869c5930a6a7.png">

