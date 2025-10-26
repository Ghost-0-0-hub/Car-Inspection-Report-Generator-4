import streamlit as st
from fpdf import FPDF
import io
import traceback
from datetime import datetime

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

# 1️⃣ Basic Information / Car Details
with st.expander("Basic Information", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        owner_name = st.text_input("Owner Name").strip()
        make = st.text_input("Make").strip()
        mileage = st.number_input("Mileage (km)", min_value=0, step=100)
        colour = st.text_input("Colour").strip()
        fuel_type = st.selectbox("Fuel Type", ["Petrol", "Hybrid", "Electric", "Diesel"])
    with col2:
        car_model = st.text_input("Car Model").strip()
        model_year = st.number_input("Model Year", min_value=1980, max_value=2030, step=1)
        registration_year = st.number_input("Registration Year", min_value=1980, max_value=2030, step=1)
        registration_type = st.selectbox("Registration Type", ["Commercial", "Private"])
        registration_city = st.text_input("Registration City").strip()
    with col3:
        variant = st.text_input("Variant").strip()
        license_plate = st.text_input("License Plate").strip()
        location = st.text_input("Location").strip()
        import_status = st.text_input("Import Status From").strip()
        number_of_seats = st.number_input("Number of Seats", min_value=1, max_value=20)
        number_of_doors = st.number_input("Number of Doors", min_value=1, max_value=10)

# 2️⃣ Engine & Transmission / Mechanical
with st.expander("Engine & Transmission"):
    col1, col2, col3 = st.columns(3)
    with col1:
        engine_condition = st.selectbox("Engine Condition", ["Excellent", "Good", "Average", "Poor"])
        transmission = st.selectbox("Transmission", ["Manual", "Automatic", "CVT", "Other"])
    with col2:
        transmission_condition = st.selectbox("Transmission Condition", ["Excellent", "Good", "Average", "Poor"])
    with col3:
        oil_leaks = st.radio("Oil Leaks?", ["Yes", "No"])

# 3️⃣ Brakes & Suspension
with st.expander("Brakes & Suspension"):
    col1, col2, col3 = st.columns(3)
    with col1:
        brakes_condition = st.selectbox("Brakes Condition", ["Excellent", "Good", "Average", "Poor"])
    with col2:
        suspension_condition = st.selectbox("Suspension Condition", ["Excellent", "Good", "Average", "Poor"])
    with col3:
        steering_condition = st.selectbox("Steering Condition", ["Excellent", "Good", "Average", "Poor"])

# 4️⃣ Tires & Wheels / Car Body Evaluation
with st.expander("Tires & Wheels / Car Body"):
    col1, col2 = st.columns(2)
    with col1:
        tire_condition = st.selectbox("Tire Condition", ["Excellent", "Good", "Average", "Poor"])
        car_diagram = st.file_uploader("Upload Car Diagram (if any)", type=["png","jpg","jpeg"])
    with col2:
        wheel_condition = st.selectbox("Wheel Condition", ["Excellent", "Good", "Average", "Poor"])
        st.text_area("Car Body Evaluation Codes:\n% Tire\nA1 - Minor Scratch\nA2 - Major Scratches\nE1 - Minor Dent\nE2 - Major Dents\nP - Paint Spray Only\nT - TOTAL Genuine\nG1 - Glass Scratches\nG4 - Glass Chipped\nW - Repaired with Dry Denting", height=150)

# 5️⃣ Lights & Electricals
with st.expander("Lights & Electricals"):
    col1, col2, col3 = st.columns(3)
    with col1:
        headlight_condition = st.selectbox("Headlights", ["Working", "Not Working"])
        accessories = st.text_area("Accessories Checked", height=60)
    with col2:
        indicator_condition = st.selectbox("Indicators", ["Working", "Not Working"])
    with col3:
        battery_condition = st.selectbox("Battery Condition", ["Excellent", "Good", "Average", "Poor"])
        test_drive = st.selectbox("Test Drive", ["Passed", "Needs Attention", "Failed"])

# 6️⃣ Interior & Exterior
with st.expander("Interior & Exterior"):
    col1, col2, col3 = st.columns(3)
    with col1:
        interior_condition = st.selectbox("Interior Condition", ["Excellent", "Good", "Average", "Poor"])
    with col2:
        exterior_condition = st.selectbox("Exterior Condition", ["Excellent", "Good", "Average", "Poor"])
    with col3:
        paint_condition = st.selectbox("Paint Condition", ["Excellent", "Good", "Average", "Poor"])

# 7️⃣ Safety & Features
with st.expander("Safety & Features"):
    col1, col2, col3 = st.columns(3)
    with col1:
        airbags = st.radio("Airbags Functional?", ["Yes", "No"])
    with col2:
        ac_condition = st.selectbox("AC Condition", ["Excellent", "Good", "Average", "Poor"])
    with col3:
        infotainment = st.selectbox("Infotainment System", ["Excellent", "Good", "Average", "Poor"])

# 8️⃣ Documents
with st.expander("Documents"):
    col1, col2 = st.columns(2)
    with col1:
        original_book = st.checkbox("Original Book")
        original_card = st.checkbox("Original Card")
        original_file = st.checkbox("Original File")
    with col2:
        number_plate_condition = st.selectbox("Number Plate Condition", ["Original", "Not Original"])

# 9️⃣ Additional Comments / Photos
with st.expander("Additional Comments / Photos"):
    comments = st.text_area("Additional Comments", height=120, placeholder="Add extra notes here...")
    photos = st.file_uploader("Upload Car Photos", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

# --- PDF GENERATION FUNCTION ---
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Car Inspection Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 8, f"Inspection Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(5)

    # Basic Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Basic Information", ln=True)
    pdf.set_font("Arial", "", 12)
    for key in ["Owner Name", "Make", "Car Model", "Model Year", "Variant", "Registration Year",
                "Mileage", "Colour", "Transmission", "Fuel Type", "Registration Type",
                "Registration City", "Location", "Import Status From", "Number of Seats", "Number of Doors",
                "License Plate"]:
        value = str(data.get(key, "N/A"))
        pdf.cell(0, 8, f"{key}: {value}", ln=True)

    # Other Sections
    for section, content in data.items():
        if section in ["Owner Name", "Make", "Car Model", "Model Year", "Variant", "Registration Year",
                       "Mileage", "Colour", "Transmission", "Fuel Type", "Registration Type",
                       "Registration City", "Location", "Import Status From", "Number of Seats", "Number of Doors",
                       "License Plate"]:
            continue
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, section, ln=True)
        pdf.set_font("Arial", "", 12)
        for key, value in content.items():
            pdf.cell(0, 8, f"{key}: {value if value else 'N/A'}", ln=True)

    pdf_output = io.BytesIO(pdf.output(dest="S").encode("latin-1"))
    return pdf_output

# --- SUBMIT BUTTON ---
if st.button("Submit Inspection"):
    try:
        if not owner_name or not car_model:
            st.warning("⚠️ Please fill in at least Owner Name and Car Model before submitting.")
            st.stop()

        data = {
            # Basic Info
            "Owner Name": owner_name,
            "Make": make,
            "Car Model": car_model,
            "Model Year": model_year,
            "Variant": variant,
            "Registration Year": registration_year,
            "Mileage": mileage,
            "Colour": colour,
            "Transmission": transmission,
            "Fuel Type": fuel_type,
            "Registration Type": registration_type,
            "Registration City": registration_city,
            "Location": location,
            "Import Status From": import_status,
            "Number of Seats": number_of_seats,
            "Number of Doors": number_of_doors,
            "License Plate": license_plate,

            # Sections
            "Engine & Transmission": {
                "Engine Condition": engine_condition,
                "Transmission Condition": transmission_condition,
                "Oil Leaks": oil_leaks,
            },
            "Brakes & Suspension": {
                "Brakes Condition": brakes_condition,
                "Suspension Condition": suspension_condition,
                "Steering Condition": steering_condition,
            },
            "Tires & Wheels / Car Body": {
                "Tire Condition": tire_condition,
                "Wheel Condition": wheel_condition,
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
                "Paint Condition": paint_condition,
            },
            "Safety & Features": {
                "Airbags Functional": airbags,
                "AC Condition": ac_condition,
                "Infotainment System": infotainment,
            },
            "Documents": {
                "Original Book": original_book,
                "Original Card": original_card,
                "Original File": original_file,
                "Number Plate Condition": number_plate_condition
            },
            "Additional Comments": {"Comments": comments},
        }

        pdf_bytes = generate_pdf(data)

        safe_owner = owner_name.replace("/", "_") or "Unknown"
        safe_model = car_model.replace("/", "_") or "Unknown"
        filename = f"{safe_owner}_{safe_model}_Inspection.pdf"

        st.success("✅ Inspection report generated successfully!")
        st.download_button(
            label="📄 Download Inspection Report PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
        )
        st.balloons()

    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.code(traceback.format_exc())
