import streamlit as st
import pandas as pd
import weasyprint
import base64

# --- Page Configuration ---
st.set_page_config(page_title="Golden Road Dispatch App", layout="wide", page_icon="✈️")

st.title("The Golden Road: Flight Dispatch & Kneeboard Generator")
st.markdown("Enter your flight details below. Your custom analog VFR kneeboard will be generated as a print-ready PDF.")

# --- UI: Dispatch Details ---
st.header("1. Flight Dispatch Details")
col1, col2, col3, col4 = st.columns(4)
with col1:
    aircraft = st.text_input("Aircraft", value="PA-28-161 (Warrior II)")
    departure = st.text_input("Departure (ICAO)", value="KAKR")
with col2:
    callsign = st.text_input("Callsign", value="N4302V")
    destination = st.text_input("Destination (ICAO)", value="KINT")
with col3:
    cruise_alt = st.text_input("Cruise Altitude", value="7,500' (VFR)")
    fuel_usable = st.text_input("Fuel Usable", value="48 US Gal")
with col4:
    est_ete = st.text_input("Estimated ETE", value="2h 35m")
    est_burn = st.text_input("Estimated Burn", value="22.0 Gal")

leg_title = st.text_input("Leg Title / Description", value="Leg 1: Coal to Hills")

# --- UI: Frequencies ---
st.header("2. Primary Frequencies")
freq_df = pd.DataFrame([
    {"Facility": "DEP ATIS", "Freq": "126.85"},
    {"Facility": "DEP TWR", "Freq": "118.30"},
    {"Facility": "DEP GND", "Freq": "121.70"},
    {"Facility": "DEP APP", "Freq": "118.25"},
    {"Facility": "NAV 1 (VOR)", "Freq": "114.20"},
    {"Facility": "NAV 2 (VOR)", "Freq": "110.80"},
    {"Facility": "ARR ATIS", "Freq": "121.05"},
    {"Facility": "ARR TWR", "Freq": "118.50"},
    {"Facility": "ARR GND", "Freq": "121.90"}
])
freq_data = st.data_editor(freq_df, num_rows="dynamic", use_container_width=True)

# --- UI: Navigation Log ---
st.header("3. Analog Navigation Log (Dead-Reckoning)")
nav_df = pd.DataFrame([
    {"Waypoint": "KAKR", "Nav Freq": "--", "Radial": "--", "Heading": "--", "Alt": "1,067'", "Dist": "0", "ETE": "0:00", "Remarks": "Akron Fulton Departure"},
    {"Waypoint": "CANTON", "Nav Freq": "114.40", "Radial": "ACO R-175", "Heading": "180°", "Alt": "3,500'", "Dist": "12", "ETE": "0:08", "Remarks": "Visual: Stadium"},
    {"Waypoint": "KINT", "Nav Freq": "--", "Radial": "--", "Heading": "155°", "Alt": "1,970'", "Dist": "20", "ETE": "0:11", "Remarks": "Winston-Salem Arrival"}
])
nav_data = st.data_editor(nav_df, num_rows="dynamic", use_container_width=True)

# --- PDF Generation Engine ---
st.header("4. Generate Kneeboard")
if st.button("Generate Pilot's Kneeboard PDF", type="primary"):
    
    # Build Frequency Table HTML
    freq_headers = "".join([f"<th>{row['Facility']}</th>" for _, row in freq_data.iterrows()])
    freq_values = "".join([f"<td>{row['Freq']}</td>" for _, row in freq_data.iterrows()])
    
    # Build Nav Log Table HTML
    nav_rows = ""
    for _, row in nav_data.iterrows():
        nav_rows += f"""
        <tr>
            <td class="nav-wpt">{row['Waypoint']}</td>
            <td class="nav-mono">{row['Nav Freq']}</td>
            <td class="nav-mono">{row['Radial']}</td>
            <td class="nav-mono">{row['Heading']}</td>
            <td class="nav-mono">{row['Alt']}</td>
            <td class="nav-mono">{row['Dist']}</td>
            <td class="nav-mono">{row['ETE']}</td>
            <td class="nav-empty"></td>
            <td class="nav-empty"></td>
            <td class="nav-remarks">{row['Remarks']}</td>
        </tr>
        """

    # Core HTML/CSS Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; }}
        @page {{ size: letter; margin: 8mm; background-color: #FAF8F5; }}
        body {{ font-family: sans-serif; color: #2b2b2b; margin: 0; padding: 0; font-size: 8.5pt; background-color: #FAF8F5; }}
        
        .header-table {{ width: 100%; border-collapse: collapse; margin-bottom: 5px; }}
        .header-logo {{ background-color: #1a252c; color: #e9c46a; padding: 8px 12px; border-radius: 4px 0 0 4px; }}
        .header-logo h1 {{ margin: 0; font-size: 14pt; font-weight: 800; text-transform: uppercase; color: #e9c46a; }}
        .header-logo p {{ margin: 2px 0 0 0; font-size: 7.5pt; font-style: italic; color: #f4f1de; }}
        .header-meta {{ background-color: #e9c46a; color: #1a252c; padding: 8px 12px; text-align: right; border-radius: 0 4px 4px 0; width: 35%; }}
        .header-meta h2 {{ margin: 0; font-size: 11pt; font-weight: 700; text-transform: uppercase; }}
        .header-meta p {{ margin: 2px 0 0 0; font-size: 7.5pt; font-weight: bold; }}
        
        .layout-table {{ width: 100%; border-collapse: collapse; margin-bottom: 6px; }}
        .layout-cell {{ vertical-align: top; padding: 0; }}
        .panel {{ border: 1px solid #d4cfb4; background-color: #fbfbf9; border-radius: 4px; padding: 6px; margin-bottom: 6px; }}
        .panel-title {{ background-color: #1a252c; color: #ffffff; font-size: 8pt; font-weight: bold; text-transform: uppercase; padding: 3px 6px; margin: -6px -6px 6px -6px; border-radius: 3px 3px 0 0; }}
        .panel-title span {{ color: #e9c46a; }}
        
        .field-grid {{ width: 100%; border-collapse: collapse; }}
        .field-grid td {{ padding: 3px 4px; border: 1px solid #e5e0cc; font-size: 8pt; }}
        .field-label {{ font-weight: bold; color: #5c5540; font-size: 7pt; text-transform: uppercase; width: 20%; background-color: #f2efe9; }}
        .field-value {{ font-family: monospace; font-weight: bold; background-color: #ffffff; }}
        
        .freq-table {{ width: 100%; border-collapse: collapse; }}
        .freq-table th {{ background-color: #5c5540; color: #ffffff; font-size: 7pt; padding: 3px; border: 1px solid #484333; }}
        .freq-table td {{ border: 1px solid #d4cfb4; padding: 4px; text-align: center; font-family: monospace; font-weight: bold; background-color: #ffffff; }}
        
        .nav-table {{ width: 100%; border-collapse: collapse; margin-top: 2px; }}
        .nav-table th {{ background-color: #1a252c; color: #ffffff; font-size: 7.5pt; padding: 4px 3px; border: 1px solid #1a252c; }}
        .nav-table th.accent {{ background-color: #e9c46a; color: #1a252c; }}
        .nav-table td {{ border: 1px solid #c8c2a3; padding: 4px 3px; text-align: center; font-size: 8pt; }}
        .nav-wpt {{ font-weight: bold; text-align: left; padding-left: 5px; }}
        .nav-mono {{ font-family: monospace; font-weight: bold; }}
        .nav-remarks {{ text-align: left; font-size: 7.5pt; padding-left: 5px; }}
        .nav-empty {{ background-color: #fff9e6 !important; border: 1.5px solid #d4af37 !important; width: 32px; }}
        
        .scratch-line {{ border-bottom: 1px dotted #999; height: 16px; margin-top: 4px; }}
        .footer-brand {{ margin-top: 5px; border-top: 1px solid #d4cfb4; padding-top: 4px; font-size: 7pt; color: #777260; text-align: center; text-transform: uppercase; letter-spacing: 1px; }}
    </style>
    </head>
    <body>
        <table class="header-table">
            <tr>
                <td class="header-logo">
                    <h1>The Golden Road to Unlimited Flights</h1>
                    <p>Analog VFR Dead-Reckoning & Steam Gauge Navigation Log</p>
                </td>
                <td class="header-meta">
                    <h2>{leg_title}</h2>
                    <p>{departure} &rarr; {destination}</p>
                </td>
            </tr>
        </table>
        
        <table class="layout-table">
            <tr>
                <td class="layout-cell" style="width: 50%; padding-right: 4px;">
                    <div class="panel" style="height: 108px;">
                        <div class="panel-title"><span>01</span> Flight Dispatch & Aircraft</div>
                        <table class="field-grid">
                            <tr><td class="field-label">Aircraft</td><td class="field-value">{aircraft}</td><td class="field-label">Callsign</td><td class="field-value">{callsign}</td></tr>
                            <tr><td class="field-label">Departure</td><td class="field-value">{departure}</td><td class="field-label">Destination</td><td class="field-value">{destination}</td></tr>
                            <tr><td class="field-label">Cruise Alt</td><td class="field-value">{cruise_alt}</td><td class="field-label">Est ETE</td><td class="field-value">{est_ete}</td></tr>
                            <tr><td class="field-label">Fuel Usable</td><td class="field-value">{fuel_usable}</td><td class="field-label">Est Burn</td><td class="field-value">{est_burn}</td></tr>
                        </table>
                    </div>
                </td>
                <td class="layout-cell" style="width: 50%; padding-left: 4px;">
                    <div class="panel" style="height: 108px;">
                        <div class="panel-title"><span>02</span> SayIntentions.AI Clearance / CRAFT</div>
                        <div style="font-family: monospace; font-size: 7.5pt; color: #333;">
                            <strong>C</strong> (Clnc Limit): <span style="border-bottom: 1px solid #999; display: inline-block; width: 140px; height: 12px;"></span><br>
                            <strong>R</strong> (Route): &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;___________________________<br>
                            <strong>A</strong> (Altitude): &nbsp;&nbsp;<span style="border-bottom: 1px solid #999; display: inline-block; width: 140px; height: 12px;"></span><br>
                            <strong>F</strong> (Freq): &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="border-bottom: 1px solid #999; display: inline-block; width: 140px; height: 12px;"></span><br>
                            <strong>T</strong> (Transponder): <span style="border-bottom: 1px solid #999; display: inline-block; width: 100px; height: 12px;"></span>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
        
        <div class="panel">
            <div class="panel-title"><span>03</span> Communication & Navigation Frequencies</div>
            <table class="freq-table">
                <tr>{freq_headers}</tr>
                <tr>{freq_values}</tr>
            </table>
        </div>
        
        <div class="panel">
            <div class="panel-title"><span>04</span> VFR Navigation Log &mdash; No GPS / Steam Gauges Only</div>
            <table class="nav-table">
                <thead>
                    <tr>
                        <th style="width: 15%;">Waypoint / Fix</th><th style="width: 10%;">NAV Freq</th><th style="width: 8%;">Ident / Rad</th>
                        <th style="width: 8%;">Heading (MH)</th><th style="width: 8%;">Alt (ft)</th><th style="width: 8%;">Dist (NM)</th>
                        <th style="width: 8%;">Est ETE</th><th class="accent" style="width: 8%;">Act ATE</th><th class="accent" style="width: 8%;">Fuel Rem</th>
                        <th style="width: 19%;">Remarks / Sightseeing</th>
                    </tr>
                </thead>
                <tbody>{nav_rows}</tbody>
            </table>
        </div>
        
        <div class="panel" style="margin-top: 6px;">
            <div class="panel-title"><span>05</span> ATIS & ATC Flight Notes Scratchpad</div>
            <div class="scratch-line">DEP ATIS:</div>
            <div class="scratch-line">ARR ATIS:</div>
            <div class="scratch-line">Enroute / SayIntentions Notes:</div>
        </div>
        
        <div class="footer-brand">The Golden Road &bull; Fly the Music, Live the Flight</div>
    </body>
    </html>
    """

    # Generate PDF using WeasyPrint
    try:
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        
        st.success("✅ Kneeboard generated successfully!")
        
        # Provide Download Button
        st.download_button(
            label="⬇️ Download Kneeboard PDF",
            data=pdf_bytes,
            file_name=f"Kneeboard_{departure}_to_{destination}.pdf",
            mime="application/pdf",
            type="primary"
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
