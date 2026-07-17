import cv2
import face_recognition
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime

# Import exporting libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------
# Configuration & Theme Colors
# -----------------------------
BG_COLOR = "#F2F4F1"
CARD_COLOR = "#DCE3DD"
PRIMARY_SAGE = "#7A9E7E"
DARK_SAGE = "#5F7F63"
ACCENT_GREY = "#707070"
TEXT_COLOR = "#2F2F2F"

# Set CTK general styling
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")  # Will override components manually with Sage palette

# -----------------------------
# Load known faces (Organized by Class Folders)
# -----------------------------
known_face_encodings = []
known_face_names = []
student_class_map = {}  # Maps student name -> class folder name
faces_folder = "faces"

# Explicit tracking lists for structural integrity
ALL_CLASSES = ["5A", "5B", "5C", "6A", "6B", "6C", "7A", "7B", "7C", "8A", "8B", "8C", "9A", "9B", "9C", "10A", "10B", "10C"]
class_students = {cls: [] for cls in ALL_CLASSES}

# Load face database scanning subdirectories recursively
if os.path.exists(faces_folder):
    for class_dir in os.listdir(faces_folder):
        class_path = os.path.join(faces_folder, class_dir)
        if os.path.isdir(class_path) and class_dir in ALL_CLASSES:
            for file in os.listdir(class_path):
                if file.endswith(".jpg") or file.endswith(".png"):
                    image_path = os.path.join(class_path, file)
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    if len(encodings) > 0:
                        student_name = os.path.splitext(file)[0]
                        known_face_encodings.append(encodings[0])
                        known_face_names.append(student_name)
                        student_class_map[student_name] = class_dir
                        class_students[class_dir].append(student_name)
else:
    print(f"Warning: '{faces_folder}' folder not found!")

master_list = known_face_names.copy()
present_list = []
present_times = {}  # Maps student name -> string timestamp when recognized

# -----------------------------
# Camera Initialization
# -----------------------------
cap = cv2.VideoCapture(0)

# -----------------------------
# Performance & Processing Variables
# -----------------------------
frame_count = 0
PROCESS_EVERY_N_FRAMES = 3  # Process face recognition on every 3rd frame to reduce CPU load
SCALE_FACTOR = 0.25         # Downscale frame to 25% for lightning-fast facial detection

# -----------------------------
# GUI Setup
# -----------------------------
app = ctk.CTk()
app.geometry("950x850")
app.title("Attendance System")
app.configure(fg_color=BG_COLOR)

# Container frame to easily clear and swap UI screens
main_container = ctk.CTkFrame(app, fg_color=BG_COLOR)
main_container.pack(fill="both", expand=True, padx=20, pady=20)

# Screen title
title_label = ctk.CTkLabel(
    main_container, 
    text="LIVE ATTENDANCE TRACKING", 
    font=ctk.CTkFont(size=20, weight="bold"),
    text_color=DARK_SAGE
)
title_label.pack(pady=(10, 5))

# Camera canvas frame with a clean border
camera_border = ctk.CTkFrame(main_container, fg_color=CARD_COLOR, corner_radius=12)
camera_border.pack(pady=10, fill="both", expand=True)

camera_label = ctk.CTkLabel(camera_border, text="")
camera_label.pack(padx=8, pady=8, fill="both", expand=True)

# Status indicators
status_frame = ctk.CTkFrame(main_container, fg_color="transparent")
status_frame.pack(pady=5)

status_title = ctk.CTkLabel(
    status_frame, 
    text="Status: ", 
    font=ctk.CTkFont(size=14, weight="bold"), 
    text_color=ACCENT_GREY
)
status_title.pack(side="left")

status = ctk.CTkLabel(
    status_frame, 
    text="Waiting...", 
    font=ctk.CTkFont(size=14, weight="bold"), 
    text_color=DARK_SAGE
)
status.pack(side="left")

running = True
global_structured_data = {}  # Shared dictionary mapping class summaries for data exports


def update():
    """Optimized camera refresh loop."""
    global frame_count, running

    if not running:
        return

    ret, frame = cap.read()

    if ret:
        # 1. Core Face Recognition Optimization
        small_frame = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Skip heavy processing on unnecessary frames
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            locations = face_recognition.face_locations(rgb_small)
            encodings = face_recognition.face_encodings(rgb_small, locations)

            for face_encoding in encodings:
                matches = face_recognition.compare_faces(
                    known_face_encodings,
                    face_encoding,
                    tolerance=0.5
                )

                if True in matches:
                    index = matches.index(True)
                    name = known_face_names[index]

                    if name not in present_list:
                        present_list.append(name)
                        present_times[name] = datetime.now().strftime("%H:%M:%S")
                        print(name, "Marked Present")
                        status.configure(
                            text=f"{name} Present",
                            text_color=DARK_SAGE
                        )
                                
        frame_count += 1

        # 2. Display Optimization
        rgb_full = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_full)
        
        # Determine dynamic sizing to fit window cleanly
        img = img.resize((720, 430))
        imgtk = ImageTk.PhotoImage(img)
        
        camera_label.configure(image=imgtk)
        camera_label.image = imgtk

    # Non-blocking GUI updates
    app.after(15, update)


def create_class_card(parent, class_name, present_studs, absent_studs):
    """Generates a structured individual UI card frame for a single class summary."""
    card = ctk.CTkFrame(parent, fg_color=CARD_COLOR, corner_radius=12, width=270, height=320)
    card.pack_propagate(False)
    
    # Class Header Banner
    header_lbl = ctk.CTkLabel(card, text=class_name, font=ctk.CTkFont(size=18, weight="bold"), text_color=DARK_SAGE)
    header_lbl.pack(pady=(10, 5))
    
    # Split Layout columns for Present/Absent Lists
    split_frame = ctk.CTkFrame(card, fg_color="transparent")
    split_frame.pack(fill="both", expand=True, padx=8)
    split_frame.grid_columnconfigure(0, weight=1, uniform="subcol")
    split_frame.grid_columnconfigure(1, weight=0)  # Separator lines column
    split_frame.grid_columnconfigure(2, weight=1, uniform="subcol")
    split_frame.grid_rowconfigure(0, weight=0)
    split_frame.grid_rowconfigure(1, weight=1)
    
    # Text headers
    ctk.CTkLabel(split_frame, text="Present", font=ctk.CTkFont(size=12, weight="bold"), text_color=DARK_SAGE).grid(row=0, column=0, sticky="ew")
    ctk.CTkLabel(split_frame, text="Absent", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_GREY).grid(row=0, column=2, sticky="ew")
    
    # Present Sub-Scrollable Area
    pres_scroll = ctk.CTkScrollableFrame(split_frame, fg_color="transparent", corner_radius=0, label_text="")
    pres_scroll.grid(row=1, column=0, sticky="nsew", pady=(2, 5))
    if present_studs:
        for s in present_studs:
            ctk.CTkLabel(pres_scroll, text=s, font=ctk.CTkFont(size=11), text_color=TEXT_COLOR, anchor="w").pack(fill="x", pady=1)
    else:
        ctk.CTkLabel(pres_scroll, text="-", font=ctk.CTkFont(size=11, slant="italic"), text_color=ACCENT_GREY).pack(pady=5)
        
    # Visual Vertical Separator Frame
    sep = ctk.CTkFrame(split_frame, width=1, fg_color=ACCENT_GREY)
    sep.grid(row=0, column=1, rowspan=2, sticky="ns", padx=4, pady=5)
    
    # Absent Sub-Scrollable Area
    abs_scroll = ctk.CTkScrollableFrame(split_frame, fg_color="transparent", corner_radius=0, label_text="")
    abs_scroll.grid(row=1, column=2, sticky="nsew", pady=(2, 5))
    if absent_studs:
        for s in absent_studs:
            ctk.CTkLabel(abs_scroll, text=s, font=ctk.CTkFont(size=11), text_color=TEXT_COLOR, anchor="w").pack(fill="x", pady=1)
    else:
        ctk.CTkLabel(abs_scroll, text="-", font=ctk.CTkFont(size=11, slant="italic"), text_color=ACCENT_GREY).pack(pady=5)
        
    # Footer Panel Metrics Statistics Calculation
    total_count = len(class_students[class_name])
    present_count = len(present_studs)
    absent_count = len(absent_studs)
    ratio = (present_count / total_count * 100) if total_count > 0 else 0.0
    
    stats_text = f"Total Students: {total_count}  |  Present: {present_count}  |  Absent: {absent_count}\nAttendance: {ratio:.1f}%"
    stats_lbl = ctk.CTkLabel(card, text=stats_text, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_COLOR, justify="center")
    stats_lbl.pack(pady=(2, 10))
    
    return card


# -----------------------------
# Export Implementation Logic
# -----------------------------
def export_to_pdf():
    """Compiles formatted document reports using ReportLab canvas layers."""
    reports_dir = "attendance_reports"
    os.makedirs(reports_dir, exist_ok=True)
    filename = os.path.join(reports_dir, f"Attendance_{datetime.now().strftime('%Y-%m-%d')}.pdf")
    
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom reporting typography mappings
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], alignment=1, textColor=colors.HexColor(DARK_SAGE), spaceAfter=20)
    class_style = ParagraphStyle('ClassHeader', parent=styles['Heading2'], textColor=colors.HexColor(DARK_SAGE), spaceBefore=15, spaceAfter=5)
    normal_style = ParagraphStyle('DocNormal', parent=styles['Normal'], textColor=colors.HexColor(TEXT_COLOR), fontSize=10, leading=14)
    
    elements = [Paragraph(f"Attendance Report — {datetime.now().strftime('%Y-%m-%d')}", title_style), Spacer(1, 10)]
    
    for class_name in ALL_CLASSES:
        p_list = global_structured_data[class_name]["Present"]
        a_list = global_structured_data[class_name]["Absent"]
        
        total_count = len(class_students[class_name])
        present_count = len(p_list)
        absent_count = len(a_list)
        ratio = (present_count / total_count * 100) if total_count > 0 else 0.0
        
        elements.append(Paragraph(f"Class Section: {class_name}", class_style))
        
        # Format textual presentation breakdowns
        p_str = ", ".join(p_list) if p_list else "None"
        a_str = ", ".join(a_list) if a_list else "None"
        
        elements.append(Paragraph(f"<b>Present:</b> {p_str}", normal_style))
        elements.append(Paragraph(f"<b>Absent:</b> {a_str}", normal_style))
        
        # Metrics table layout parsing
        data = [
            ["Total Students", "Present Count", "Absent Count", "Attendance Percentage"],
            [str(total_count), str(present_count), str(absent_count), f"{ratio:.1f}%"]
        ]
        
        t = Table(data, colWidths=[130, 130, 130, 140])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(CARD_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(TEXT_COLOR)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(ACCENT_GREY)),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        elements.append(Spacer(1, 6))
        elements.append(t)
        elements.append(Spacer(1, 15))
        
    doc.build(elements)
    show_success_banner()


def show_success_banner():
    """Pops open a brief notification indicator context validation overlay."""
    toast = ctk.CTkLabel(
        main_container,
        text="Attendance report saved successfully.",
        fg_color=DARK_SAGE,
        text_color="white",
        font=ctk.CTkFont(size=14, weight="bold"),
        corner_radius=6,
        padx=15,
        pady=8
    )
    toast.pack(pady=5, before=action_panel)
    app.after(3000, toast.destroy)


def display_results(structured_data):
    """Replaces the webcam interface frame with the continuous scrollable grid view dashboard."""
    global action_panel
    
    # Clear out existing webcam view elements completely
    for widget in main_container.winfo_children():
        widget.destroy()

    # Title Header Info
    top_label = ctk.CTkLabel(
        main_container,
        text="ATTENDANCE SUMMARY REPORT",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color=DARK_SAGE
    )
    top_label.pack(pady=(15, 10))
    
    # Main Universal Scrollable Container Box
    master_scroll = ctk.CTkScrollableFrame(
        main_container,
        fg_color="transparent",
        scrollbar_button_color=PRIMARY_SAGE,
        scrollbar_button_hover_color=DARK_SAGE
    )
    master_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    master_scroll.grid_columnconfigure((0, 1, 2), weight=1, uniform="card_col")
    
    current_row = 0
    current_col = 0
    
    # Loop over predefined sections to render cards systematically
    for class_name in ALL_CLASSES:
        p_list = structured_data[class_name]["Present"]
        a_list = structured_data[class_name]["Absent"]
        
        # Build individual UI Cards inside layout grid directly on the master scroll
        class_card = create_class_card(master_scroll, class_name, p_list, a_list)
        class_card.grid(row=current_row, column=current_col, padx=12, pady=12, sticky="nsew")
        
        current_col += 1
        if current_col > 2:
            current_col = 0
            current_row += 1

    # Action panel section configuration wrapper containing core utilities buttons controls
    action_panel = ctk.CTkFrame(main_container, fg_color="transparent")
    action_panel.pack(fill="x", pady=15)
    
    pdf_btn = ctk.CTkButton(
        action_panel,
        text="Save as PDF",
        command=export_to_pdf,
        width=200,
        height=40,
        fg_color=PRIMARY_SAGE,
        hover_color=DARK_SAGE,
        text_color="white",
        font=ctk.CTkFont(weight="bold"),
        corner_radius=8
    )
    pdf_btn.pack(side="left", padx=40, expand=True)

    close_btn = ctk.CTkButton(
        action_panel,
        text="Close Application",
        command=app.destroy,
        width=200,
        height=40,
        fg_color=DARK_SAGE,
        hover_color=ACCENT_GREY,
        text_color="white",
        font=ctk.CTkFont(weight="bold"),
        corner_radius=8
    )
    close_btn.pack(side="left", padx=40, expand=True)


def done():
    """Stops webcam tracking updates, structures logs by folder levels, and spawns the summary visualizer."""
    global running, global_structured_data

    running = False
    cap.release()

    # Compile present/absent sorted layout maps by class structure
    global_structured_data = {
        cls: {"Present": [], "Absent": []} for cls in ALL_CLASSES
    }
    
    # Map out the present students dynamically
    for student in present_list:
        cls = student_class_map.get(student)
        if cls in global_structured_data:
            global_structured_data[cls]["Present"].append(student)

    # Evaluate missing students globally by comparing lists
    for cls in ALL_CLASSES:
        for student in class_students[cls]:
            if student not in global_structured_data[cls]["Present"]:
                global_structured_data[cls]["Absent"].append(student)

    # Render results inline on the main screen container view
    display_results(global_structured_data)


# Done Button
button = ctk.CTkButton(
    main_container,
    text="DONE",
    command=done,
    width=200,
    height=42,
    fg_color=PRIMARY_SAGE,
    hover_color=DARK_SAGE,
    text_color="white",
    font=ctk.CTkFont(size=14, weight="bold"),
    corner_radius=8
)
button.pack(pady=(5, 15))

# Initialize Loop
update()

app.mainloop()

# Cleanup just in case execution terminates abruptly
if cap.isOpened():
    cap.release()
cv2.destroyAllWindows()
