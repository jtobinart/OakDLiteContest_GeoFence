#MegaDetector
I am working on getting the MegaDetector blob file to function correctly on the Oak-D Lite. Some of the files are too large to upload to GitHub. I have uploaded them instead to my [Google Drive](https://drive.google.com/drive/folders/1LWEt41xBAvc3OU689Z-VDh1WX_gBRFzI?usp=sharing).

There are seven faster_RCNN transformations config files to use. I am not sure which version of TensorFlow was used so I am testing each one. The following is published on [OpenVino](https://docs.openvino.ai/latest/openvino_docs_MO_DG_prepare_model_convert_model_tf_specific_Convert_Object_Detection_API_Models.html)'s documentation.
>faster_rcnn_support.json for Faster R-CNN topologies from the TF 1.X models zoo trained with TensorFlow* version up to 1.6.X inclusively

>faster_rcnn_support_api_v1.7.json for Faster R-CNN topologies trained using the TensorFlow* Object Detection API version 1.7.0 up to 1.9.X inclusively

>faster_rcnn_support_api_v1.10.json for Faster R-CNN topologies trained using the TensorFlow* Object Detection API version 1.10.0 up to 1.12.X inclusively

>faster_rcnn_support_api_v1.13.json for Faster R-CNN topologies trained using the TensorFlow* Object Detection API version 1.13.X

>faster_rcnn_support_api_v1.14.json for Faster R-CNN topologies trained using the TensorFlow* Object Detection API version 1.14.0 up to 1.14.X inclusively

>faster_rcnn_support_api_v1.15.json for Faster R-CNN topologies trained using the TensorFlow* Object Detection API version 1.15.0 up to 2.0

>faster_rcnn_support_api_v2.0.json for Faster R-CNN topologies trained using the TensorFlow* Object Detection API version 2.0 or higher


I have converted the Tensorflow frozen file into an Intermediate Representation (IR). The MegaDetector utilizes TensorFlow.
| MODEL | STATUS | COMMENTS |
| ------------- | ------------- | ------------- |
| IR_tf_1.0 | Error | Starts then fails: ImangeManip Error - image size bigger than expected |
| IR_tf_1.7 | Error | Starts then fails: ImangeManip Error - image size bigger than expected |
| IR_tf_1.10 | Error | Starts then fails: ImangeManip Error - image size bigger than expected |
| IR_tf_1.13 | Incompatible |  |
| IR_tf_1.14 | Incompatible |  |
| IR_tf_1.15 | Incompatible |  |
| IR_tf_2.0 | Incompatible |  |
