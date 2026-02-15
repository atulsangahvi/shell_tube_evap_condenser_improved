"""
MASTER HEAT EXCHANGER DESIGNER
Unified application combining all functionality

Features:
- Evaporator design (DX type)
- Condenser design (Standard + Advanced segment method)
- TEMA 10th Edition compliance
- Interactive visual interfaces
"""

import streamlit as st
import sys
from pathlib import Path

# Add modules directory to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="TEMA Heat Exchanger Designer",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PASSWORD PROTECTION
# ============================================================================

def check_password():
    """Password protection for the app"""
    def password_entered():
        if st.session_state["password"] == "Semaanju":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Enter Password", type="password", on_change=password_entered, key="password"
        )
        st.write("*Please enter the password to access the design tool*")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Enter Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# Check password first
if not check_password():
    st.stop()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🌡️ TEMA Heat Exchanger Designer</h1>', unsafe_allow_html=True)
st.markdown("**Professional tool for DX evaporators and condensers - TEMA 10th Edition**")

# ============================================================================
# SIDEBAR: APPLICATION SELECTION
# ============================================================================

st.sidebar.title("⚙️ Application Settings")

app_mode = st.sidebar.selectbox(
    "Select Application",
    [
        "🏠 Home",
        "❄️ DX Evaporator Designer",
        "🔥 Condenser Designer (Standard)",
        "🔧 Condenser Designer (Professional)",
        "📚 Documentation"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This tool provides comprehensive design capabilities for:\n\n"
    "- **DX Evaporators** (refrigerant in tubes)\n"
    "- **Condensers** (standard or advanced methods)\n\n"
    "All calculations comply with **TEMA 10th Edition** standards."
)

# ============================================================================
# ROUTE TO APPROPRIATE APPLICATION
# ============================================================================

if app_mode == "🏠 Home":
    # Home page
    st.markdown("## Welcome to TEMA Heat Exchanger Designer")
    
    st.markdown("""
    This professional design tool provides comprehensive capabilities for refrigeration 
    and air conditioning heat exchangers.
    
    ### 🎯 Select Your Application:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### ❄️ DX Evaporator Designer
        - Direct expansion evaporators
        - Refrigerant in tubes (two-phase)
        - Water/glycol on shell side
        - Shah evaporation correlation
        - TEMA compliant
        
        **Use for:** Chillers, cooling systems, process cooling
        """)
        
        if st.button("Open Evaporator Designer", key="btn_evap"):
            st.session_state.app_mode = "❄️ DX Evaporator Designer"
            st.rerun()
    
    with col2:
        st.markdown("""
        #### 🔥 Condenser Designer
        
        **Standard Method:**
        - Fast calculation
        - Area distribution method
        - Shell-side refrigerant
        - Good for preliminary design
        
        **Professional Method:** ⭐ NEW!
        - Shell-side or Tube-side refrigerant
        - Row-based allocation (DX mode)
        - Interactive TEMA diagrams
        - Subcooling optimization
        - TEMA BEM/BEU/AEM/AES support
        
        **Use for:** Heat rejection, condensing units, DX systems
        """)
        
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button("Standard Method", key="btn_cond_std"):
                st.session_state.app_mode = "🔥 Condenser Designer (Standard)"
                st.rerun()
        with col2b:
            if st.button("Professional Method ⭐", key="btn_cond_pro", type="primary"):
                st.session_state.app_mode = "🔧 Condenser Designer (Professional)"
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Recent Updates")
    st.success("""
    ✅ **Latest Version - February 2026:**
    - ⭐ NEW: Professional Condenser Designer with two modes
    - ⭐ Shell-side refrigerant (traditional BEM/AEM)
    - ⭐ Tube-side refrigerant (DX) with row-based allocation
    - ⭐ Interactive subcooling zone optimization
    - ✅ Official TEMA diagrams integrated
    - ✅ TEMA 10th Edition compliant
    - ✅ All critical calculation fixes applied
    """)

elif app_mode == "❄️ DX Evaporator Designer":
    # Import and run evaporator from original corrected code
    st.markdown("## ❄️ DX Evaporator Designer")
    
    try:
        # Import the corrected evaporator/condenser code
        from shell_tube_evap_condenser_CORRECTED import (
            HeatExchangerDesigner,
            create_input_section,
            display_results
        )
        
        # Initialize designer
        if 'designer' not in st.session_state:
            st.session_state.designer = HeatExchangerDesigner()
        
        designer = st.session_state.designer
        
        # Create input section
        inputs = create_input_section(designer, hx_type="evaporator")
        
        # Calculate button
        if st.button("🔄 Calculate Evaporator Performance", type="primary"):
            with st.spinner("Calculating..."):
                results = designer.design_evaporator(inputs)
                st.session_state.evap_results = results
        
        # Display results if available
        if 'evap_results' in st.session_state:
            display_results(st.session_state.evap_results, hx_type="evaporator")
    
    except Exception as e:
        st.error(f"Error loading evaporator designer: {str(e)}")
        st.exception(e)
        st.info("Make sure 'shell_tube_evap_condenser_CORRECTED.py' is in the same directory")

elif app_mode == "🔥 Condenser Designer (Standard)":
    # Import and run condenser from original corrected code
    st.markdown("## 🔥 Condenser Designer (Standard Method)")
    
    try:
        from shell_tube_evap_condenser_CORRECTED import (
            HeatExchangerDesigner,
            create_input_section,
            display_results
        )
        
        # Initialize designer
        if 'designer' not in st.session_state:
            st.session_state.designer = HeatExchangerDesigner()
        
        designer = st.session_state.designer
        
        # Create input section
        inputs = create_input_section(designer, hx_type="condenser")
        
        # Calculate button
        if st.button("🔄 Calculate Condenser Performance", type="primary"):
            with st.spinner("Calculating..."):
                results = designer.design_condenser(inputs)
                st.session_state.cond_results = results
        
        # Display results if available
        if 'cond_results' in st.session_state:
            display_results(st.session_state.cond_results, hx_type="condenser")
    
    except Exception as e:
        st.error(f"Error loading condenser designer: {str(e)}")
        st.exception(e)
        st.info("Make sure 'shell_tube_evap_condenser_CORRECTED.py' is in the same directory")

elif app_mode == "🔧 Condenser Designer (Professional)":
    # Import and run professional condenser designer
    st.markdown("## 🔧 Professional Condenser Designer")
    
    try:
        from professional_condenser_designer import ProfessionalCondenserDesigner
        
        # Run the professional designer
        designer = ProfessionalCondenserDesigner()
        designer.run()
    
    except Exception as e:
        st.error(f"Error loading professional condenser designer: {str(e)}")
        st.exception(e)
        st.info("""
        Make sure 'professional_condenser_designer.py' is in the same directory as app.py
        """)

elif app_mode == "📚 Documentation":
    # Documentation page
    st.markdown("## 📚 Documentation")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Quick Start",
        "Evaporator Guide",
        "Condenser Guide",
        "TEMA Standards"
    ])
    
    with tab1:
        st.markdown("""
        ### Quick Start Guide
        
        #### 1. Select Your Application
        From the sidebar, choose:
        - **DX Evaporator** for evaporator design
        - **Condenser (Standard)** for fast condenser calculations
        - **Condenser (Advanced)** for detailed segment-by-segment analysis
        
        #### 2. Enter Design Parameters
        - Refrigerant type and flow rate
        - Water/glycol properties
        - Geometry (tubes, length, etc.)
        
        #### 3. Calculate & Review Results
        - Click "Calculate Performance"
        - Review detailed results
        - Check TEMA compliance
        - Export reports if needed
        
        #### 4. Iterate as Needed
        - Adjust parameters based on results
        - Compare different configurations
        - Optimize design
        """)
    
    with tab2:
        st.markdown("""
        ### DX Evaporator Design Guide
        
        #### Application
        Direct expansion evaporators for refrigeration and A/C systems.
        
        #### Configuration
        - **Refrigerant:** Inside tubes (two-phase flow)
        - **Water/Glycol:** Shell side (single phase)
        
        #### Key Parameters
        - Evaporating temperature
        - Inlet quality (typically 20-40%)
        - Required superheat (typically 5-10 K)
        
        #### Correlations Used
        - **Evaporation:** Shah correlation (improved)
        - **Superheat:** Single-phase Gnielinski
        - **Shell-side:** Bell-Delaware method
        
        #### TEMA Compliance
        All designs checked against TEMA 10th Edition:
        - Tube selection (Table D-7)
        - Baffle spacing (RCB-4.5)
        - Vibration analysis (Section 6)
        """)
    
    with tab3:
        st.markdown("""
        ### Condenser Design Guide
        
        #### Two Methods Available
        
        **Standard Method:**
        - Fast calculation (seconds)
        - Area distribution approach
        - Shell-side refrigerant (traditional)
        - Good for preliminary design
        - All TEMA compliance checks
        
        **Professional Method:** ⭐ NEW!
        - **Two Operating Modes:**
          
          **Mode A: Shell-Side Refrigerant (Traditional)**
          - Refrigerant condenses on shell side
          - Water/glycol in tubes
          - TEMA types: BEM, AEM, AES
          - Vertical cut baffles (drainage)
          - Simple area-based calculation
          
          **Mode B: Tube-Side Refrigerant (DX)** ⭐
          - Refrigerant in tubes (phase-changing)
          - Water/glycol on shell side (cross-flow)
          - TEMA types: BEM, BEU
          - Horizontal cut baffles (zigzag flow)
          - **ROW-BASED allocation** with user control
          - Interactive subcooling optimization
        
        #### DX Condenser Workflow (Mode B)
        
        **Step 1: Calculate Requirements**
        - Enter design parameters
        - Program calculates required rows per zone:
          - Desuperheat zone
          - Condensing zone
          - Subcooling zone
        
        **Step 2: Allocate Rows**
        - See recommended allocation
        - Adjust rows for each zone
        - Real-time validation
        
        **Step 3: Optimize Performance**
        - View actual subcooling achieved
        - Get warnings if zones undersized
        - Follow optimization recommendations
        - Iterate until satisfied
        
        #### Configuration Selection Guide
        
        **Choose Shell-Side Refrigerant When:**
        - Large tonnage systems
        - Flooded condenser design
        - Standard HVAC/refrigeration
        - Cost-effective solution needed
        
        **Choose Tube-Side Refrigerant (DX) When:**
        - Direct expansion systems
        - High-pressure refrigerants (R410A)
        - Precise subcooling control needed
        - Want to minimize refrigerant charge
        - Need to handle thermal expansion
        
        #### Three-Region Calculation
        1. **Desuperheat:** Vapor → Saturated vapor
        2. **Condensation:** Phase change (main zone)
        3. **Subcooling:** Saturated liquid → Subcooled
        
        #### Common Issues & Solutions
        
        **Subcooling Inadequate (DX Mode):**
        - Allocate more rows to subcooling zone
        - Reduce water inlet temperature
        - Increase tube length
        - Add dedicated subcooler section
        
        **High Pressure Drop:**
        - Reduce number of passes
        - Increase tube size
        - Reduce baffle count
        - Check tube-side velocity
        """)
    
    with tab4:
        st.markdown("""
        ### TEMA 10th Edition Standards
        
        #### TEMA Classifications
        
        **Class R:** Severe requirements (petroleum, chemical)
        **Class C:** Moderate requirements (commercial, HVAC)
        **Class B:** Chemical process service
        
        #### TEMA Types (Front-Shell-Rear)
        
        **Common Types:**
        - **AES:** Fixed tubesheet, floating head
        - **AEL:** Fixed both ends (lowest cost)
        - **BEU:** Bonnet, U-tube bundle
        - **CFU:** Two-pass shell, U-tube
        
        **Zoned Types (for condensers):**
        - **AES-Z:** Fixed tubesheet with zone partitions
        - **AEL-Z:** Fixed both ends with zone partitions
        
        #### Key Requirements
        
        **Tubes:**
        - Standard sizes from Table D-7
        - BWG thickness per pressure rating
        - Material selection guidelines
        
        **Baffles:**
        - Minimum spacing: 1/5 shell ID or 2"
        - Maximum unsupported span per material/temp
        - Segmental cut: typically 20-25%
        
        **Vibration:**
        - Natural frequency calculation
        - Critical velocity check
        - Safety factor ≥ 1.5 required
        
        #### Fouling Resistances
        Used from TEMA Table RGP-T-2.4:
        - Cooling tower water: 0.000176 m²·K/W
        - Refrigerant liquid: 0.000176 m²·K/W
        - Refrigerant vapor: 0.000352 m²·K/W
        - Glycol solutions: 0.000352 m²·K/W
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 0.8rem;'>
    <p>TEMA Heat Exchanger Designer</p>
    <p>Version 2.0 - February 2026</p>
    <p>Compliant with TEMA 10th Edition</p>
</div>
""", unsafe_allow_html=True)
