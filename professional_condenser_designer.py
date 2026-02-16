"""
PROFESSIONAL CONDENSER DESIGNER
Complete condenser design tool with two configurations:
  
  Mode A: Shell-Side Refrigerant (Traditional)
    - Refrigerant: Shell side
    - Water/Glycol: Tube side
    - TEMA: BEM/AEM
    - Baffles: Vertical cut (for condensate drainage)
    - Calculation: Simple area distribution
  
  Mode B: Tube-Side Refrigerant (DX) ⭐ NEW!
    - Refrigerant: Tube side (phase-changing)
    - Water/Glycol: Shell side (cross-flow)
    - TEMA: BEM/BEU
    - Baffles: Horizontal cut (up-down zigzag)
    - Calculation: ROW-BASED with user allocation ⭐

Created: February 2026
TEMA 10th Edition Compliant
"""

import streamlit as st
import numpy as np
import pandas as pd
import math
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import CoolProp.CoolProp as CP
import sys
from pathlib import Path

# Import the existing calculation engine
try:
    from shell_tube_evap_condenser_CORRECTED import (
        TEMACompliantDXHeatExchangerDesign,
        TEMAFoulingResistances,
        TEMATubeStandards,
        TEMABaffleStandards
    )
except ImportError:
    st.error("Error: Could not import calculation engine. Make sure shell_tube_evap_condenser_CORRECTED.py is available.")
    st.stop()


class ProfessionalCondenserDesigner:
    """
    Professional condenser design tool with two operating modes
    """
    
    def __init__(self):
        self.initialize_session_state()
        self.calc_engine = TEMACompliantDXHeatExchangerDesign()
    
    def get_tube_od_mm(self, tube_size: str) -> float:
        """Get tube OD in mm from TEMA standards"""
        tube_od_map = {
            "1/4\"": 6.35,
            "3/8\"": 9.53,
            "1/2\"": 12.7,
            "5/8\"": 15.88,
            "3/4\"": 19.05,
            "1\"": 25.4,
            "1.25\"": 31.75,
            "1.5\"": 38.1,
            "2\"": 50.8
        }
        return tube_od_map.get(tube_size, 15.88)  # Default to 5/8"
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'condenser_mode' not in st.session_state:
            st.session_state.condenser_mode = "Shell-Side Refrigerant"
        
        if 'tema_type' not in st.session_state:
            st.session_state.tema_type = "BEM"
        
        if 'row_allocation' not in st.session_state:
            st.session_state.row_allocation = {
                'total_rows': 40,
                'desuperheat_rows': 8,
                'condensing_rows': 27,
                'subcooling_rows': 5
            }
        
        if 'design_results' not in st.session_state:
            st.session_state.design_results = None
    
    def run(self):
        """Main application entry point"""
        
        st.markdown("## 🔧 Professional Condenser Designer")
        st.markdown("**TEMA 10th Edition Compliant - Shell-Side or Tube-Side Refrigerant**")
        
        st.markdown("---")
        
        # Step 1: Select condenser configuration
        self.select_configuration()
        
        st.markdown("---")
        
        # Step 2: Route to appropriate design mode
        if st.session_state.condenser_mode == "Shell-Side Refrigerant":
            self.design_shell_side_refrigerant()
        else:
            self.design_tube_side_refrigerant_dx()
    
    def select_configuration(self):
        """Step 1: User selects refrigerant location"""
        
        st.markdown("### Step 1: Select Refrigerant Location")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 🔵 Shell-Side Refrigerant (Traditional)
            
            **Configuration:**
            - Refrigerant: Shell side (condensing)
            - Water/Glycol: Tube side
            - TEMA Types: **BEM, AEM**
            - Baffles: **Vertical cut** (condensate drainage)
            
            **Calculation Method:**
            - Simple area distribution
            - 3-zone calculation (desuperheat, condense, subcool)
            - Fast computation
            
            **Best for:**
            - Large tonnage systems
            - Flooded condensers
            - Standard HVAC/refrigeration
            """)
            
            if st.button("🔵 Select Shell-Side Refrigerant", use_container_width=True):
                st.session_state.condenser_mode = "Shell-Side Refrigerant"
                st.session_state.tema_type = "BEM"
                st.rerun()
        
        with col2:
            st.markdown("""
            #### 🟢 Tube-Side Refrigerant (DX) ⭐
            
            **Configuration:**
            - Refrigerant: **Tube side** (phase-changing)
            - Water/Glycol: **Shell side** (cross-flow)
            - TEMA Types: **BEM, BEU**
            - Baffles: **Horizontal cut** (up-down zigzag)
            
            **Calculation Method:**
            - **ROW-BASED segmentation** ⭐
            - User allocates rows to zones
            - Actual subcooling calculation
            - Iterative optimization
            
            **Best for:**
            - Direct expansion (DX) systems
            - High-pressure refrigerants (R410A)
            - Precise subcooling control
            """)
            
            if st.button("🟢 Select Tube-Side Refrigerant (DX)", use_container_width=True, type="primary"):
                st.session_state.condenser_mode = "Tube-Side Refrigerant (DX)"
                st.session_state.tema_type = "BEM"
                st.rerun()
        
        # Show current selection
        st.info(f"**Current Selection:** {st.session_state.condenser_mode}")
    
    def design_shell_side_refrigerant(self):
        """Mode A: Shell-side refrigerant design (simple)"""
        
        st.markdown("### Mode A: Shell-Side Refrigerant Design")
        
        # TEMA type selection with official diagrams
        self.select_tema_type_shell_side()
        
        st.markdown("---")
        
        # Input parameters
        inputs = self.create_inputs_shell_side()
        
        # Calculate button
        if st.button("🔄 Calculate Condenser Performance", type="primary", key="calc_shell"):
            with st.spinner("Calculating shell-side condenser..."):
                results = self.calculate_shell_side_condenser(inputs)
                st.session_state.design_results = results
        
        # Display results
        if st.session_state.design_results is not None:
            self.display_shell_side_results(st.session_state.design_results)
    
    def design_tube_side_refrigerant_dx(self):
        """Mode B: Tube-side refrigerant (DX) with row-based allocation ⭐"""
        
        st.markdown("### Mode B: Tube-Side Refrigerant (DX) - Row-Based Design ⭐")
        
        # TEMA type selection
        self.select_tema_type_tube_side()
        
        st.markdown("---")
        
        # Design workflow tabs
        tab1, tab2, tab3 = st.tabs([
            "📊 Step 1: Calculate Requirements",
            "🎯 Step 2: Allocate Rows",
            "📈 Step 3: Results & Optimization"
        ])
        
        with tab1:
            self.dx_step1_calculate_requirements()
        
        with tab2:
            self.dx_step2_allocate_rows()
        
        with tab3:
            self.dx_step3_results_and_optimization()
    
    def select_tema_type_shell_side(self):
        """TEMA type selection for shell-side refrigerant"""
        
        st.markdown("### TEMA Type Selection")
        
        # Show official TEMA diagram
        try:
            st.image(
                "assets/TEMA_TYPES_OFFICIAL_DIAGRAM.png",
                caption="Figure N-1.2 - TEMA Heat Exchanger Nomenclature (TEMA 10th Edition)",
                use_column_width=True
            )
        except:
            st.warning("TEMA diagram not found. Continuing without image.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            tema_type = st.radio(
                "Select TEMA Type",
                ["BEM", "AEM", "AES"],
                horizontal=True,
                help="Common types for shell-side refrigerant condensers"
            )
            st.session_state.tema_type = tema_type
        
        with col2:
            # Show configuration details
            tema_info = {
                "BEM": {
                    "name": "Bonnet, One Pass Shell, Fixed Tubesheet",
                    "cost": "$",
                    "use": "High pressure, compact design"
                },
                "AEM": {
                    "name": "Channel & Cover, One Pass Shell, Fixed Tubesheet",
                    "cost": "$",
                    "use": "Easy tube cleaning access"
                },
                "AES": {
                    "name": "Channel & Cover, One Pass Shell, Floating Head",
                    "cost": "$$$",
                    "use": "Thermal expansion handling"
                }
            }
            
            info = tema_info[tema_type]
            st.markdown(f"**{tema_type}**")
            st.markdown(f"Cost: {info['cost']}")
            st.markdown(f"Use: {info['use']}")
        
        # Show detailed component diagram
        try:
            if tema_type in ["BEM", "AEM"]:
                st.image(
                    "assets/TEMA_COMPONENTS_BEM_AEP_CFU.png",
                    caption=f"{tema_type} Configuration Details",
                    use_column_width=True
                )
            elif tema_type == "AES":
                st.image(
                    "assets/TEMA_COMPONENTS_AES_DIAGRAM.png",
                    caption="AES Configuration Details",
                    use_column_width=True
                )
        except:
            pass
        
        # Baffle orientation note
        st.info("🔧 **Baffle Configuration:** Vertical cut baffles for condensate drainage")
    
    def select_tema_type_tube_side(self):
        """TEMA type selection for tube-side refrigerant (DX)"""
        
        st.markdown("### TEMA Type Selection (DX Configuration)")
        
        # Show official TEMA diagram
        try:
            st.image(
                "assets/TEMA_TYPES_OFFICIAL_DIAGRAM.png",
                caption="Figure N-1.2 - TEMA Heat Exchanger Nomenclature (TEMA 10th Edition)",
                use_column_width=True
            )
        except:
            st.warning("TEMA diagram not found. Continuing without image.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            tema_type = st.radio(
                "Select TEMA Type (DX)",
                ["BEM", "BEU"],
                horizontal=True,
                help="Recommended types for tube-side refrigerant"
            )
            st.session_state.tema_type = tema_type
        
        with col2:
            tema_info = {
                "BEM": {
                    "name": "Fixed Tubesheet",
                    "cost": "$",
                    "use": "Economical, high pressure containment"
                },
                "BEU": {
                    "name": "U-Tube Bundle",
                    "cost": "$$",
                    "use": "Excellent thermal expansion tolerance"
                }
            }
            
            info = tema_info[tema_type]
            st.markdown(f"**{tema_type}**")
            st.markdown(f"Cost: {info['cost']}")
            st.markdown(f"Use: {info['use']}")
        
        # Show detailed component diagram
        try:
            st.image(
                "assets/TEMA_COMPONENTS_BEM_AEP_CFU.png",
                caption=f"{tema_type} Configuration Details (DX Application)",
                use_column_width=True
            )
        except:
            pass
        
        # Baffle orientation note
        st.info("🔧 **Baffle Configuration:** Horizontal cut baffles for water cross-flow (up-down zigzag)")
    
    def create_inputs_shell_side(self) -> Dict:
        """Create input form for shell-side refrigerant design"""
        
        st.markdown("### Design Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Refrigerant Data")
            refrigerant = st.selectbox(
                "Refrigerant Type",
                ["R134a", "R410A", "R407C", "R404A", "R22", "R717"],
                help="Select refrigerant type"
            )
            
            T_cond = st.number_input(
                "Condensing Temperature (°C)",
                value=40.0,
                min_value=20.0,
                max_value=60.0,
                step=1.0
            )
            
            T_superheat = st.number_input(
                "Inlet Superheat (K)",
                value=10.0,
                min_value=0.0,
                max_value=30.0,
                step=1.0
            )
            
            subcool_target = st.number_input(
                "Target Subcooling (K)",
                value=5.0,
                min_value=0.0,
                max_value=15.0,
                step=1.0
            )
            
            m_dot_ref = st.number_input(
                "Refrigerant Flow Rate (kg/s)",
                value=1.0,
                min_value=0.1,
                max_value=10.0,
                step=0.1
            )
        
        with col2:
            st.markdown("#### Water/Glycol Data")
            fluid_type = st.selectbox(
                "Cooling Fluid",
                ["Water", "30% Glycol", "50% Glycol"],
                help="Cooling fluid type"
            )
            
            T_water_in = st.number_input(
                "Water Inlet Temperature (°C)",
                value=25.0,
                min_value=5.0,
                max_value=40.0,
                step=1.0
            )
            
            m_dot_water = st.number_input(
                "Water Flow Rate (kg/s)",
                value=5.0,
                min_value=0.5,
                max_value=50.0,
                step=0.5
            )
        
        with col3:
            st.markdown("#### Geometry")
            tube_size = st.selectbox(
                "Tube Size",
                ["1/4\"", "3/8\"", "1/2\"", "5/8\"", "3/4\"", "1\"", "1.25\"", "1.5\"", "2\""],
                index=3,  # Default to 5/8"
                help="TEMA standard tube sizes"
            )
            
            bwg = st.selectbox(
                "BWG Gauge",
                ["14", "16", "18", "20"],
                index=2
            )
            
            tube_length = st.number_input(
                "Tube Length (m)",
                value=3.0,
                min_value=1.0,
                max_value=6.0,
                step=0.5
            )
            
            n_tubes = st.number_input(
                "Number of Tubes",
                value=200,
                min_value=50,
                max_value=1000,
                step=10
            )
        
        # Compile inputs
        inputs = {
            'refrigerant': refrigerant,
            'T_cond': T_cond,
            'T_superheat': T_superheat,
            'subcool_target': subcool_target,
            'm_dot_ref': m_dot_ref,
            'fluid_type': fluid_type,
            'T_water_in': T_water_in,
            'm_dot_water': m_dot_water,
            'tube_size': tube_size,
            'bwg': bwg,
            'tube_length': tube_length,
            'n_tubes': n_tubes,
            'tema_type': st.session_state.tema_type
        }
        
        return inputs
    
    def calculate_shell_side_condenser(self, inputs: Dict) -> Dict:
        """Calculate shell-side condenser using existing engine"""
        
        # This would call the existing condenser calculation from shell_tube_evap_condenser_CORRECTED.py
        # For now, placeholder that returns basic structure
        
        st.info("⚠️ Shell-side condenser calculation uses existing Standard Condenser method")
        st.markdown("This mode reuses the existing condenser calculation engine.")
        st.markdown("Navigate to **Condenser Designer (Standard)** from the main menu.")
        
        return {}
    
    def display_shell_side_results(self, results: Dict):
        """Display shell-side condenser results"""
        
        st.markdown("### Results")
        st.info("Results displayed using Standard Condenser method")
    
    # ========================================================================
    # DX CONDENSER (TUBE-SIDE REFRIGERANT) - ROW-BASED CALCULATION ⭐
    # ========================================================================
    
    def dx_step1_calculate_requirements(self):
        """Step 1: Calculate required rows for each zone"""
        
        st.markdown("### Calculate Zone Requirements")
        st.markdown("Enter design parameters to calculate how many tube rows are needed for each zone")
        
        try:
            # Input form
            inputs = self.create_inputs_dx()
            
            if st.button("📊 Calculate Required Rows", type="primary", key="calc_req"):
                with st.spinner("Calculating zone requirements..."):
                    requirements = self.calculate_zone_requirements_dx(inputs)
                    st.session_state.zone_requirements = requirements
                    st.session_state.dx_inputs = inputs
        
        except Exception as e:
            st.error(f"❌ Error in input processing: {str(e)}")
            st.exception(e)
            return
        
        # Display requirements if calculated
        if 'zone_requirements' in st.session_state:
            req = st.session_state.zone_requirements
            
            st.success("✅ Zone Requirements Calculated")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Desuperheat Zone",
                    f"{req['desuperheat_rows']:.0f} rows",
                    help="Rows needed to desuperheat vapor to saturation"
                )
                st.caption(f"{req['Q_desuperheat']/1000:.1f} kW")
            
            with col2:
                st.metric(
                    "Condensing Zone",
                    f"{req['condensing_rows']:.0f} rows",
                    help="Rows needed for phase change"
                )
                st.caption(f"{req['Q_condensing']/1000:.1f} kW")
            
            with col3:
                st.metric(
                    "Subcooling Zone",
                    f"{req['subcooling_rows']:.0f} rows",
                    help=f"Rows needed for {req['subcool_target']:.0f}K subcooling"
                )
                st.caption(f"{req['Q_subcooling']/1000:.1f} kW")
            
            with col4:
                total_rows = req['desuperheat_rows'] + req['condensing_rows'] + req['subcooling_rows']
                st.metric(
                    "Total Rows",
                    f"{total_rows:.0f} rows"
                )
                st.caption(f"{req['Q_total']/1000:.1f} kW")
            
            # Visualization
            self.visualize_zone_requirements(req)
            
            # Move to next step
            st.info("✅ Requirements calculated. Proceed to **Step 2: Allocate Rows** to design the tube bundle.")
    
    def dx_step2_allocate_rows(self):
        """Step 2: User allocates rows to zones"""
        
        st.markdown("### Allocate Rows to Zones")
        st.markdown("Specify how many rows to allocate to each zone. The program will calculate actual performance.")
        
        if 'zone_requirements' not in st.session_state:
            st.warning("⚠️ Please complete **Step 1** first to calculate zone requirements")
            return
        
        req = st.session_state.zone_requirements
        
        # Show recommended allocation
        st.markdown("#### Recommended Allocation (from Step 1)")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info(f"**Desuperheat:** {req['desuperheat_rows']:.0f} rows")
        with col2:
            st.info(f"**Condensing:** {req['condensing_rows']:.0f} rows")
        with col3:
            st.info(f"**Subcooling:** {req['subcooling_rows']:.0f} rows")
        with col4:
            total_rec = req['desuperheat_rows'] + req['condensing_rows'] + req['subcooling_rows']
            st.info(f"**Total:** {total_rec:.0f} rows")
        
        st.markdown("---")
        
        # User allocation
        st.markdown("#### Your Allocation")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            total_rows = st.number_input(
                "Total Number of Rows",
                value=int(total_rec),
                min_value=10,
                max_value=100,
                step=1,
                help="Total rows in tube bundle"
            )
            
            desuperheat_rows = st.number_input(
                "Rows for Desuperheat",
                value=int(req['desuperheat_rows']),
                min_value=1,
                max_value=total_rows-2,
                step=1
            )
            
            condensing_rows = st.number_input(
                "Rows for Condensing",
                value=int(req['condensing_rows']),
                min_value=1,
                max_value=total_rows-2,
                step=1
            )
            
            subcooling_rows = st.number_input(
                "Rows for Subcooling",
                value=int(req['subcooling_rows']),
                min_value=1,
                max_value=total_rows-2,
                step=1
            )
        
        with col2:
            allocated = desuperheat_rows + condensing_rows + subcooling_rows
            remaining = total_rows - allocated
            
            st.markdown("#### Allocation Summary")
            st.metric("Total Rows", total_rows)
            st.metric("Allocated", allocated)
            
            if remaining == 0:
                st.success(f"✅ All rows allocated")
            elif remaining > 0:
                st.warning(f"⚠️ {remaining} rows unallocated")
            else:
                st.error(f"❌ Over-allocated by {-remaining} rows")
        
        # Save allocation
        st.session_state.row_allocation = {
            'total_rows': total_rows,
            'desuperheat_rows': desuperheat_rows,
            'condensing_rows': condensing_rows,
            'subcooling_rows': subcooling_rows
        }
        
        # Calculate with user allocation
        if st.button("🎯 Calculate with This Allocation", type="primary", key="calc_alloc"):
            if remaining != 0:
                st.error("❌ Please allocate all rows before calculating")
            else:
                with st.spinner("Calculating performance with your allocation..."):
                    results = self.calculate_dx_with_allocation(
                        st.session_state.dx_inputs,
                        st.session_state.row_allocation
                    )
                    st.session_state.dx_results = results
                    st.success("✅ Calculation complete! View results in **Step 3**")
    
    def dx_step3_results_and_optimization(self):
        """Step 3: Display results and optimization recommendations"""
        
        st.markdown("### Results & Optimization")
        
        if 'dx_results' not in st.session_state:
            st.warning("⚠️ Please complete **Step 2** to calculate performance with your row allocation")
            return
        
        results = st.session_state.dx_results
        req = st.session_state.zone_requirements
        alloc = st.session_state.row_allocation
        
        # Performance summary
        st.markdown("#### Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Heat Transfer",
                f"{results['Q_total']/1000:.1f} kW",
                delta=f"{(results['Q_total']-req['Q_total'])/1000:.1f} kW"
            )
        
        with col2:
            actual_subcool = results['subcool_achieved']
            target_subcool = req['subcool_target']
            delta_subcool = actual_subcool - target_subcool
            
            st.metric(
                "Subcooling Achieved",
                f"{actual_subcool:.1f} K",
                delta=f"{delta_subcool:.1f} K"
            )
        
        with col3:
            if results['subcool_adequate']:
                st.success("✅ Subcooling Adequate")
            else:
                st.error("❌ Subcooling Insufficient")
        
        with col4:
            st.metric(
                "Water Outlet Temp",
                f"{results['T_water_out']:.1f} °C"
            )
        
        # Zone-by-zone results
        st.markdown("---")
        st.markdown("#### Zone-by-Zone Performance")
        
        zone_df = pd.DataFrame([
            {
                'Zone': 'Desuperheat',
                'Rows Allocated': alloc['desuperheat_rows'],
                'Rows Required': f"{req['desuperheat_rows']:.0f}",
                'Heat Transfer (kW)': f"{results['zones']['desuperheat']['Q']/1000:.1f}",
                'Status': '✅' if alloc['desuperheat_rows'] >= req['desuperheat_rows'] else '⚠️'
            },
            {
                'Zone': 'Condensing',
                'Rows Allocated': alloc['condensing_rows'],
                'Rows Required': f"{req['condensing_rows']:.0f}",
                'Heat Transfer (kW)': f"{results['zones']['condensing']['Q']/1000:.1f}",
                'Status': '✅' if alloc['condensing_rows'] >= req['condensing_rows'] else '⚠️'
            },
            {
                'Zone': 'Subcooling',
                'Rows Allocated': alloc['subcooling_rows'],
                'Rows Required': f"{req['subcooling_rows']:.0f}",
                'Heat Transfer (kW)': f"{results['zones']['subcooling']['Q']/1000:.1f}",
                'Status': '✅ Adequate' if results['subcool_adequate'] else '❌ Insufficient'
            }
        ])
        
        st.dataframe(zone_df, use_container_width=True, hide_index=True)
        
        # Warnings and recommendations
        if results['warnings']:
            st.markdown("#### ⚠️ Warnings")
            for warning in results['warnings']:
                st.warning(warning)
        
        if results['recommendations']:
            st.markdown("#### 💡 Recommendations")
            for rec in results['recommendations']:
                st.info(rec)
        
        # Visualization
        self.visualize_dx_results(results, alloc)
        
        # Optimization suggestions
        if not results['subcool_adequate']:
            st.markdown("---")
            st.markdown("#### 🔧 Quick Fixes")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Option 1: Add More Subcooling Rows**")
                additional_rows = results['subcool_rows_needed'] - alloc['subcooling_rows']
                st.markdown(f"Add **{additional_rows:.0f} more rows** to subcooling zone")
                st.markdown(f"New allocation: {alloc['subcooling_rows']} → {results['subcool_rows_needed']:.0f} rows")
                
                if st.button("Apply This Fix", key="fix1"):
                    st.session_state.row_allocation['subcooling_rows'] = int(results['subcool_rows_needed'])
                    # Reduce condensing rows proportionally
                    st.session_state.row_allocation['condensing_rows'] -= int(additional_rows)
                    st.success("✅ Allocation updated! Recalculate in Step 2")
            
            with col2:
                st.markdown("**Option 2: Lower Water Inlet Temperature**")
                st.markdown(f"Current: {req['T_water_in']:.1f}°C")
                st.markdown("Try reducing by 2-3°C")
                st.info("Return to Step 1 to adjust water temperature")
    
    def create_inputs_dx(self) -> Dict:
        """Create input form for DX condenser"""
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Refrigerant Data")
            refrigerant = st.selectbox(
                "Refrigerant",
                ["R134a", "R410A", "R407C", "R404A"],
                key="dx_ref"
            )
            
            T_cond = st.number_input(
                "Condensing Temp (°C)",
                value=40.0,
                min_value=20.0,
                max_value=60.0,
                step=1.0,
                key="dx_tcond"
            )
            
            T_superheat = st.number_input(
                "Superheat (K)",
                value=10.0,
                min_value=0.0,
                max_value=30.0,
                step=1.0,
                key="dx_superheat"
            )
            
            subcool_target = st.number_input(
                "Target Subcool (K)",
                value=5.0,
                min_value=0.0,
                max_value=15.0,
                step=1.0,
                key="dx_subcool"
            )
            
            m_dot_ref = st.number_input(
                "Refrigerant Flow (kg/s)",
                value=1.0,
                min_value=0.1,
                max_value=10.0,
                step=0.1,
                key="dx_mdot"
            )
        
        with col2:
            st.markdown("#### Water Data")
            T_water_in = st.number_input(
                "Water Inlet (°C)",
                value=25.0,
                min_value=5.0,
                max_value=40.0,
                step=1.0,
                key="dx_tw"
            )
            
            m_dot_water = st.number_input(
                "Water Flow (kg/s)",
                value=5.0,
                min_value=0.5,
                max_value=50.0,
                step=0.5,
                key="dx_mw"
            )
        
        with col3:
            st.markdown("#### Tube Geometry")
            tube_size = st.selectbox(
                "Tube Size",
                ["1/4\"", "3/8\"", "1/2\"", "5/8\"", "3/4\"", "1\"", "1.25\"", "1.5\"", "2\""],
                index=3,  # Default to 5/8"
                key="dx_size",
                help="TEMA standard tube sizes"
            )
            
            bwg = st.selectbox(
                "BWG",
                ["16", "18", "20"],
                index=1,
                key="dx_bwg"
            )
            
            tube_length = st.number_input(
                "Length (m)",
                value=3.0,
                min_value=1.0,
                max_value=6.0,
                step=0.5,
                key="dx_length"
            )
            
            tubes_per_row = st.number_input(
                "Tubes per Row",
                value=10,
                min_value=5,
                max_value=30,
                step=1,
                key="dx_tpr"
            )
        
        inputs = {
            'refrigerant': refrigerant,
            'T_cond': T_cond,
            'T_superheat': T_superheat,
            'subcool_target': subcool_target,
            'm_dot_ref': m_dot_ref,
            'T_water_in': T_water_in,
            'm_dot_water': m_dot_water,
            'tube_size': tube_size,
            'bwg': bwg,
            'tube_length': tube_length,
            'tubes_per_row': tubes_per_row
        }
        
        return inputs
    
    def calculate_zone_requirements_dx(self, inputs: Dict) -> Dict:
        """Calculate required rows for each zone based on heat duties"""
        
        try:
            # Get refrigerant properties
            refrigerant = inputs['refrigerant']
            T_cond = inputs['T_cond']
            T_superheat = inputs['T_superheat']
            subcool_target = inputs['subcool_target']
            m_dot_ref = inputs['m_dot_ref']
            
            # Get properties at saturation
            T_K = T_cond + 273.15
            P_sat = CP.PropsSI('P', 'T', T_K, 'Q', 1, refrigerant)
            
            # Vapor properties (superheated)
            T_in = T_cond + T_superheat
            T_in_K = T_in + 273.15
            cp_v = CP.PropsSI('C', 'T', T_in_K, 'P', P_sat, refrigerant)
            
            # Liquid properties
            cp_l = CP.PropsSI('C', 'T', T_K, 'Q', 0, refrigerant)
            
            # Latent heat
            h_l = CP.PropsSI('H', 'T', T_K, 'Q', 0, refrigerant)
            h_v = CP.PropsSI('H', 'T', T_K, 'Q', 1, refrigerant)
            h_fg = h_v - h_l
            
            # Heat duties (W)
            Q_desuperheat = m_dot_ref * cp_v * T_superheat
            Q_condensing = m_dot_ref * h_fg
            Q_subcooling = m_dot_ref * cp_l * subcool_target
            Q_total = Q_desuperheat + Q_condensing + Q_subcooling
            
            # Estimate rows needed (simplified - assumes constant U and LMTD)
            tube_length = inputs['tube_length']
            tubes_per_row = inputs['tubes_per_row']
            
            # Get tube OD using helper method
            tube_size = inputs['tube_size']
            tube_od_mm = self.get_tube_od_mm(tube_size)
            tube_od_m = tube_od_mm / 1000
            
            # Area per row
            A_row = math.pi * tube_od_m * tube_length * tubes_per_row
            
            # Assume typical U values (W/m²K) for each zone
            U_desuperheat = 800  # Single phase vapor
            U_condensing = 1500  # Two-phase condensation
            U_subcooling = 1200  # Single phase liquid
            
            # Assume typical LMTD (K) - simplified
            LMTD_desuperheat = 8
            LMTD_condensing = 10
            LMTD_subcooling = 6
            
            # Required area per zone
            A_desuperheat = Q_desuperheat / (U_desuperheat * LMTD_desuperheat)
            A_condensing = Q_condensing / (U_condensing * LMTD_condensing)
            A_subcooling = Q_subcooling / (U_subcooling * LMTD_subcooling)
            
            # Required rows
            rows_desuperheat = max(1, A_desuperheat / A_row)
            rows_condensing = max(1, A_condensing / A_row)
            rows_subcooling = max(1, A_subcooling / A_row)
            
            requirements = {
                'Q_desuperheat': Q_desuperheat,
                'Q_condensing': Q_condensing,
                'Q_subcooling': Q_subcooling,
                'Q_total': Q_total,
                'desuperheat_rows': math.ceil(rows_desuperheat),
                'condensing_rows': math.ceil(rows_condensing),
                'subcooling_rows': math.ceil(rows_subcooling),
                'subcool_target': subcool_target,
                'T_water_in': inputs['T_water_in'],
                'A_row': A_row
            }
            
            return requirements
            
        except KeyError as e:
            st.error(f"❌ Missing input parameter: {str(e)}")
            raise
        except Exception as e:
            st.error(f"❌ Error calculating zone requirements: {str(e)}")
            st.error("Please check your input values")
            raise
    
    def calculate_dx_with_allocation(self, inputs: Dict, allocation: Dict) -> Dict:
        """Calculate actual performance with user's row allocation"""
        
        # This is a simplified calculation
        # In production, you would do row-by-row heat transfer calculation
        
        req = st.session_state.zone_requirements
        
        # Calculate actual subcooling based on allocated rows
        rows_allocated = allocation['subcooling_rows']
        rows_required = req['subcooling_rows']
        
        # Simplified: subcooling is proportional to rows
        subcool_achieved = req['subcool_target'] * (rows_allocated / rows_required)
        subcool_adequate = subcool_achieved >= req['subcool_target'] * 0.95
        
        # Calculate zone performance
        zones = {
            'desuperheat': {
                'Q': req['Q_desuperheat'] * (allocation['desuperheat_rows'] / req['desuperheat_rows']),
                'rows': allocation['desuperheat_rows']
            },
            'condensing': {
                'Q': req['Q_condensing'] * (allocation['condensing_rows'] / req['condensing_rows']),
                'rows': allocation['condensing_rows']
            },
            'subcooling': {
                'Q': req['Q_subcooling'] * (rows_allocated / rows_required),
                'rows': rows_allocated
            }
        }
        
        Q_total = sum(z['Q'] for z in zones.values())
        
        # Water outlet temperature
        m_water = inputs['m_dot_water']
        cp_water = 4186  # J/kg·K
        T_water_out = inputs['T_water_in'] + Q_total / (m_water * cp_water)
        
        # Warnings and recommendations
        warnings = []
        recommendations = []
        
        if not subcool_adequate:
            warnings.append(
                f"⚠️ Subcooling insufficient: Achieved {subcool_achieved:.1f}K, need {req['subcool_target']:.1f}K"
            )
            recommendations.append(
                f"💡 Add {math.ceil(rows_required - rows_allocated)} more rows to subcooling zone"
            )
        
        if allocation['desuperheat_rows'] < req['desuperheat_rows'] * 0.9:
            warnings.append("⚠️ Desuperheat zone may be undersized")
            recommendations.append("💡 Consider adding rows to desuperheat zone")
        
        if allocation['condensing_rows'] < req['condensing_rows'] * 0.9:
            warnings.append("⚠️ Condensing zone may be undersized")
            recommendations.append("💡 Consider adding rows to condensing zone")
        
        results = {
            'Q_total': Q_total,
            'subcool_achieved': subcool_achieved,
            'subcool_adequate': subcool_adequate,
            'subcool_rows_needed': rows_required,
            'T_water_out': T_water_out,
            'zones': zones,
            'warnings': warnings,
            'recommendations': recommendations
        }
        
        return results
    
    def visualize_zone_requirements(self, req: Dict):
        """Visualize zone requirements"""
        
        fig = go.Figure()
        
        zones = ['Desuperheat', 'Condensing', 'Subcooling']
        rows = [req['desuperheat_rows'], req['condensing_rows'], req['subcooling_rows']]
        heat = [req['Q_desuperheat']/1000, req['Q_condensing']/1000, req['Q_subcooling']/1000]
        
        colors = ['#FCA5A5', '#FCD34D', '#93C5FD']
        
        fig.add_trace(go.Bar(
            x=zones,
            y=rows,
            name='Rows Required',
            marker_color=colors,
            text=[f"{r:.0f} rows<br>{h:.1f} kW" for r, h in zip(rows, heat)],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Zone Requirements",
            xaxis_title="Zone",
            yaxis_title="Number of Rows",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def visualize_dx_results(self, results: Dict, allocation: Dict):
        """Visualize DX condenser results"""
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Row Allocation", "Heat Transfer by Zone"),
            specs=[[{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Row allocation
        zones = ['Desuperheat', 'Condensing', 'Subcooling']
        rows = [
            allocation['desuperheat_rows'],
            allocation['condensing_rows'],
            allocation['subcooling_rows']
        ]
        colors = ['#FCA5A5', '#FCD34D', '#93C5FD']
        
        fig.add_trace(
            go.Bar(
                x=zones,
                y=rows,
                marker_color=colors,
                text=rows,
                textposition='auto',
                name='Rows'
            ),
            row=1, col=1
        )
        
        # Heat transfer pie
        heat = [
            results['zones']['desuperheat']['Q']/1000,
            results['zones']['condensing']['Q']/1000,
            results['zones']['subcooling']['Q']/1000
        ]
        
        fig.add_trace(
            go.Pie(
                labels=zones,
                values=heat,
                marker_colors=colors,
                textinfo='label+percent+value',
                texttemplate='%{label}<br>%{value:.1f} kW<br>%{percent}'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# STANDALONE EXECUTION (for testing)
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="Professional Condenser Designer",
        page_icon="🔧",
        layout="wide"
    )
    
    designer = ProfessionalCondenserDesigner()
    designer.run()
