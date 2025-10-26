import streamlit as st
from fpdf import FPDF
import io
import traceback
from datetime import datetime
from zipfile import ZipFile
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CAROBAR Inspection Form",
    page_icon="🚘",
    layout="wide"
)
st.title("🚘 CAROBAR Inspection Form")

# --- LIGHT THEME CSS ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background-color: #FFFFFF;}
[data-testid="stSidebar"] {background-color: #F8F9FA;}
[data-testid="stAppViewContainer"] {color: #0B2F7A;}
.stButton>button {background-color: #0B2F7A; color: white; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- FORM SECTIONS ---
# ... (keep all your form code unchanged from before)
# I assume the form sections code remains exactly as your last version
# Including Basic Info, Engine & Transmission, Brakes & Suspension, Tires & Wheels, etc.

# --- PDF GENERATION FUNCTION ---
def generate_pdf(data, tire_data, codes, car_diagram, photos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Car Inspection Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 8, f"Inspection Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    # --- Basic Info ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Basic Information", ln=True, fill=True)
    pdf.set_font("Arial", "", 12)
    for key in [
        "Owner Name", "Make", "Car Model", "Model Year", "Variant", "Registration Year",
        "Mileage", "Colour", "Transmission", "Fuel Type", "Registration Type",
        "Registration City", "Location", "Import Status From", "Number of Seats",
        "Number of Doors", "License Plate"
    ]:
        pdf.cell(0, 8, f"{key}: {data.get(key,'N/A')}", ln=True)

    # --- Car Diagram ---
    if car_diagram:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Car Diagram", ln=True)
        car_diagram_path = f"/tmp/{car_diagram.name}"
        with open(car_diagram_path, "wb") as f:
            f.write(car_diagram.getbuffer())
        pdf.image(car_diagram_path, w=150)
        pdf.ln(5)

    # --- Car Body Evaluation Table ---
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 8, "Car Body Evaluation", ln=True, fill=True)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(30, 8, "Tire %", border=1)
    pdf.cell(30, 8, "Code", border=1)
    pdf.cell(120, 8, "Description / Notes", border=1)
    pdf.ln()
    pdf.set_font("Arial", "", 12)

    # Tire % rows
    for pos, value in tire_data.items():
        pdf.cell(30, 8, str(value), border=1)
        pdf.cell(30, 8, "Tire", border=1)
        pdf.cell(120, 8, pos, border=1)
        pdf.ln()

    # Evaluation codes
    for code, info in codes.items():
        pdf.cell(30, 8, "-", border=1)
        pdf.cell(30, 8, code, border=1)
        pdf.cell(120, 8, f"{'Yes' if info['checked'] else 'No'} | Notes: {info['note']}", border=1)
        pdf.ln()

    # --- Other Sections ---
    for section, content in data.items():
        if section in [
            "Owner Name", "Make", "Car Model", "Model Year", "Variant", "Registration Year",
            "Mileage", "Colour", "Transmission", "Fuel Type", "Registration Type",
            "Registration City", "Location", "Import Status From", "Number of Seats",
            "Number of Doors", "License Plate"
        ]:
            continue
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, section, ln=True)
        pdf.set_font("Arial", "", 12)
        for key, value in content.items():
            pdf.cell(0, 8, f"{key}: {value if value else 'N/A'}", ln=True)

    # --- Embed first few photos in PDF ---
    if photos:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Car Photos (Preview)", ln=True)
        for i, photo in enumerate(photos):
            if i >= 3:  # embed only first 3 photos
                break
            photo_path = f"/tmp/{photo.name}"
            with open(photo_path, "wb") as f:
                f.write(photo.getbuffer())
            pdf.image(photo_path, w=150)
            pdf.ln(5)

    pdf_bytes = io.BytesIO(pdf.output(dest="S").encode("latin-1"))
    return pdf_bytes

# --- SUBMIT BUTTON ---
if st.button("Submit Inspection"):
    try:
        if not owner_name or not car_model:
            st.warning("⚠️ Please fill in at least Owner Name and Car Model before submitting.")
            st.stop()

        # Data dictionaries
        tire_data = {
            "Front Left": tire_front_left,
            "Front Right": tire_front_right,
            "Rear Left": tire_rear_left,
            "Rear Right": tire_rear_right
        }

        # Generate PDF
        pdf_bytes = generate_pdf(
            data={
                "Owner Name": owner_name, "Make": make, "Car Model": car_model,
                "Model Year": model_year, "Variant": variant, "Registration Year": registration_year,
                "Mileage": mileage, "Colour": colour, "Transmission": transmission,
                "Fuel Type": fuel_type, "Registration Type": registration_type,
                "Registration City": registration_city, "Location": location,
                "Import Status From": import_status, "Number of Seats": number_of_seats,
                "Number of Doors": number_of_doors, "License Plate": license_plate,
                "Engine & Transmission": {
                    "Engine Condition": engine_condition,
                    "Transmission Condition": transmission_condition,
                    "Oil Leaks": oil_leaks
                },
                "Brakes & Suspension": {
                    "Brakes Condition": brakes_condition,
                    "Suspension Condition": suspension_condition,
                    "Steering Condition": steering_condition
                },
                "Lights & Electricals": {
                    "Headlights": headlight_condition,
                    "Indicators": indicator_condition,
                    "Battery Condition": battery_condition,
                    "Accessories Checked": accessories,
                    "Test Drive": test_drive
                },
                "Interior & Exterior": {
                    "Interior Condition": interior_condition,
                    "Exterior Condition": exterior_condition,
                    "Paint Condition": paint_condition
                },
                "Safety & Features": {
                    "Airbags Functional": airbags,
                    "AC Condition": ac_condition,
                    "Infotainment System": infotainment
                },
                "Documents": {
                    "Original Book": original_book,
                    "Original Card": original_card,
                    "Original File": original_file,
                    "Number Plate Condition": number_plate_condition
                },
                "Additional Comments": {"Comments": comments}
            },
            tire_data=tire_data,
            codes=codes,
            car_diagram=car_diagram,
            photos=photos
        )

        # --- Create ZIP ---
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as zipf:
            zipf.writestr(f"{owner_name}_{car_model}_Inspection.pdf", pdf_bytes.getvalue())
            if car_diagram:
                zipf.writestr(f"Diagram_{car_diagram.name}", car_diagram.getvalue())
            if photos:
                for photo in photos:
                    zipf.writestr(photo.name, photo.getvalue())

        zip_buffer.seek(0)

        st.success("✅ Inspection report and images packaged successfully!")
        st.download_button(
            label="📦 Download ZIP (PDF + Images)",
            data=zip_buffer,
            file_name=f"{owner_name}_{car_model}_Inspection.zip",
            mime="application/zip"
        )
        st.balloons()

    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.code(traceback.format_exc())
