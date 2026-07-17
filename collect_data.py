import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from tkinter import messagebox 

# -----------------------------
# Configuration & Theme Colors
# -----------------------------
BG_COLOR = "#F2F4F1"
CARD_COLOR = "#DCE3DD"
PRIMARY_SAGE = "#7A9E7E"
DARK_SAGE = "#5F7F63"
ACCENT_GREY = "#707070"
TEXT_COLOR = "#2F2F2F"

# Set CTK general styling to match
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")  

SAVE_FOLDER = "faces"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -----------------------------
# Camera Initialization
# -----------------------------
cap = cv2.VideoCapture(0)

# -----------------------------
# Performance Optimization Variables
# -----------------------------
SCALE_FACTOR = 0.5  # Downscale webcam frames by 50% for lag-free face detection

# -----------------------------
# GUI Setup
# -----------------------------
app = ctk.CTk()
app.title("Student Registration")
app.geometry("900x750")
app.configure(fg_color=BG_COLOR)

# Main wrapping container
main_container = ctk.CTkFrame(app, fg_color=BG_COLOR)
main_container.pack(fill="both", expand=True, padx=20, pady=20)

# Screen title
title_label = ctk.CTkLabel(
    main_container, 
    text="STUDENT REGISTRATION", 
    font=ctk.CTkFont(size=20, weight="bold"),
    text_color=DARK_SAGE
)
title_label.pack(pady=(10, 5))

# Interactive control form frame (Moved above camera to follow the requested layout)
form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
form_frame.pack(pady=10, fill="x")

# Student Name Field Label & Entry
name_label = ctk.CTkLabel(
    form_frame,
    text="Student Name",
    font=ctk.CTkFont(size=13, weight="bold"),
    text_color=TEXT_COLOR
)
name_label.pack(pady=(5, 2))

name_entry = ctk.CTkEntry(
    form_frame, 
    width=320, 
    height=40,
    placeholder_text="Enter Student Name",
    fg_color="white",
    text_color=TEXT_COLOR,
    border_color=CARD_COLOR,
    corner_radius=8,
    font=ctk.CTkFont(size=14)
)
name_entry.pack(pady=5)

# Standard & Section Label & Dropdown
class_label = ctk.CTkLabel(
    form_frame,
    text="Standard & Section",
    font=ctk.CTkFont(size=13, weight="bold"),
    text_color=TEXT_COLOR
)
class_label.pack(pady=(5, 2))

class_options = [
    "5A", "5B", "5C", "6A", "6B", "6C", "7A", "7B", "7C",
    "8A", "8B", "8C", "9A", "9B", "9C", "10A", "10B", "10C"
]

class_dropdown = ctk.CTkComboBox(
    form_frame,
    values=class_options,
    width=320,
    height=40,
    fg_color="white",
    text_color=TEXT_COLOR,
    border_color=CARD_COLOR,
    button_color=PRIMARY_SAGE,
    button_hover_color=DARK_SAGE,
    corner_radius=8,
    font=ctk.CTkFont(size=14),
    state="readonly"  # Restricts user from entering custom text manually
)
class_dropdown.set("Select Class")  # Set clean initial placeholder state
class_dropdown.pack(pady=5)

# Video display box with a clean card boundary
camera_border = ctk.CTkFrame(main_container, fg_color=CARD_COLOR, corner_radius=12)
camera_border.pack(pady=10, fill="both", expand=True)

camera_label = ctk.CTkLabel(camera_border, text="")
camera_label.pack(padx=8, pady=8, fill="both", expand=True)

# Modern Status panel
status_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
status_frame.pack(pady=5)

status_title = ctk.CTkLabel(
    status_frame, 
    text="Status: ", 
    font=ctk.CTkFont(size=13, weight="bold"), 
    text_color=ACCENT_GREY
)
status_title.pack(side="left")

status_label = ctk.CTkLabel(
    status_frame, 
    text="Ready", 
    font=ctk.CTkFont(size=13, weight="bold"), 
    text_color=DARK_SAGE
)
status_label.pack(side="left")

current_frame = None
current_face = None


def update_camera():
    """Reads webcam frames, scales down for lag-free face detection, and draws the viewfinder."""
    global current_frame, current_face

    ret, frame = cap.read()

    if ret:
        current_frame = frame.copy()

        # 1. Downscale frame for fast, lag-free face tracking
        small_frame = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(120 * SCALE_FACTOR), int(120 * SCALE_FACTOR))
        )

        current_face = None

        for (x, y, w, h) in faces:
            # 2. Scale face coordinates back up to map onto original high-res image
            x_orig = int(x / SCALE_FACTOR)
            y_orig = int(y / SCALE_FACTOR)
            w_orig = int(w / SCALE_FACTOR)
            h_orig = int(h / SCALE_FACTOR)

            # Draw tracking boundary on frame
            cv2.rectangle(frame, (x_orig, y_orig), (x_orig + w_orig, y_orig + h_orig), (122, 158, 126), 2)

            # Crop face from original frame for a high-quality photo save
            current_face = current_frame[y_orig:y_orig + h_orig, x_orig:x_orig + w_orig]
            break

        # Convert full-res frames to RGB and resize nicely to match UI boundaries
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img = img.resize((720, 430))

        imgtk = ImageTk.PhotoImage(img)

        camera_label.configure(image=imgtk)
        camera_label.image = imgtk

    # Non-blocking main GUI refresh using after()
    app.after(15, update_camera)


def capture():
    """Validates fields, automatically creates subfolders, and saves the detected face."""
    global current_face

    name = name_entry.get().strip()
    selected_class = class_dropdown.get()

    # 1. Validation Checks
    if name == "":
        messagebox.showwarning("Missing Information", "Please enter the Student Name before capturing.")
        status_label.configure(text="Enter a name first.", text_color=ACCENT_GREY)
        return

    if selected_class == "Select Class" or selected_class not in class_options:
        messagebox.showwarning("Missing Information", "Please select a valid Standard & Section before capturing.")
        status_label.configure(text="Select standard/section.", text_color=ACCENT_GREY)
        return

    if current_face is None:
        status_label.configure(text="No face detected.", text_color=ACCENT_GREY)
        return

    # 2. Structured Folder Directory Layout Logic
    class_folder = os.path.join(SAVE_FOLDER, selected_class)
    os.makedirs(class_folder, exist_ok=True)

    filename = os.path.join(class_folder, f"{name}.jpg")

    # Save the high-res cropped face crop exactly as before
    cv2.imwrite(filename, current_face)

    status_label.configure(text=f"Saved {name}.jpg to {selected_class} successfully!", text_color=DARK_SAGE)
    
    # Reset input entry fields for the next registration
    name_entry.delete(0, "end")
    class_dropdown.set("Select Class")


# Capture Button
capture_button = ctk.CTkButton(
    form_frame,
    text="CAPTURE PHOTO",
    command=capture,
    width=220,
    height=42,
    fg_color=PRIMARY_SAGE,
    hover_color=DARK_SAGE,
    text_color="white",
    font=ctk.CTkFont(size=14, weight="bold"),
    corner_radius=8
)
capture_button.pack(pady=15)

# Initialize Loop
update_camera()

app.mainloop()

# Proper memory releases
cap.release()
cv2.destroyAllWindows()
