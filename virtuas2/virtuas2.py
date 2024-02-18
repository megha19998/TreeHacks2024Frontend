"""Welcome to Reflex! This file outlines the steps to create a basic app."""

from rxconfig import config
import reflex as rx
from typing import List
import cv2
import easyocr
import matplotlib.pyplot as plt
import numpy as np
import os
import time
from PIL import Image
from pathlib import Path
import speech_recognition as sr
import pygame
import time

docs_url = "https://reflex.dev/docs/getting-started/introduction"
filename = f"{config.app_name}/{config.app_name}.py"
recognizer = sr.Recognizer()

class State(rx.State):
    """The app state."""
    img: list[str]
    inputBox: str

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle the upload of file(s).

        Args:
            files: The uploaded files.
        """
        for file in files:
            upload_data = await file.read()
            outfile = Path(rx.get_upload_dir()) / file.filename
            # outfile = rx.get_asset_path(file.filename)

            # Save the file.
            with open(outfile, "wb") as file_object:
                file_object.write(upload_data)
            print(file_object.name)
            tempImg = performOCR(str(file_object.name))
            print("here")
            print(tempImg)
            
            # Update the img var.
            self.img.append(tempImg)
    
    def mouse_callback(self,event, x, y, flags, param):
        global captured, frame
        if event == cv2.EVENT_LBUTTONDOWN:
            captured = True
            frame = param

    def captureImage(self):
        global captured, frame
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return
        cv2.namedWindow('Camera')
        cv2.setMouseCallback('Camera', self.mouse_callback)

        captured = False
        frame = None
        current_directory = os.getcwd()
        print("Current working directory:", current_directory)
        while not captured:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not capture frame.")
                break
            cv2.imshow('Camera', frame)
            key = cv2.waitKey(1)
            if key == 27:  
                break
        img_path = Path(rx.get_upload_dir()) / "capturedImage.png"
        if frame is not None:
            print("I am here")
            cv2.imwrite(str(img_path), frame)
        print(frame)
        print("I am here now")
        cap.release()
        cv2.destroyAllWindows()

        #State.handle_upload('captured_image.png')
        time.sleep(5)
        tempImg = performOCR(str(img_path))
        self.img.append(tempImg)

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            print("Recognizing...")
            self.inputBox = recognizer.recognize_google(audio)
            print("You said:", self.inputBox)
            return "Success"
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return None
        except sr.RequestError as e:
            print("Error:", e)
            return None

# class StateVariable(rx.State):
#     inputBox: str
#     inputVoice: str

color = "rgb(107,99,246)"

def performOCR(image_path):
    print(image_path)
    img = cv2.imread(image_path)
    reader = easyocr.Reader(['en'], gpu=False)
    text_ = reader.readtext(img)
    print(text_)
    threshold = 0.25
    ifTextPresent = False
    for t_, t in enumerate(text_):
        if(t[1] == "Forgotten password?"):
            ifTextPresent = True
            break
    if(ifTextPresent):
        for t_, t in enumerate(text_):
            if(t[1] == "Forgotten password?"):
                print(t[1])
                bbox, text, score = t 
                print(text)
                cv2.rectangle(img, bbox[0], bbox[2], (0, 255, 0), 5)
                cv2.putText(img, "click here", bbox[0], cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)
                cv2.imwrite(image_path,cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                print("it is here in if")
                return image_path.split("/")[-1]
    else:
        cv2.imwrite(image_path,cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        cv2.imwrite("test.png",cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        print(image_path)
        print("it is not here in if")
        return image_path.split("/")[-1]

class StepNumber(rx.State):
    step: List[str] = []

    def onClick(self):
        self.step =  ["step 1","step 2","step 3","step 4","step 5","step 6"]

    def finish_item(self, step: str):
        self.step = [i for i in self.step if i != step]

def addSteps(text):
    return rx.hstack(
            rx.section(
                rx.text(text),
                padding_left="12px",
                padding_right="12px",
                background_color="var(--gray-2)",
            ),
            rx.button(
                "Done",
                on_click=lambda: StepNumber.finish_item(text)
            ),
            rx.drawer.root(
                rx.drawer.trigger(rx.button("Upload a Photo")),
                rx.drawer.overlay(),
                rx.drawer.portal(
                    rx.drawer.content(
                        rx.flex(
                            rx.drawer.close(rx.box(rx.button("Close"))),
                            align_items="start",
                            direction="column",
                        ),
                        rx.hstack(
                            rx.vstack(
                                rx.upload(
                                    rx.vstack(
                                        rx.button("Select File", color=color, bg="white", border=f"1px solid {color}"),
                                        rx.text("Drag and drop files here or click to select files"),
                                    ),
                                    border=f"1px dotted {color}",
                                    padding="5em",
                                ),
                                rx.button(
                                "Capture",
                                on_click=lambda:State.captureImage()
                                )
                            ),
                            rx.hstack(rx.foreach(rx.selected_files, rx.text)),
                            rx.button(
                                "Upload",
                                on_click=lambda:State.handle_upload(rx.upload_files()),
                            ),
                            rx.button(
                                "Clear",
                                on_click=rx.clear_selected_files,
                            ),
                            rx.foreach(State.img, lambda img: rx.image(
                                src=rx.get_upload_url(img),
                                width = "80%",
                                height = "80%"
                                )),
                            padding="5em",
                        ),
                        top="auto",
                        right="auto",
                        height="100%",
                        width="100%",
                        padding="2em",
                        background_color="#FFF"
                        # background_color=rx.color("green", 3)
                    )
                ),
                direction="bottom",
            )
        )

def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.input(placeholder="Ask a question", value=State.inputBox),
                rx.button(
                    "Click",
                align="center", 
                spacing="7",
                on_click=StepNumber.onClick
                ),
                rx.button(
                    rx.image(
                    src='mic.png',
                    height='1em',
                    width='1em'
                    ),
                    on_click = State.listen()
                )
            ),
            rx.scroll_area(
                rx.foreach(
                    StepNumber.step, addSteps
                ),
                scrollbars="vertical",
                style={"height": 500}
            ),
        ),
        height="100vh",
    )

app = rx.App()
app.add_page(index)
