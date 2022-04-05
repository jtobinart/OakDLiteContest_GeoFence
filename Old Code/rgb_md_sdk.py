# python Desktop/opencv_comp/rgb_md_sdk.py
print("======================================================")
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.absolute()))
sys.path.append(str((Path(__file__).parent / "depthai_sdk/depthai_sdk" / "src").absolute()))

from depthai_sdk import Previews
from depthai_sdk.managers import PipelineManager, PreviewManager, NNetManager, BlobManager
import depthai as dai
import cv2

#md_blob_path = str((Path(__file__).parent / Path('MegaDetector/IR_tf_v1.0/md_v4.1.0_openvino_2021.4_6shave.blob')).resolve().absolute())
#md_blob_path = str((Path(__file__).parent / Path('MegaDetector/IR_tf_v1.7/md_v4.1.0_openvino_2021.4_6shave.blob')).resolve().absolute())
md_blob_path = str((Path(__file__).parent / Path('MegaDetector/IR_tf_v1.10/md_v4.1.0_openvino_2021.4_6shave.blob')).resolve().absolute())

labels = {
    '1': 'animal',
    '2': 'person',
    '3': 'vehicle'
}

pm = PipelineManager(openvinoVersion=dai.OpenVINO.VERSION_2021_4)
pm.createColorCam(previewSize=(600, 600), xout=True)

bm = BlobManager(blobPath=md_blob_path)
nm = NNetManager(inputSize=(600, 600))
nn = nm.createNN(pipeline=pm.pipeline, nodes=pm.nodes, blobPath=bm.getBlob(shaves=6, openvinoVersion=pm.pipeline.getOpenVINOVersion()))
pm.addNn(nn)

with dai.Device(pm.pipeline) as device:
    pv = PreviewManager(display=[Previews.color.name])
    pv.createQueues(device)
    nm.createQueues(device)
    nnData = []

    print("Starting Loop")
    while True:
        pv.prepareFrames()
        inNn = nm.outputQueue.tryGet()

        if inNn is not None:
            nnData = nm.decode(inNn)

        nm.draw(pv, nnData)
        pv.showFrames()
        
        if cv2.waitKey(1) == ord('q'):
            break
