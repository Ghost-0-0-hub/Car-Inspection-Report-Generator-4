import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from jinja2 import Template
from datetime import datetime

# --- Login Credentials ---
USERNAME = "admin"
PASSWORD = "1234"

# --- Initialize login state ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
# --- CSS for green login button ---
st.markdown("""
    <style>
    /* Login Button */
    div.stButton > button:first-child {
        background-color: #28a745;  /* green */
        color: white;
        font-weight: bold;
        padding: 8px 20px;
        font-size: 16px;
        border-radius: 8px;
    }
    div.stButton > button:first-child:hover {
        background-color: #218838; /* darker green on hover */
    }

    /* Optional: make letters bold or bigger if needed */
    .green-letter {
        color: #28a745;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Login function ---
def login():
    st.title("🔒 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state["logged_in"] = True
            st.rerun()  # immediately rerun the app
        else:
            st.error("❌ Incorrect username or password")

# --- Stop app until logged in ---
if not st.session_state["logged_in"]:
    login()
    st.stop()

# ================================
# --- CONFIGURATION ---
# ================================
st.set_page_config(page_title="🚘 Car Inspection Form", layout="wide")

# --- Directories & Templates ---
REPORTS_DIR = "reports"
TEMPLATE_PATH = "templates/report_template.html"
os.makedirs(REPORTS_DIR, exist_ok=True)

# ================================
# --- TABS ---
# ================================
tab1, tab2 = st.tabs(["Inspection Form", "Damage Diagram"])

# ================================
# --- DAMAGE DIAGRAM TAB ---
# ================================
with tab2:
    st.title("Car Damage Diagram")
    with open("CarDamage.jpg", "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()
    
        html_code = f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;">
            <h2 style="text-align:center; margin-bottom:10px;">Car Damage Diagram</h2>
            <canvas id="carCanvas" style="border:1px solid #ccc; max-width:90%; height:auto;"></canvas>
            <select id="damageSelect" style="position:absolute; display:none; padding:5px;">
              <option value="">--Select Damage--</option>
              <option value="A1">A1 - Minor Scratch</option>
              <option value="A2">A2 - Major/Multiple Scratches</option>
              <option value="E1">E1 - Minor Dent</option>
              <option value="E2">E2 - Major/Multiple Dents</option>
              <option value="P">P - Paint Spray ONLY</option>
              <option value="T">T - TOTAL Genuine</option>
              <option value="G1">G1 - Glass Scratches</option>
              <option value="G4">G4 - Glass Chipped</option>
              <option value="S">S - Repaired / Dry Denting</option>
            </select>
            <button id="downloadBtn" style="
                margin-top:15px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #28a745;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: background-color 0.3s;
            ">Download Diagram</button>
        </div>
    
        <script>
        const canvas = document.getElementById('carCanvas');
        const ctx = canvas.getContext('2d');
        const damageSelect = document.getElementById('damageSelect');
        const downloadBtn = document.getElementById('downloadBtn');
        let annotations = [];
    
        const colors = {{
            "A1": "#D8BFD8",
            "A2": "#800080",
            "E1": "#FFA07A",
            "E2": "#FF8C00",
            "G1": "#1E90FF",
            "S": "#FFD700",
            "T": "#FFFF00"
        }};
    
        const img = new Image();
        img.src = "data:image/jpeg;base64,{img_base64}";
        img.onload = () => {{
            const maxWidth = 600;  
            const scale = Math.min(maxWidth / img.naturalWidth, 1);
            canvas.width = img.naturalWidth * scale;
            canvas.height = img.naturalHeight * scale;
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }};
    
        function getCanvasCoordinates(e) {{
            const rect = canvas.getBoundingClientRect();
            let clientX, clientY;
            if (e.touches) {{
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            }} else {{
                clientX = e.clientX;
                clientY = e.clientY;
            }}
            // Compute coordinates relative to canvas
            const x = (clientX - rect.left) * (canvas.width / rect.width);
            const y = (clientY - rect.top) * (canvas.height / rect.height);
            return {{x, y}};
        }}

    
        function showDropdown(x, y, clientX, clientY) {{
            damageSelect.style.left = clientX + 'px';
            damageSelect.style.top = clientY + 'px';
            damageSelect.style.display = 'block';
            damageSelect.dataset.x = x;
            damageSelect.dataset.y = y;
            damageSelect.focus();
        }}
    
        canvas.addEventListener('click', (e) => {{
            const coords = getCanvasCoordinates(e);
            showDropdown(coords.x, coords.y, e.clientX, e.clientY);
        }});
    
        canvas.addEventListener('touchstart', (e) => {{
            e.preventDefault();  // prevent scrolling
            const coords = getCanvasCoordinates(e);
            showDropdown(coords.x, coords.y, e.touches[0].clientX, e.touches[0].clientY);
        }});
    
        damageSelect.addEventListener('change', (e) => {{
            const code = e.target.value;
            if(!code) return;
            annotations.push({{code, x:e.target.dataset.x, y:e.target.dataset.y}});
            ctx.clearRect(0,0,canvas.width,canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            annotations.forEach(a => {{
                const padding = 6;
                ctx.font = 'bold 14px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                const textWidth = ctx.measureText(a.code).width;
                const rectWidth = textWidth + padding*2;
                const rectHeight = 20;
                const bx = a.x - rectWidth/2;
                const by = a.y - rectHeight/2;
                ctx.fillStyle = colors[a.code] || "#ff6666";
                ctx.fillRect(bx, by, rectWidth, rectHeight);
                ctx.strokeStyle = "black";
                ctx.strokeRect(bx, by, rectWidth, rectHeight);
                ctx.fillStyle = "white";
                ctx.fillText(a.code, a.x, a.y);
            }});
            damageSelect.style.display='none';
            damageSelect.value='';
        }});
    
        downloadBtn.addEventListener('click', () => {{
            const link = document.createElement('a');
            link.download = 'car_damage.png';
            link.href = canvas.toDataURL();
            link.click();
        }});
        </script>
        """
    
        components.html(html_code, height=700)



    # ================================
# --- INSPECTION FORM TAB ---
# ================================
with open("CompanyLogo.jpg", "rb") as f:
    logo_bytes = f.read()
    logo_base64 = base64.b64encode(logo_bytes).decode()

with tab1:
    st.markdown(f"""
    <div style="display:flex; align-items:center; margin-bottom:10px;">
        <img src="data:image/png;base64,{logo_base64}" style="height:50px; margin-right:10px;">
        <h1 style="font-size:32px; margin:0;">
            INSPECTION REPORT GENERATOR
        </h1>
    </div>
    <h3 style="margin-top:0;">🧾 Fill the Vehicle Inspection Form</h3>
    """, unsafe_allow_html=True)

    # ========================
    # --- Highlights ---
    # ========================
    with st.expander("Highlights", expanded=False):
        st.write("Upload showcase images of the car (front, rear, side, interior, engine bay)")
        highlight_images = st.file_uploader(
            "Upload Highlight Images", accept_multiple_files=True, type=["jpg", "png"], key="highlight_images"
        )
        reference_id = st.text_input("Reference ID", key="highlight_reference_id")
        mileage = st.text_input("Mileage (km)", key="highlight_mileage")
        color = st.text_input("Color", key="highlight_color")
        fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Hybrid", "Electric"], key="highlight_fuel_type")
        transmission = st.selectbox("Transmission", ["Manual", "Automatic"], key="highlight_transmission")
        drive_type = st.selectbox("Drive Type", ["2WD", "4WD", "AWD"], key="highlight_drive_type")
        pickup_location = st.text_input("Pick-up Location", key="highlight_pickup_location")
        registration_city = st.text_input("Registration City", key="highlight_registration_city")
        registration_type = st.selectbox("Registration Type", ["Private", "Commercial"], key="highlight_registration_type")

    # Convert highlight images to Base64
    highlight_images_b64 = []
    if highlight_images:
        for img_file in highlight_images:
            bytes_data = img_file.read()
            encoded = base64.b64encode(bytes_data).decode()
            highlight_images_b64.append(f"data:{img_file.type};base64,{encoded}")

    # ========================
    # --- Car Details ---
    # ========================
    with st.expander("Car Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            make = st.text_input("Make", key="car_make")
            model = st.text_input("Model", key="car_model")
            variant = st.text_input("Variant", key="car_variant")
            model_year = st.text_input("Model Year", key="car_model_year")
            reg_year = st.text_input("Registration Year", key="car_reg_year")
        with col2:
            engine_capacity = st.text_input("Engine Capacity (cc)", key="car_engine_capacity")
            seating_capacity = st.number_input("Seating Capacity", min_value=1, max_value=20, key="car_seating_capacity")
            color_code = st.text_input("Color Code (if available)", key="car_color_code")
            chassis_number = st.text_input("Chassis Number", key="car_chassis_number")
            engine_number = st.text_input("Engine Number", key="car_engine_number")

    # ========================
    # --- Documents ---
    # ========================
    with st.expander("Documents", expanded=False):
        original_book = st.selectbox("Original Book", ["Yes", "No"], key="doc_original_book")
        original_card = st.selectbox("Original Card", ["Yes", "No"], key="doc_original_card")
        original_file = st.selectbox("Original File", ["Yes", "No"], key="doc_original_file")
        number_plate_condition = st.selectbox("Number Plate Condition", ["Original", "Not Original"], key="doc_number_plate")
        registration_certificate = st.selectbox("Registration Certificate", ["Yes", "No"], key="doc_registration_cert")
        insurance_copy = st.selectbox("Insurance Copy", ["Yes", "No"], key="doc_insurance_copy")
        no_of_owners = st.number_input("Number of Previous Owners", min_value=0, key="doc_no_of_owners")
        no_of_keys = st.number_input("Number of Keys", min_value=0, key="doc_no_of_keys")

    # ========================
    # --- Interior ---
    # ========================
    with st.expander("Interior", expanded=False):
        dashboard = st.selectbox("Dashboard Condition", ["Good", "Average", "Bad"], key="int_dashboard")
        seats = st.selectbox("Seat Condition", ["Good", "Average", "Bad"], key="int_seats")
        roof_liner = st.selectbox("Roof Liner Condition", ["Good", "Average", "Bad"], key="int_roof_liner")
        ac_heater = st.selectbox("A/C & Heater", ["Working", "Not Working"], key="int_ac_heater")
        infotainment = st.selectbox("Infotainment / Stereo", ["Working", "Not Working"], key="int_infotainment")
        seat_belts = st.selectbox("Seat Belts Condition", ["Good", "Average", "Bad"], key="int_seat_belts")
        interior_lights = st.selectbox("Interior Lights", ["Working", "Faulty"], key="int_lights")
        pedals = st.selectbox("Pedals Condition", ["Good", "Worn", "Needs Replacement"], key="int_pedals")
        interior_comments = st.text_area("Interior Comments", key="int_comments")

    # ========================
    # --- Car Body Evaluation ---
    # ========================
    with st.expander("Car Body Evaluation", expanded=False):
        st.write("Upload photos of body evaluation or diagrams")
        body_images = st.file_uploader(
            "Upload Body Evaluation Images", accept_multiple_files=True, type=["jpg", "png"], key="body_images"
        )

        front_bumper = st.selectbox("Front Bumper Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_front_bumper")
        st.text_area("Front Bumper Comments", key="body_front_bumper_comment")

        bonnet = st.selectbox("Bonnet Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_bonnet")
        st.text_area("Bonnet Comments", key="body_bonnet_comment")

        front_windscreen = st.selectbox("Front Windscreen Condition", ["Good", "Cracked", "Replaced"], key="body_front_windscreen")
        st.text_area("Front Windscreen Comments", key="body_front_windscreen_comment")

        front_left_fender = st.selectbox("Front Left Fender Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_front_left_fender")
        st.text_area("Front Left Fender Comments", key="body_front_left_fender_comment")

        left_a_pillar = st.selectbox("Left A-Pillar Condition", ["Good", "Damaged", "Repaired"], key="body_left_a_pillar")
        st.text_area("Left A-Pillar Comments", key="body_left_a_pillar_comment")

        front_left_door = st.selectbox("Front Left Door Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_front_left_door")
        st.text_area("Front Left Door Comments", key="body_front_left_door_comment")

        roof = st.selectbox("Roof Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_roof")
        st.text_area("Roof Comments", key="body_roof_comment")

        left_b_pillar = st.selectbox("Left B-Pillar Condition", ["Good", "Damaged", "Repaired"], key="body_left_b_pillar")
        st.text_area("Left B-Pillar Comments", key="body_left_b_pillar_comment")

        back_left_door = st.selectbox("Back Left Door Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_back_left_door")
        st.text_area("Back Left Door Comments", key="body_back_left_door_comment")

        left_c_pillar = st.selectbox("Left C-Pillar Condition", ["Good", "Damaged", "Repaired"], key="body_left_c_pillar")
        st.text_area("Left C-Pillar Comments", key="body_left_c_pillar_comment")

        left_d_pillar = st.selectbox("Left D-Pillar Condition", ["Good", "Damaged", "Repaired"], key="body_left_d_pillar")
        st.text_area("Left D-Pillar Comments", key="body_left_d_pillar_comment")

        back_left_quarter_panel = st.selectbox("Back Left Quarter Panel Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_back_left_quarter")
        st.text_area("Back Left Quarter Panel Comments", key="body_back_left_quarter_comment")

        rear_bumper = st.selectbox("Rear Bumper Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_rear_bumper")
        st.text_area("Rear Bumper Comments", key="body_rear_bumper_comment")

        trunk_lid = st.selectbox("Trunk Lid Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_trunk_lid")
        st.text_area("Trunk Lid Comments", key="body_trunk_lid_comment")

        back_right_quarter_panel = st.selectbox("Back Right Quarter Panel Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_back_right_quarter")
        st.text_area("Back Right Quarter Panel Comments", key="body_back_right_quarter_comment")

        rear_windscreen = st.selectbox("Rear Windscreen Condition", ["Good", "Cracked", "Replaced"], key="body_rear_windscreen")
        st.text_area("Rear Windscreen Comments", key="body_rear_windscreen_comment")

        right_d_pillar = st.selectbox("Right D-Pillar Condition", ["Good", "Damaged", "Repaired"], key="body_right_d_pillar")
        st.text_area("Right D-Pillar Comments", key="body_right_d_pillar_comment")

        right_c_pillar = st.selectbox("Right C-Pillar Condition", ["Good", "Damaged", "Repaired"], key="body_right_c_pillar")
        st.text_area("Right C-Pillar Comments", key="body_right_c_pillar_comment")

        back_right_door = st.selectbox("Back Right Door Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_back_right_door")
        st.text_area("Back Right Door Comments", key="body_back_right_door_comment")

        right_b_pillar = st.selectbox("Right B-Pillar Condition", ["Good", "Damaged", "Repaired"], key="body_right_b_pillar")
        st.text_area("Right B-Pillar Comments", key="body_right_b_pillar_comment")

        front_right_door = st.selectbox("Front Right Door Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_front_right_door")
        st.text_area("Front Right Door Comments", key="body_front_right_door_comment")

        right_a_pillar = st.selectbox("Right A-Pillar Condition", ["Good", "Damaged", "Repaired"], key="body_right_a_pillar")
        st.text_area("Right A-Pillar Comments", key="body_right_a_pillar_comment")

        front_right_fender = st.selectbox("Front Right Fender Condition", ["Good", "Scratched", "Repaired", "Replaced"], key="body_front_right_fender")
        st.text_area("Front Right Fender Comments", key="body_front_right_fender_comment")

        exterior_condition = st.selectbox("Overall Exterior Condition", ["Excellent", "Good", "Average", "Poor"], key="body_exterior_condition")
        st.text_area("Overall Exterior Comments", key="body_exterior_comment")

        interior_condition = st.selectbox("Overall Interior Condition", ["Excellent", "Good", "Average", "Poor"], key="body_interior_condition")
        st.text_area("Overall Interior Comments", key="body_interior_comment")

        car_body_comments = st.text_area("General Car Body Comments / Observations", key="body_comments")


        # --- Mechanical ---
    with st.expander("Mechanical", expanded=False):
        engine_condition = st.selectbox("Engine Condition", ["Good", "Average", "Weak"], key="mech_engine_condition")
        transmission_function = st.selectbox("Transmission Function", ["Smooth", "Rough", "Needs Service"], key="mech_transmission_function")
        clutch_condition = st.selectbox("Clutch Condition", ["Good", "Slipping", "Needs Replacement"], key="mech_clutch")
        catalytic_converter = st.selectbox("Catalytic Converter Condition", ["Good", "Average", "Faulty"], key="mech_catalytic")
        radiator_condition = st.selectbox("Radiator Condition", ["Good", "Average", "Leaking"], key="mech_radiator")
        engine_noise = st.selectbox("Engine Noise", ["Normal", "Abnormal"], key="mech_engine_noise")
        inner_bonnet_condition = st.selectbox("Inner Bonnet Condition", ["Clean", "Oily", "Damaged"], key="mech_inner_bonnet")
        battery_condition = st.selectbox("Battery Condition", ["Good", "Weak", "Dead"], key='mech_battery')
        abs_present = st.selectbox("Has ABS (Anti-lock Braking System)?", ["Yes", "No"], key="mech_abs")
        exhaust_smoke = st.selectbox("Engine Smoke Condition", ["None", "White", "Black", "Blue"], key="mech_exhaust_smoke")
        engine_oil_condition = st.selectbox("Engine Oil Condition", ["Good", "Dirty", "Low"], key="mech_oil")
        mechanical_comments = st.text_area("Mechanical Comments", key="mech_comments")
    
    
    # --- Suspension ---
    with st.expander("Suspension", expanded=False):
        front_left_shock = st.selectbox("Front Left Shock Absorber Condition", ["Good", "Weak", "Leaking"], key="susp_fl_shock")
        front_right_shock = st.selectbox("Front Right Shock Absorber Condition", ["Good", "Weak", "Leaking"], key="susp_fr_shock")
        back_left_shock = st.selectbox("Back Left Shock Absorber Condition", ["Good", "Weak", "Leaking"], key="susp_bl_shock")
        back_right_shock = st.selectbox("Back Right Shock Absorber Condition", ["Good", "Weak", "Leaking"], key="susp_br_shock")
    
        front_left_axle = st.selectbox("Front Left Axle Condition", ["Good", "Worn", "Damaged"], key="susp_fl_axle")
        front_right_axle = st.selectbox("Front Right Axle Condition", ["Good", "Worn", "Damaged"], key="susp_fr_axle")
        back_left_axle = st.selectbox("Back Left Axle Condition", ["Good", "Worn", "Damaged"], key="susp_bl_axle")
        back_right_axle = st.selectbox("Back Right Axle Condition", ["Good", "Worn", "Damaged"], key="susp_br_axle")
    
        steering_alignment = st.selectbox("Steering Alignment", ["Good", "Off", "Needs Work"], key="susp_steering_alignment")
        suspension_noise = st.selectbox("Suspension Noise", ["None", "Mild", "Severe"], key="susp_noise")
        suspension_comments = st.text_area("Suspension Comments", key="susp_comments")
    
    
    # --- Electrical ---
    with st.expander("Electrical", expanded=False):
        headlights = st.selectbox("Headlights Condition", ["Working", "Faulty", "Scratched"], key="elec_headlights")
        tail_lights = st.selectbox("Tail Lights Condition", ["Working", "Faulty", "Scratched"], key="elec_tail_lights")
        indicators = st.selectbox("Indicators / Blinkers", ["Working", "Faulty"], key="elec_indicators")
        brake_lights = st.selectbox("Brake Lights", ["Working", "Faulty"], key="elec_brake_lights")
        power_windows = st.selectbox("Power Windows", ["Working", "Faulty"], key="elec_power_windows")
        central_locking = st.selectbox("Central Locking", ["Working", "Faulty"], key="elec_central_lock")
        battery_elec = st.selectbox("Battery Condition", ["Good", "Weak", "Dead"], key='elec_battery')
        wiring = st.selectbox("Wiring Condition", ["Good", "Average", "Poor"], key="elec_wiring")
        electrical_comments = st.text_area("Electrical Comments", key="elec_comments")

    
    
    # --- Tires ---
    with st.expander("Tires", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        tire_fl = st.slider("Front Left Tire %", 0, 100, 80, key="tire_fl")
        tire_fr = st.slider("Front Right Tire %", 0, 100, 80, key="tire_fr")
        tire_rl = st.slider("Rear Left Tire %", 0, 100, 80, key="tire_rl")
        tire_rr = st.slider("Rear Right Tire %", 0, 100, 80, key="tire_rr")
        spare_tire_condition = st.selectbox("Spare Tire Condition", ["Available", "Missing", "Damaged"], key="tire_spare")
        tire_comments = st.text_area("Tires Comments", key="tire_comments")
    
    
    # --- Accessories ---
    with st.expander("Accessories", expanded=False):
        has_fog_lamp = st.selectbox("Has Fog Lamp?", ["Yes", "No"], key="acc_fog_lamp")
        has_immobilizer_key = st.selectbox("Has Immobilizer Key?", ["Yes", "No"], key="acc_immobilizer")
        has_push_start = st.selectbox("Has Push Start?", ["Yes", "No"], key="acc_push_start")
        upholstery_type = st.selectbox("Upholstery Type", ["Fabric", "Leather", "Synthetic", "Other"], key="acc_upholstery")
        has_electric_seats = st.selectbox("Has Electric Seats?", ["Yes", "No"], key="acc_electric_seats")
        has_immobiliser = st.selectbox("Has Immobiliser?", ["Yes", "No"], key="acc_immobiliser")
        has_retractable_side_mirrors = st.selectbox("Has Retractable Side Mirrors?", ["Yes", "No"], key="acc_side_mirrors")
        has_tool_kit = st.selectbox("Has Tool Kit?", ["Yes", "No"], key="acc_tool_kit")
        has_puncture_kit = st.selectbox("Has Puncture Kit?", ["Yes", "No"], key="acc_puncture_kit")
        has_spare_wheel = st.selectbox("Has Spare Wheel?", ["Yes", "No"], key="acc_spare_wheel")
    
    
    # --- Test Drive ---
    with st.expander("Test Drive", expanded=False):
        engine_function = st.selectbox("Engine Function", ["Normal", "Abnormal"], key="td_engine_function")
        transmission_condition = st.selectbox("Transmission Condition", ["Smooth", "Rough", "Needs Service"], key="td_transmission_condition")
        brake_function = st.selectbox("Brake Function", ["Good", "Average", "Weak"], key="td_brake_function")
        suspension_function = st.selectbox("Suspension Function", ["Good", "Average", "Weak"], key="td_suspension_function")
        steering_function = st.selectbox("Steering Function", ["Good", "Loose", "Stiff"], key="td_steering_function")
    
        has_radio = st.selectbox("Has Radio?", ["Yes", "No"], key="td_radio")
        has_air_conditioning = st.selectbox("Has Air Conditioning?", ["Yes", "No"], key="td_ac")
        has_power_windows_td = st.selectbox("Has Power Windows?", ["Yes", "No"], key="td_power_windows")
        has_navigation = st.selectbox("Has Navigation System?", ["Yes", "No"], key="td_navigation")
        navigation_condition = st.selectbox("Navigation Condition", ["Working", "Not Working"], key="td_navigation_condition") if has_navigation=="Yes" else None
    
        dashboard_instruments = st.selectbox("Dashboard Instruments Condition", ["Good", "Average", "Faulty"], key="td_dashboard_instruments")
        interior_lights_td = st.selectbox("Interior Light Condition", ["Working", "Faulty"], key="td_interior_lights")
        test_drive_comments = st.text_area("Test Drive / Functional Comments", key="td_comments")
    
    
    # --- Final Comments ---
    with st.expander("Final Comments", expanded=False):
        inspector_name = st.text_input("Inspector Name", key="final_inspector_name")
        overall_condition = st.selectbox("Overall Vehicle Condition", ["Excellent", "Good", "Average", "Poor"], key="final_overall_condition")
        final_comments = st.text_area("Final Remarks / Notes", key="final_comments")
    
    # --- Inject CSS for green button ---
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #28a745;
        color: white;
        padding: 8px 20px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 8px;
    }
    div.stButton > button:first-child:hover {
        background-color: #218838;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("Generate Report"):
        # --- 1. Highlights ---
        highlights = {
            "reference_id": reference_id,
            "mileage": mileage,
            "color": color,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "drive_type": drive_type,
            "pickup_location": pickup_location,
            "registration_city": registration_city,
            "registration_type": registration_type,
            "hilight_image_b64": highlight_images_b64,
            "highlight_images": [f.name for f in highlight_images] if highlight_images else []
        }
    
        # --- 2. Car Details ---
        car_details = {
            "make": make,
            "model": model,
            "variant": variant,
            "model_year": model_year,
            "reg_year": reg_year,
            "engine_capacity": engine_capacity,
            "seating_capacity": seating_capacity,
            "color_code": color_code,
            "chassis_number": chassis_number,
            "engine_number": engine_number
        }
    
        # --- 3. Documents ---
        documents = {
            "original_book": original_book,
            "original_card": original_card,
            "original_file": original_file,
            "number_plate_condition": number_plate_condition,
            "registration_certificate": registration_certificate,
            "insurance_copy": insurance_copy,
            "no_of_owners": no_of_owners,
            "no_of_keys": no_of_keys
        }
    
        # --- 4. Interior ---
        interior = {
            "dashboard": dashboard,
            "seats": seats,
            "roof_liner": roof_liner,
            "ac_heater": ac_heater,
            "infotainment": infotainment,
            "seat_belts": seat_belts,
            "interior_lights": interior_lights,
            "pedals": pedals,
            "interior_comments": interior_comments
        }
    
        # --- 5. Car Body Evaluation ---
        car_body = {
            "body_images": [f.name for f in body_images] if body_images else [],
            "panels": {
                "Front Bumper": front_bumper,
                "Bonnet": bonnet,
                "Front Windscreen": front_windscreen,
                "Front Left Fender": front_left_fender,
                "Left A-Pillar": left_a_pillar,
                "Front Left Door": front_left_door,
                "Roof": roof,
                "Left B-Pillar": left_b_pillar,
                "Back Left Door": back_left_door,
                "Left C-Pillar": left_c_pillar,
                "Left D-Pillar": left_d_pillar,
                "Back Left Quarter Panel": back_left_quarter_panel,
                "Rear Bumper": rear_bumper,
                "Trunk Lid": trunk_lid,
                "Back Right Quarter Panel": back_right_quarter_panel,
                "Rear Windscreen": rear_windscreen,
                "Right D-Pillar": right_d_pillar,
                "Right C-Pillar": right_c_pillar,
                "Back Right Door": back_right_door,
                "Right B-Pillar": right_b_pillar,
                "Front Right Door": front_right_door,
                "Right A-Pillar": right_a_pillar,
                "Front Right Fender": front_right_fender
            },
            "overall_exterior_condition": exterior_condition,
            "overall_interior_condition": interior_condition,
            "comments": car_body_comments
        }
    
        # --- 6. Mechanical ---
        mechanical = {
            "engine_condition": engine_condition,
            "transmission_function": transmission_function,
            "clutch_condition": clutch_condition,
            "catalytic_converter": catalytic_converter,
            "radiator_condition": radiator_condition,
            "engine_noise": engine_noise,
            "inner_bonnet_condition": inner_bonnet_condition,
            "battery_condition": battery_elec,
            "abs_present": abs_present,
            "exhaust_smoke": exhaust_smoke,
            "engine_oil_condition": engine_oil_condition,
            "mechanical_comments": mechanical_comments
        }
    
        # --- 7. Suspension ---
        suspension = {
            "shock_absorbers": {
                "Front Left": front_left_shock,
                "Front Right": front_right_shock,
                "Back Left": back_left_shock,
                "Back Right": back_right_shock
            },
            "axles": {
                "Front Left": front_left_axle,
                "Front Right": front_right_axle,
                "Back Left": back_left_axle,
                "Back Right": back_right_axle
            },
            "steering_alignment": steering_alignment,
            "suspension_noise": suspension_noise,
            "suspension_comments": suspension_comments
        }
    
        # --- 8. Electrical ---
        electrical = {
            "headlights": headlights,
            "tail_lights": tail_lights,
            "indicators": indicators,
            "brake_lights": brake_lights,
            "power_windows": power_windows,
            "central_locking": central_locking,
            "battery_condition": battery_elec,
            "wiring": wiring,
            "electrical_comments": electrical_comments
        }
    
        # --- 9. Tires ---
        tires = {
            "front_left": tire_fl,
            "front_right": tire_fr,
            "rear_left": tire_rl,
            "rear_right": tire_rr,
            "spare_tire_condition": spare_tire_condition,
            "comments": tire_comments
        }
    
        # --- 10. Accessories ---
        accessories = {
            "fog_lamp": has_fog_lamp,
            "immobilizer_key": has_immobilizer_key,
            "push_start": has_push_start,
            "upholstery_type": upholstery_type,
            "electric_seats": has_electric_seats,
            "immobiliser": has_immobiliser,
            "retractable_side_mirrors": has_retractable_side_mirrors,
            "tool_kit": has_tool_kit,
            "puncture_kit": has_puncture_kit,
            "spare_wheel": has_spare_wheel
        }
    
        # --- 11. Test Drive ---
        test_drive = {
            "engine_function": engine_function,
            "transmission_condition": transmission_condition,
            "brake_function": brake_function,
            "suspension_function": suspension_function,
            "steering_function": steering_function,
            "has_radio": has_radio,
            "has_air_conditioning": has_air_conditioning,
            "has_power_windows": has_power_windows_td,
            "has_navigation": has_navigation,
            "navigation_condition": navigation_condition if has_navigation=="Yes" else "N/A",
            "dashboard_instruments": dashboard_instruments,
            "interior_light_condition": interior_lights_td,
            "comments": test_drive_comments
        }
    
        # --- 12. Final Comments ---
        final = {
            "inspector_name": inspector_name,
            "overall_condition": overall_condition,
            "final_comments": final_comments
        }
    
        # --- New function: Calculate condition-based percentage ---
        def calculate_condition_score(section_dict, exclude_fields=None):
            """
            Calculate a condition-based percentage for a section dictionary.

            Rules:
            - Presence-only fields (make/model/chassis/etc.) -> 100 if non-empty, else 0.
            - Condition keywords (good/average/scratched/damaged/working/not working/yes/no etc.) -> mapped scores.
            - Numeric values (ints/floats) -> treated as percent if in 0-100 range, otherwise normalized to [0,100] heuristically.
            - Nested dicts -> handled recursively (average of nested items).
            - Unknown strings -> neutral mid score (0.7 by default), but lowered from previous behavior to avoid skew.
            """

            if exclude_fields is None:
                exclude_fields = []

            # Fields that are identity / presence-only (not conditions)
            PRESENCE_ONLY = {
                "make", "model", "variant", "model_year", "reg_year", "registration_city",
                "registration_type", "chassis_number", "engine_number", "color_code",
                "reference_id", "pickup_location", "inspector_name"
            }

            # Mapping for condition-like words -> score between 0 and 1
            condition_map = {
                "excellent": 1.0,
                "like new": 1.0,
                "good": 0.95,
                "working": 0.95,
                "yes": 1.0,
                "ok": 0.8,
                "okay": 0.8,
                "average": 0.7,
                "fair": 0.65,
                "minor": 0.75,
                "minor scratch": 0.75,
                "scratched": 0.5,
                "repaired": 0.6,
                "replaced": 0.9,
                "needs service": 0.4,
                "needs replacement": 0.2,
                "worn": 0.45,
                "weak": 0.3,
                "leaking": 0.2,
                "damaged": 0.15,
                "bad": 0.15,
                "poor": 0.1,
                "not working": 0.1,
                "no": 0.0,
                "missing": 0.0,
                "dead": 0.0,
                "none": 0.0,
                "n/a": 0.0,
                "na": 0.0
            }

            # Helper to score a single value
            def score_value(key, value):
                # exclude explicit fields
                if key in exclude_fields:
                    return None

                # nested dict -> compute nested average
                if isinstance(value, dict):
                    nested = []
                    for k, v in value.items():
                        s = score_value(k, v)
                        if s is not None:
                            nested.append(s)
                    return round(sum(nested) / len(nested), 3) if nested else None

                # lists -> attempt to score each item (presence or nested)
                if isinstance(value, list):
                    if not value:
                        return None
                    # if list of strings/images -> treat presence as full
                    # else try to score items
                    scores = []
                    for itm in value:
                        if isinstance(itm, (str, int, float)):
                            # presence for image strings
                            if isinstance(itm, str) and (itm.lower().startswith("data:") or len(itm) > 0):
                                scores.append(1.0)
                            elif isinstance(itm, (int, float)):
                                # numeric in list: normalize if 0-100 treat as percent
                                n = itm
                                if 0 <= n <= 100:
                                    scores.append(n/100.0)
                                else:
                                    scores.append(0.7)
                            else:
                                scores.append(0.7)
                        elif isinstance(itm, dict):
                            nested_score = score_value(key, itm)
                            if nested_score is not None:
                                scores.append(nested_score)
                    return round(sum(scores) / len(scores), 3) if scores else None

                # None or empty string -> no score
                if value is None:
                    return None
                vstr = str(value).strip()
                if vstr == "":
                    return None

                # If key is presence only -> 100%
                if key.lower() in PRESENCE_ONLY:
                    return 1.0

                # If it's a numeric-like string or number -> try to interpret
                try:
                    num = float(vstr.replace(",", "").replace("%", ""))
                    # if already 0-100 treat as percent
                    if 0 <= num <= 100:
                        return max(0.0, min(1.0, num / 100.0))
                    # otherwise normalize with a heuristic (cap to 100)
                    # e.g., seating_capacity, engine_capacity -> presence-based
                    # default to presence mid score
                    return 0.9 if num > 0 else 0.0
                except Exception:
                    pass
                
                # Lowercase textual mapping
                key_lower = vstr.lower()
                if key_lower in condition_map:
                    return condition_map[key_lower]

                # Some common multi-word matching
                for kword, score in condition_map.items():
                    if kword in key_lower:
                        return score

                # Unknown string - give neutral mid score (0.7) instead of high 0.95
                # This avoids single unrecognized field from pulling section to 70-95% incorrectly.
                return 0.7

            # iterate and compute
            scores = []
            for k, v in section_dict.items():
                s = score_value(k, v)
                if s is not None:
                    scores.append(s)

            if not scores:
                return 0.0

            # final percent 0-100
            percent = round((sum(scores) / len(scores)) * 100, 1)
            return percent


        # --- Now compute section scores using the new function ---
        highlights_completion = calculate_condition_score(
            highlights, exclude_fields=["hilight_image_b64", "highlight_images"]
        )
        car_details_completion = calculate_condition_score(car_details)
        documents_completion = calculate_condition_score(documents)
        interior_completion = calculate_condition_score(interior, exclude_fields=["interior_comments"])
        car_body_completion = calculate_condition_score(car_body.get("panels", {}))
        mechanical_completion = calculate_condition_score(mechanical, exclude_fields=["mechanical_comments"])
        
        # handle suspension (both parts merged)
        suspension_data = {}
        if "shock_absorbers" in suspension:
            suspension_data.update(suspension["shock_absorbers"])
        if "axles" in suspension:
            suspension_data.update(suspension["axles"])
        suspension_completion = calculate_condition_score(suspension_data)
        
        electrical_completion = calculate_condition_score(electrical, exclude_fields=["electrical_comments"])
        tires_completion = calculate_condition_score(tires, exclude_fields=["comments"])
        accessories_completion = calculate_condition_score(accessories)
        test_drive_completion = calculate_condition_score(test_drive, exclude_fields=["comments"])
        final_completion = calculate_condition_score(final)
        
        # --- Completion dictionary ---
        completion = {
            "highlights": highlights_completion,
            "car_details": car_details_completion,
            "documents": documents_completion,
            "interior": interior_completion,
            "car_body": car_body_completion,
            "mechanical": mechanical_completion,
            "suspension": suspension_completion,
            "electrical": electrical_completion,
            "tires": tires_completion,
            "accessories": accessories_completion,
            "test_drive": test_drive_completion,
            "final": final_completion
        }
        
        # --- Calculate overall condition ---
        all_scores = [v for v in completion.values() if v > 0]
        overall_condition = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        


        # --- ✅ Calculate Overall Vehicle Condition Percentage ---
        section_scores = [v for v in completion.values() if isinstance(v, (int, float))]
        if section_scores:
            overall_condition_percent = round(sum(section_scores) / len(section_scores), 1)
        else:
            overall_condition_percent = 0
        def calculate_condition_percent(section_dict):
            score_map = {"Good": 100, "Average": 60, "Bad": 30, "Poor": 10, "N/A": 0, "": 0}
            valid_values = [score_map.get(str(v).title(), 0) for v in section_dict.values() if isinstance(v, str)]
            if not valid_values:
                return 0
            return round(sum(valid_values) / len(valid_values), 1)
        import base64

        with open("CompanyLogo.jpg", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        with open(TEMPLATE_PATH , "r", encoding='utf-8') as f:
            template = Template(f.read())

        # --- Render the HTML template ---
        html = template.render(
            date=datetime.now().strftime("%d-%b-%Y"),
            highlights=highlights,
            car_details=car_details,
            documents=documents,
            interior=interior,
            car_body=car_body,
            car_body_panels=car_body['panels'],
            mechanical=mechanical,
            suspension=suspension,
            suspension_parts={
                "shock_absorbers": suspension["shock_absorbers"],
                "axles": suspension["axles"]
            },
            electrical=electrical,
            tires=tires,
            accessories=accessories,
            test_drive=test_drive,
            final=final,
            completion=completion,
            overall_condition=overall_condition_percent,
            logo_base64=logo_base64,  # ✅ pass it to template
        )
        
        # --- Convert to bytes for download ---
        report_bytes = html.encode("utf-8")
        report_filename = f"{make}_{model}_report.html"
        st.markdown("""
            <style>
            div.stDownloadButton > button:first-child {
                background-color: #28a745;
                color: white;
                font-weight: bold;
            }
            div.stDownloadButton > button:first-child:hover {
                background-color: #218838;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)

        # --- Download button ---
        st.download_button(
            label="📥 Download Report",
            data=report_bytes,
            file_name=report_filename,
            mime="text/html"
        )
    
        st.success("✅ Report ready for download!")
        st.balloons()
    
