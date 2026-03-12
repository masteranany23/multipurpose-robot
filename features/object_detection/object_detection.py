import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import Picamera2
from flask import Flask, Response

app = Flask(__name__)
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 640)})
picam2.configure(config)

# Initialize TFLite with your custom model
interpreter = tflite.Interpreter(model_path='yolov8s_float16.tflite' )  # Update path
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Update with your custom class labels

CLASSES = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
           "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
           "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
           "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
           "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
           "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl",
           "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza",
           "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table", "toilet",
           "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven",
           "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
           "hair drier", "toothbrush"] # Replace with your actual classes

def draw_detections(frame, boxes, scores, class_ids):
    height, width, _ = frame.shape
    for box, score, cls_id in zip(boxes, scores, class_ids):
        if np.max(box) <= 1.0:
            box = box * np.array([width, height, width, height])
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{CLASSES[cls_id]}: {score:.2f}" if cls_id < len(CLASSES) else f"Unknown: {score:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return frame
def postprocess(outputs, conf_thresh=0.5, iou_thresh=0.4):
    outputs = np.transpose(outputs, (0, 2, 1))
    
    # Split outputs
    boxes = outputs[..., 0:4]
    scores = outputs[..., 4:].max(axis=2)
    class_ids = outputs[..., 4:].argmax(axis=2)
    
    # Convert boxes to OpenCV format [x_center, y_center, width, height] -> [x1, y1, x2, y2]
    x1 = boxes[..., 0] - boxes[..., 2] / 2
    y1 = boxes[..., 1] - boxes[..., 3] / 2
    x2 = boxes[..., 0] + boxes[..., 2] / 2
    y2 = boxes[..., 1] + boxes[..., 3] / 2
    boxes = np.stack([x1, y1, x2, y2], axis=-1)
    
    # Filter by confidence
    mask = scores > conf_thresh
    boxes = boxes[mask]
    scores = scores[mask]
    class_ids = class_ids[mask]
    
    # OpenCV NMS (faster on Raspberry Pi)
    indices = cv2.dnn.NMSBoxes(
        bboxes=boxes.tolist(),
        scores=scores.tolist(),
        score_threshold=conf_thresh,
        nms_threshold=iou_thresh,
        eta=1,
        top_k=5000
    )
    
    if len(indices) > 0:
        indices = indices.flatten()
        return boxes[indices], scores[indices], class_ids[indices]
    else:
        return np.array([]), np.array([]), np.array([])

def gen_frames():
    picam2.start()
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Preprocess
        img = cv2.resize(frame, (640, 640))
        img = img.astype(np.float32) / 255.0
        
        # Inference
        interpreter.set_tensor(input_details[0]['index'], [img])
        interpreter.invoke()
        outputs = interpreter.get_tensor(output_details[0]['index'])
        
        # Postprocess
        boxes, scores, class_ids = postprocess(outputs, conf_thresh=0.4)         
        # Draw
        frame = draw_detections(frame, boxes, scores, class_ids)
        
        # Encode
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
