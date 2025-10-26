import streamlit as st
from fpdf import FPDF
import io
import traceback

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CAROBAR Inspection Form",
    page_icon="🚘",
    layout="wide"
)
st.title("🚘 CAROBAR Inspection Form")

st.markdown("""
<style>
/* Main background */
[data-testid="stAppViewContainer"] {background-color: #FFFFFF;}
/* Sidebar background */
[data-testid="stSidebar"] {background-color: #F8F9FA;}
/* Text color */
[data-testid="stAppViewContainer"] {color: #0B2F7A;}
/* Button color */
.stButton>button {background-color: #0B2F7A; color: white; font-weight: bold;}
</style>
""", unsafe_allow_html=True)
# --- FORM SECTIONS ---
with st.expander("Basic Information", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        owner_name = st.text_input("Owner Name").strip()
    with col2:
        car_model = st.text_input("Car Model").strip()
    with col3:
        car_year = st.number_input("Year", min_value=1980, max_value=2030, step=1)
    license_plate = st.text_input("License Plate").strip()

with st.expander("Engine & Transmission"):
    col1, col2, col3 = st.columns(3)
    with col1:
        engine_condition = st.selectbox("Engine Condition", ["Excellent", "Good", "Average", "Poor"])
    with col2:
        transmission_condition = st.selectbox("Transmission Condition", ["Excellent", "Good", "Average", "Poor"])
    with col3:
        oil_leaks = st.radio("Oil Leaks?", ["Yes", "No"])

with st.expander("Brakes & Suspension"):
    col1, col2, col3 = st.columns(3)
    with col1:
        brakes_condition = st.selectbox("Brakes Condition", ["Excellent", "Good", "Average", "Poor"])
    with col2:
        suspension_condition = st.selectbox("Suspension Condition", ["Excellent", "Good", "Average", "Poor"])
    with col3:
        steering_condition = st.selectbox("Steering Condition", ["Excellent", "Good", "Average", "Poor"])

with st.expander("Tires & Wheels"):
    col1, col2 = st.columns(2)
    with col1:
        tire_condition = st.selectbox("Tire Condition", ["Excellent", "Good", "Average", "Poor"])
    with col2:
        wheel_condition = st.selectbox("Wheel Condition", ["Excellent", "Good", "Average", "Poor"])

with st.expander("Lights & Electricals"):
    col1, col2, col3 = st.columns(3)
    with col1:
        headlight_condition = st.selectbox("Headlights", ["Working", "Not Working"])
    with col2:
        indicator_condition = st.selectbox("Indicators", ["Working", "Not Working"])
    with col3:
        battery_condition = st.selectbox("Battery Condition", ["Excellent", "Good", "Average", "Poor"])

with st.expander("Interior & Exterior"):
    col1, col2, col3 = st.columns(3)
    with col1:
        interior_condition = st.selectbox("Interior Condition", ["Excellent", "Good", "Average", "Poor"])
    with col2:
        exterior_condition = st.selectbox("Exterior Condition", ["Excellent", "Good", "Average", "Poor"])
    with col3:
        paint_condition = st.selectbox("Paint Condition", ["Excellent", "Good", "Average", "Poor"])

with st.expander("Safety & Features"):
    col1, col2, col3 = st.columns(3)
    with col1:
        airbags = st.radio("Airbags Functional?", ["Yes", "No"])
    with col2:
        ac_condition = st.selectbox("AC Condition", ["Excellent", "Good", "Average", "Poor"])
    with col3:
        infotainment = st.selectbox("Infotainment System", ["Excellent", "Good", "Average", "Poor"])

with st.expander("Additional Comments / Photos"):
    comments = st.text_area("Comments", height=120, placeholder="Add additional inspection notes here...")
    photos = st.file_uploader("Upload Car Photos", accept_multiple_files=True, type=["png", "jpg", "jpeg"])


# --- PDF GENERATION FUNCTION ---
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Car Inspection Report", ln=True, align="C")
    pdf.ln(10)

    # Basic Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Basic Information", ln=True)
    pdf.set_font("Arial", "", 12)
    for key in ["Owner Name", "Car Model", "Year", "License Plate"]:
        value = str(data.get(key, "N/A"))
        pdf.cell(0, 8, f"{key}: {value}", ln=True)

    # Other Sections
    for section, content in data.items():
        if section in ["Owner Name", "Car Model", "Year", "License Plate"]:
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
            "Owner Name": owner_name,
            "Car Model": car_model,
            "Year": car_year,
            "License Plate": license_plate,
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
            "Tires & Wheels": {
                "Tire Condition": tire_condition,
                "Wheel Condition": wheel_condition,
            },
            "Lights & Electricals": {
                "Headlights": headlight_condition,
                "Indicators": indicator_condition,
                "Battery Condition": battery_condition,
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