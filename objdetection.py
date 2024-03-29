import torch
import numpy as np
import cv2
import pafy
import time

class ObjectDetection:
    """
    Class implements Yolo5 model to make2 inferences on a youtube video using OpenCV.
    """
    
    cap = cv2.VideoCapture(0)


    def _init_(self):
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL,on which prediction is made.
        :param out_file: A valid output file name.
        """
        self.model = self.load_model()
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("\n\nDevice Used:", self.device)

    def load_model(self):
        """
        Loads Yolo5 model from pytorch hub.
        :return: Trained Pytorch model.
        """
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        return model

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
     
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        area = 0  # Initialize area variable
        center = None  # Initialize center point variable

        for i in range(n):
            row = cord[i]
            if row[4] >= 0.2:
                x1, y1, x2, y2 = int(row[0] * x_shape), int(row[1] * y_shape), int(row[2] * x_shape), int(row[3] * y_shape)
                bgr = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
            
                if self.class_to_label(labels[i]) == 'person':
                    l = x2 - x1
                    b = y2 - y1
                    area = l * b  # Calculate area for the 'person' class
                    center = (x1 + l // 2, y1 + b // 2)  # Calculate the center point of the bounding box

                    # Display the center of the bounding box
                    cv2.circle(frame, center, 3, (0, 0, 255), -1)

        return frame, area, center

    def _call_(self):
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame,
        and write the output into a new file.
        :return: void
        """

        while cap.isOpened():     
            start_time = time.perf_counter()
            ret, frame = cap.read()
            if not ret:
                break
            results = self.score_frame(frame)
            frame, area, center = self.plot_boxes(results, frame)  # Receive the area value and center point
            end_time = time.perf_counter()
            fps = 1 / np.round(end_time - start_time, 3)
            cv2.putText(frame, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)

            # Calculate the center of the screen
            height, width, _ = frame.shape
            center_x = width // 2
            center_y = height // 2
            cv2.circle(frame, (center_x, center_y), 3, (255, 0, 0), -1)
            
            # print(center_x, center_y)

            cv2.imshow("img", frame)

            if area != 0:  # Check if an area value is available
                return area, center

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        


# Create a new object and execute.
detection = ObjectDetection()
# area, center = detection()

while True:
    area, center = detection()
    print(area)
    print(center)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()