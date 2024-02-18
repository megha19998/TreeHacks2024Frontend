import cv2
import easyocr
import matplotlib.pyplot as plt
import numpy as np

image_path = '/Users/meghasharma/TreeHacks2024/facebook.jpeg'
img = cv2.imread(image_path)
reader = easyocr.Reader(['en'], gpu=False)
text_ = reader.readtext(img)
threshold = 0.25
for t_, t in enumerate(text_):
    if(t[1] == "Forgotten password?"):
        print(t[1])
        bbox, text, score = t 
        print(text)
        cv2.rectangle(img, bbox[0], bbox[2], (0, 255, 0), 5)
        cv2.putText(img, "click here", bbox[0], cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.show()