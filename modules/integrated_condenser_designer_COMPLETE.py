"""
COMPLETE INTEGRATED CONDENSER DESIGNER
Full implementation with interactive TEMA drawings, tube sheet designer, and segment model

This is the MASTER MODULE that integrates:
1. TEMA general arrangement drawings
2. Interactive water inlet/outlet selection
3. Interactive tube zone assignment
4. Segment-by-segment calculation
5. Subcool area analysis and recommendations
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import math
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class IntegratedCondenserDesigner:
    """
    Complete condenser design tool with visual interface
    """
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        
        if 'design_step' not in st.session_state:
            st.session_state.design_step = 1
        
        if 'tema_type' not in st.session_state:
            st.session_state.tema_type = "AES"
        
        if 'enable_zoned' not in st.session_state:
            st.session_state.enable_zoned = False
        
        if 'tube_sheet' not in st.session_state:
            st.session_state.tube_sheet = None
        
        if 'tube_zones' not in st.session_state:
            st.session_state.tube_zones = None
        
        if 'water_inlet_pos' not in st.session_state:
            st.session_state.water_inlet_pos = None
        
        if 'water_outlet_pos' not in st.session_state:
            st.session_state.water_outlet_pos = None
        
        if 'segment_results' not in st.session_state:
            st.session_state.segment_results = None
    
    def run(self):
        """Main application flow"""
        
        st.title("🌡️ Advanced Condenser Designer - TEMA 10th Edition")
        st.markdown("**Complete segment-by-segment design with interactive visualization**")
        
        # Progress indicator
        self.show_progress_bar()
        
        # Design wizard steps
        if st.session_state.design_step == 1:
            self.step1_basic_inputs()
        
        elif st.session_state.design_step == 2:
            self.step2_tema_selection()
        
        elif st.session_state.design_step == 3:
            self.step3_water_flow_path()
        
        elif st.session_state.design_step == 4:
            self.step4_tube_zone_assignment()
        
        elif st.session_state.design_step == 5:
            self.step5_segment_calculation()
        
        elif st.session_state.design_step == 6:
            self.step6_results_and_recommendations()
    
    def show_progress_bar(self):
        """Show design progress"""
        
        steps = [
            "Basic Inputs",
            "TEMA Selection",
            "Water Flow Path",
            "Zone Assignment",
            "Calculate",
            "Results"
        ]
        
        cols = st.columns(6)
        
        for i, (col, step_name) in enumerate(zip(cols, steps), 1):
            with col:
                if i < st.session_state.design_step:
                    st.success(f"✅ {step_name}")
                elif i == st.session_state.design_step:
                    st.info(f"▶️ {step_name}")
                else:
                    st.text(f"⭕ {step_name}")
    
    # ========================================================================
    # STEP 1: BASIC INPUTS
    # ========================================================================
    
    def step1_basic_inputs(self):
        """Collect basic design parameters"""
        
        st.markdown("## Step 1: Basic Design Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Refrigerant Side")
            
            refrigerant = st.selectbox(
                "Refrigerant",
                ["R134a", "R410A", "R407C", "R404A", "R32", "R1234yf", "R717 (Ammonia)"]
            )
            
            m_dot_ref = st.number_input(
                "Mass Flow Rate (kg/s)",
                min_value=0.01, max_value=10.0, value=0.221, step=0.01
            )
            
            T_ref_in = st.number_input(
                "Inlet Temperature (superheated) [°C]",
                min_value=20.0, max_value=150.0, value=95.0, step=1.0
            )
            
            T_cond = st.number_input(
                "Condensing Temperature [°C]",
                min_value=20.0, max_value=100.0, value=45.0, step=1.0
            )
            
            subcool_req = st.number_input(
                "Required Subcooling [K]",
                min_value=0.0, max_value=20.0, value=5.0, step=0.5
            )
        
        with col2:
            st.markdown("### Water/Glycol Side")
            
            glycol_type = st.selectbox("Glycol Type", ["None (Water)", "Ethylene", "Propylene"])
            
            if glycol_type == "None (Water)":
                glycol_percent = 0.0
            else:
                glycol_percent = st.slider("Glycol Concentration (%)", 0, 60, 30)
            
            m_dot_water_lph = st.number_input(
                "Water Flow Rate (L/hr)",
                min_value=100, max_value=100000, value=24851, step=100
            )
            
            T_water_in = st.number_input(
                "Water Inlet Temperature [°C]",
                min_value=5.0, max_value=50.0, value=35.0, step=1.0
            )
        
        st.markdown("### Heat Exchanger Geometry")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            n_tubes = st.number_input("Number of Tubes", 100, 500, 200, 10)
            tube_length = st.number_input("Tube Length (m)", 0.5, 3.0, 1.0, 0.1)
        
        with col2:
            tube_size = st.selectbox("Tube Size", ["1/4\"", "3/8\"", "1/2\"", "5/8\"", "3/4\"", "1\""])
            bwg = st.selectbox("BWG Gauge", ["16", "18", "20", "22"])
        
        with col3:
            n_passes = st.selectbox("Number of Passes", [1, 2, 4, 6, 8])
            tube_layout = st.selectbox("Tube Layout", ["Triangular", "Square"])
        
        st.markdown("### Advanced Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_zoned = st.checkbox(
                "Enable Zoned Condenser (Integral Subcooler)",
                value=False,
                help="Allows separate tube zones for desuperheat, condensation, and subcooling"
            )
            st.session_state.enable_zoned = enable_zoned
        
        with col2:
            n_segments = st.slider(
                "Number of Calculation Segments",
                min_value=10, max_value=50, value=20,
                help="More segments = more accurate but slower calculation"
            )
        
        # Store inputs in session state
        st.session_state.inputs = {
            'refrigerant': refrigerant,
            'm_dot_ref': m_dot_ref,
            'T_ref_in_superheated': T_ref_in,
            'T_cond': T_cond,
            'subcool_req': subcool_req,
            'glycol_type': glycol_type.lower().replace(" (water)", "").replace("none", "water"),
            'glycol_percent': glycol_percent,
            'm_dot_water_lph': m_dot_water_lph,
            'T_water_in': T_water_in,
            'n_tubes': n_tubes,
            'tube_length': tube_length,
            'tube_size': tube_size,
            'bwg': bwg,
            'n_passes': n_passes,
            'tube_layout': tube_layout.lower(),
            'n_segments': n_segments
        }
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col3:
            if st.button("Next: Select TEMA Type →", type="primary"):
                st.session_state.design_step = 2
                st.rerun()
    
    # ========================================================================
    # STEP 2: TEMA SELECTION WITH VISUAL DRAWINGS
    # ========================================================================
    
    def step2_tema_selection(self):
        """Select TEMA type with visual drawings"""
        
        st.markdown("## Step 2: Select TEMA Type")
        
        st.info(
            "💡 **Tip:** For zoned condenser with integral subcooler, "
            "select a '-Z' type (AES-Z or AEL-Z) for best performance."
        )
        
        # TEMA type selection
        tema_types = list(TEMAArrangementDrawings.TEMA_TYPES.keys())
        
        # Highlight zoned types if zoned design enabled
        if st.session_state.enable_zoned:
            recommended_types = [t for t in tema_types if '-Z' in t]
            other_types = [t for t in tema_types if '-Z' not in t]
            
            st.markdown("### 🎯 Recommended for Zoned Design:")
            tema_type_rec = st.radio(
                "Select TEMA Type (Recommended)",
                recommended_types,
                format_func=lambda x: f"{x} - {TEMAArrangementDrawings.TEMA_TYPES[x]['description']}"
            )
            
            with st.expander("Show Other TEMA Types"):
                tema_type_other = st.radio(
                    "Other TEMA Types",
                    other_types,
                    format_func=lambda x: f"{x} - {TEMAArrangementDrawings.TEMA_TYPES[x]['description']}"
                )
                if st.button("Use This Type Instead"):
                    tema_type = tema_type_other
                else:
                    tema_type = tema_type_rec
            
            tema_type = tema_type_rec
        
        else:
            tema_type = st.selectbox(
                "Select TEMA Type",
                tema_types,
                format_func=lambda x: f"{x} - {TEMAArrangementDrawings.TEMA_TYPES[x]['description']}"
            )
        
        st.session_state.tema_type = tema_type
        
        # Show TEMA general arrangement drawing
        st.markdown("### 📐 TEMA General Arrangement")
        
        fig = TEMAArrangementDrawings.draw_tema_arrangement(tema_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show description
        config = TEMAArrangementDrawings.TEMA_TYPES[tema_type]
        
        st.markdown("### 📋 Configuration Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Front Head:** {config['front_head']}")
            st.markdown(f"**Shell Type:** {config['shell']}")
            st.markdown(f"**Rear Head:** {config['rear_head']}")
        
        with col2:
            st.markdown(f"**Description:** {config['description']}")
            st.markdown(f"**Typical Use:** {config['typical_use']}")
        
        # Special notes for zoned designs
        if '-Z' in tema_type:
            st.success(
                "✅ This TEMA type includes **zone partitions** in the shell, "
                "allowing separate water flow to different tube zones. "
                "This is ideal for achieving better subcooling control."
            )
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Back"):
                st.session_state.design_step = 1
                st.rerun()
        
        with col3:
            if st.button("Next: Water Flow Path →", type="primary"):
                st.session_state.design_step = 3
                st.rerun()
    
    # ========================================================================
    # STEP 3: WATER FLOW PATH (INTERACTIVE CLICKING)
    # ========================================================================
    
    def step3_water_flow_path(self):
        """Interactive selection of water inlet/outlet positions"""
        
        st.markdown("## Step 3: Define Water Flow Path")
        
        st.info(
            "Click on the shell diagram to mark water **INLET** and **OUTLET** positions. "
            "This determines the flow pattern and affects zone calculations."
        )
        
        # Create interactive shell diagram
        fig = self.create_clickable_shell_diagram()
        
        # Display current selections
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.water_inlet_pos:
                st.success(f"✅ Water Inlet: {st.session_state.water_inlet_pos['label']}")
            else:
                st.warning("⚠️ Click to mark Water Inlet")
        
        with col2:
            if st.session_state.water_outlet_pos:
                st.success(f"✅ Water Outlet: {st.session_state.water_outlet_pos['label']}")
            else:
                st.warning("⚠️ Click to mark Water Outlet")
        
        # Show diagram with plotly clickable
        st.plotly_chart(fig, use_container_width=True)
        
        # Preset configurations
        st.markdown("### 🎯 Or Use Preset Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Bottom In / Top Out (Counterflow)"):
                st.session_state.water_inlet_pos = {'x': 5, 'y': 0.5, 'label': 'Bottom'}
                st.session_state.water_outlet_pos = {'x': 5, 'y': 2.5, 'label': 'Top'}
                st.rerun()
        
        with col2:
            if st.button("Side In / Side Out (Cross-flow)"):
                st.session_state.water_inlet_pos = {'x': 1, 'y': 1.5, 'label': 'Left Side'}
                st.session_state.water_outlet_pos = {'x': 9, 'y': 1.5, 'label': 'Right Side'}
                st.rerun()
        
        with col3:
            if st.button("Top In / Bottom Out (Co-flow)"):
                st.session_state.water_inlet_pos = {'x': 5, 'y': 2.5, 'label': 'Top'}
                st.session_state.water_outlet_pos = {'x': 5, 'y': 0.5, 'label': 'Bottom'}
                st.rerun()
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Back"):
                st.session_state.design_step = 2
                st.rerun()
        
        with col3:
            can_proceed = (st.session_state.water_inlet_pos is not None and 
                          st.session_state.water_outlet_pos is not None)
            
            if can_proceed:
                if st.button("Next: Tube Zone Assignment →", type="primary"):
                    st.session_state.design_step = 4
                    st.rerun()
            else:
                st.button("Next: Tube Zone Assignment →", disabled=True)
                st.caption("⚠️ Please mark both inlet and outlet positions first")
    
    def create_clickable_shell_diagram(self) -> go.Figure:
        """Create interactive shell diagram for clicking inlet/outlet"""
        
        fig = go.Figure()
        
        # Draw shell
        fig.add_shape(
            type="rect",
            x0=1, y0=0.5, x1=9, y1=2.5,
            line=dict(color="black", width=3),
            fillcolor="lightblue",
            opacity=0.2
        )
        
        # Draw tubesheets
        fig.add_shape(type="line", x0=1, y0=0.5, x1=1, y1=2.5, 
                     line=dict(color="black", width=5))
        fig.add_shape(type="line", x0=9, y0=0.5, x1=9, y1=2.5,
                     line=dict(color="black", width=5))
        
        # Show current selections
        if st.session_state.water_inlet_pos:
            pos = st.session_state.water_inlet_pos
            fig.add_trace(go.Scatter(
                x=[pos['x']], y=[pos['y']],
                mode='markers+text',
                marker=dict(size=20, color='blue', symbol='arrow-up'),
                text=['WATER IN'],
                textposition='top center',
                name='Water Inlet',
                showlegend=False
            ))
        
        if st.session_state.water_outlet_pos:
            pos = st.session_state.water_outlet_pos
            fig.add_trace(go.Scatter(
                x=[pos['x']], y=[pos['y']],
                mode='markers+text',
                marker=dict(size=20, color='red', symbol='arrow-down'),
                text=['WATER OUT'],
                textposition='bottom center',
                name='Water Outlet',
                showlegend=False
            ))
        
        # Clickable points grid
        x_points = [1, 3, 5, 7, 9]
        y_points = [0.5, 1.0, 1.5, 2.0, 2.5]
        
        for x in x_points:
            for y in y_points:
                fig.add_trace(go.Scatter(
                    x=[x], y=[y],
                    mode='markers',
                    marker=dict(size=10, color='gray', opacity=0.3),
                    hoverinfo='text',
                    text=[f"Click to place nozzle at ({x:.1f}, {y:.1f})"],
                    showlegend=False
                ))
        
        fig.update_layout(
            title="Click to Mark Water Inlet (Blue) and Outlet (Red)",
            xaxis=dict(range=[0, 10], showgrid=False, zeroline=False),
            yaxis=dict(range=[0, 3], showgrid=False, zeroline=False),
            height=300,
            plot_bgcolor='white'
        )
        
        return fig
    
    # ========================================================================
    # STEP 4: TUBE ZONE ASSIGNMENT (INTERACTIVE TUBE SHEET)
    # ========================================================================
    
    def step4_tube_zone_assignment(self):
        """Interactive tube zone assignment on tube sheet"""
        
        st.markdown("## Step 4: Assign Tube Zones")
        
        if st.session_state.enable_zoned:
            st.info(
                "🎨 **Zoned Design Enabled:** Assign tubes to different zones "
                "(Desuperheat, Condensation, Subcooling). Each zone can have "
                "dedicated tubes for better performance control."
            )
        else:
            st.info(
                "ℹ️ **Standard Design:** All tubes will be used for all zones "
                "sequentially along the tube length. You can still visualize the tube layout."
            )
        
        # Initialize tube sheet if not exists
        if st.session_state.tube_sheet is None:
            from interactive_tube_sheet_designer import InteractiveTubeSheet
            
            inputs = st.session_state.inputs
            tube_pitch = 15.0  # mm (can be calculated from tube size)
            
            st.session_state.tube_sheet = InteractiveTubeSheet(
                n_tubes=inputs['n_tubes'],
                tube_layout=inputs['tube_layout'],
                tube_pitch=tube_pitch
            )
        
        tube_sheet = st.session_state.tube_sheet
        
        # Zone assignment interface (only if zoned design)
        if st.session_state.enable_zoned:
            
            st.markdown("### 🎯 Zone Assignment Methods")
            
            tab1, tab2, tab3 = st.tabs([
                "By Rows (Simple)",
                "By Position (Rectangular)",
                "By Percentage (Auto)"
            ])
            
            with tab1:
                st.markdown("**Assign zones by row ranges**")
                st.caption("Tip: Top rows for desuperheat, middle for condense, bottom for subcool")
                
                # Estimate number of rows
                n_rows = int(np.ceil(np.sqrt(inputs['n_tubes'])))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Desuperheat Zone** (Hottest)")
                    desup_rows = st.slider(
                        "Row Range",
                        0, n_rows, (0, n_rows//5),
                        key="desup_rows"
                    )
                    if st.button("✅ Assign Desuperheat", key="btn_desup"):
                        tube_sheet.assign_zone_by_rows("desuperheat", desup_rows[0], desup_rows[1])
                        st.success("Assigned!")
                
                with col2:
                    st.markdown("**Condensation Zone** (Main)")
                    cond_rows = st.slider(
                        "Row Range",
                        0, n_rows, (n_rows//5, n_rows*4//5),
                        key="cond_rows"
                    )
                    if st.button("✅ Assign Condensation", key="btn_cond"):
                        tube_sheet.assign_zone_by_rows("condense", cond_rows[0], cond_rows[1])
                        st.success("Assigned!")
                
                with col3:
                    st.markdown("**Subcool Zone** (Coldest)")
                    sub_rows = st.slider(
                        "Row Range",
                        0, n_rows, (n_rows*4//5, n_rows),
                        key="sub_rows"
                    )
                    if st.button("✅ Assign Subcool", key="btn_sub"):
                        tube_sheet.assign_zone_by_rows("subcool", sub_rows[0], sub_rows[1])
                        st.success("Assigned!")
            
            with tab2:
                st.markdown("**Assign zones by rectangular position**")
                
                zone_to_assign = st.selectbox(
                    "Zone to Assign",
                    ["desuperheat", "condense", "subcool"],
                    key="zone_select"
                )
                
                max_x = float(np.max(tube_sheet.tube_positions[:, 0]))
                max_y = float(np.max(tube_sheet.tube_positions[:, 1]))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    x_range = st.slider(
                        "X Range (mm)",
                        0.0, max_x, (0.0, max_x/3),
                        key="x_range"
                    )
                
                with col2:
                    y_range = st.slider(
                        "Y Range (mm)",
                        0.0, max_y, (0.0, max_y),
                        key="y_range"
                    )
                
                if st.button("✅ Assign Selected Region", key="btn_region"):
                    tube_sheet.assign_zone_by_position(zone_to_assign, x_range, y_range)
                    st.success(f"Assigned region to {zone_to_assign} zone!")
            
            with tab3:
                st.markdown("**Auto-assign by percentage (typical distribution)**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pct_desup = st.slider("Desuperheat %", 0, 50, 15, key="pct_desup")
                
                with col2:
                    pct_cond = st.slider("Condensation %", 0, 100, 70, key="pct_cond")
                
                with col3:
                    pct_sub = st.slider("Subcool %", 0, 50, 15, key="pct_sub")
                
                total_pct = pct_desup + pct_cond + pct_sub
                
                if total_pct != 100:
                    st.warning(f"⚠️ Total = {total_pct}% (should be 100%)")
                
                if st.button("🤖 Auto-Assign by Percentage", key="btn_auto"):
                    # Auto-assign by rows based on percentages
                    n_rows = int(np.ceil(np.sqrt(inputs['n_tubes'])))
                    
                    rows_desup = int(n_rows * pct_desup / 100)
                    rows_cond = int(n_rows * pct_cond / 100)
                    rows_sub = n_rows - rows_desup - rows_cond
                    
                    tube_sheet.assign_zone_by_rows("desuperheat", 0, rows_desup)
                    tube_sheet.assign_zone_by_rows("condense", rows_desup, rows_desup + rows_cond)
                    tube_sheet.assign_zone_by_rows("subcool", rows_desup + rows_cond, n_rows)
                    
                    st.success("Auto-assigned zones!")
        
        # Display tube sheet
        st.markdown("### 🎨 Tube Sheet Layout")
        
        fig = tube_sheet.draw_tube_sheet_interactive(show_zones=st.session_state.enable_zoned)
        st.plotly_chart(fig, use_container_width=True)
        
        # Zone summary
        if st.session_state.enable_zoned:
            summary = tube_sheet.get_zone_summary()
            
            st.markdown("### 📊 Zone Distribution Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Desuperheat",
                    f"{summary['desuperheat']['count']} tubes",
                    f"{summary['desuperheat']['percentage']:.0f}%"
                )
            
            with col2:
                st.metric(
                    "Condensation",
                    f"{summary['condense']['count']} tubes",
                    f"{summary['condense']['percentage']:.0f}%"
                )
            
            with col3:
                st.metric(
                    "Subcool",
                    f"{summary['subcool']['count']} tubes",
                    f"{summary['subcool']['percentage']:.0f}%"
                )
            
            with col4:
                st.metric(
                    "Inactive",
                    f"{summary['inactive']['count']} tubes",
                    f"{summary['inactive']['percentage']:.0f}%"
                )
            
            # Validation
            if summary['inactive']['count'] > 0:
                st.warning(
                    f"⚠️ {summary['inactive']['count']} tubes are not assigned to any zone. "
                    f"They will not contribute to heat transfer."
                )
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Back", key="nav_back_4"):
                st.session_state.design_step = 3
                st.rerun()
        
        with col3:
            if st.button("Next: Calculate Performance →", type="primary", key="nav_next_4"):
                # Store tube zones
                if st.session_state.enable_zoned:
                    st.session_state.tube_zones = tube_sheet.export_tube_zones()
                else:
                    # All tubes in all zones (standard design)
                    st.session_state.tube_zones = None
                
                st.session_state.design_step = 5
                st.rerun()
    
    # ========================================================================
    # STEP 5: SEGMENT CALCULATION
    # ========================================================================
    
    def step5_segment_calculation(self):
        """Run segment-by-segment calculation"""
        
        st.markdown("## Step 5: Segment-by-Segment Calculation")
        
        st.info("🔄 Running detailed segment-by-segment analysis...")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Prepare inputs
            inputs = st.session_state.inputs
            inputs['tube_zones'] = st.session_state.tube_zones
            inputs['water_inlet_pos'] = st.session_state.water_inlet_pos
            inputs['water_outlet_pos'] = st.session_state.water_outlet_pos
            inputs['tema_type'] = st.session_state.tema_type
            
            # Initialize segment model
            from segment_by_segment_model import SegmentBySegmentCondenser
            
            segment_model = SegmentBySegmentCondenser(n_segments=inputs['n_segments'])
            
            status_text.text("Calculating segment properties...")
            progress_bar.progress(20)
            
            # Run calculation
            results = segment_model.calculate_condenser_segmented(inputs)
            
            progress_bar.progress(80)
            status_text.text("Analyzing subcool zone...")
            
            # Store results
            st.session_state.segment_results = results
            
            progress_bar.progress(100)
            status_text.text("✅ Calculation complete!")
            
            # Auto-advance to results
            import time
            time.sleep(1)
            st.session_state.design_step = 6
            st.rerun()
        
        except Exception as e:
            st.error(f"❌ Calculation failed: {str(e)}")
            st.exception(e)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← Back to Fix Inputs"):
                    st.session_state.design_step = 1
                    st.rerun()
    
    # ========================================================================
    # STEP 6: RESULTS AND RECOMMENDATIONS
    # ========================================================================
    
    def step6_results_and_recommendations(self):
        """Display results with comprehensive recommendations"""
        
        st.markdown("## Step 6: Results & Recommendations")
        
        if st.session_state.segment_results is None:
            st.error("No results available. Please run calculation first.")
            if st.button("← Back to Calculate"):
                st.session_state.design_step = 5
                st.rerun()
            return
        
        results = st.session_state.segment_results
        
        # Quick summary at top
        self.display_quick_summary(results)
        
        # Detailed tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Performance",
            "🔬 Segment Analysis",
            "⚠️ Subcool Check",
            "📈 Visualizations",
            "📋 Recommendations"
        ])
        
        with tab1:
            self.display_performance_metrics(results)
        
        with tab2:
            self.display_segment_data(results)
        
        with tab3:
            self.display_subcool_analysis(results)
        
        with tab4:
            self.display_visualizations(results)
        
        with tab5:
            self.display_recommendations(results)
        
        # Export and navigation
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 New Design"):
                # Reset all
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("📝 Modify Inputs"):
                st.session_state.design_step = 1
                st.rerun()
        
        with col3:
            if st.button("📊 Export Report"):
                self.export_design_report(results)
        
        with col4:
            st.download_button(
                label="💾 Download Data",
                data=results['segments'].to_csv(index=False),
                file_name=f"condenser_segments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def display_quick_summary(self, results: Dict):
        """Quick summary metrics"""
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status = "✅ ADEQUATE" if results['subcool_adequate'] else "❌ INADEQUATE"
            st.metric("Design Status", status)
        
        with col2:
            st.metric(
                "Subcool Achieved",
                f"{results['subcool_achieved']:.2f} K",
                f"{results['subcool_achieved'] - results['subcool_required']:.2f} K",
                delta_color="normal" if results['subcool_adequate'] else "inverse"
            )
        
        with col3:
            st.metric(
                "Total Heat Transfer",
                f"{results['Q_total']/1000:.1f} kW"
            )
        
        with col4:
            st.metric(
                "Number of Segments",
                results['n_segments']
            )
    
    def display_performance_metrics(self, results: Dict):
        """Display detailed performance metrics"""
        
        st.markdown("### Overall Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Refrigerant Side:**")
            st.write(f"- Inlet Temp: {results['T_ref_in']:.1f}°C")
            st.write(f"- Outlet Temp: {results['T_ref_out']:.1f}°C")
            st.write(f"- Subcooling: {results['subcool_achieved']:.2f} K (required: {results['subcool_required']:.1f} K)")
        
        with col2:
            st.markdown("**Water Side:**")
            st.write(f"- Inlet Temp: {results['T_water_in']:.1f}°C")
            st.write(f"- Outlet Temp: {results['T_water_out']:.1f}°C")
            st.write(f"- Temperature Rise: {results['T_water_out'] - results['T_water_in']:.1f}°C")
        
        st.markdown("### Zone-wise Performance")
        
        zone_data = []
        for zone, summary in results['zone_summaries'].items():
            zone_data.append({
                "Zone": zone.capitalize(),
                "Length (m)": f"{summary['length_m']:.3f}",
                "Area (m²)": f"{summary['A_total']:.2f}",
                "Heat (kW)": f"{summary['Q_total']/1000:.2f}",
                "Avg U (W/m²·K)": f"{summary['U_avg']:.0f}",
                "Avg h_tube": f"{summary['h_tube_avg']:.0f}",
                "Avg LMTD (°C)": f"{summary['LMTD_avg']:.1f}"
            })
        
        df_zones = pd.DataFrame(zone_data)
        st.dataframe(df_zones, use_container_width=True)
    
    def display_segment_data(self, results: Dict):
        """Display segment-by-segment data"""
        
        st.markdown("### Detailed Segment Data")
        
        st.dataframe(results['segments'], use_container_width=True, height=400)
        
        # Summary statistics
        st.markdown("### Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Heat Transfer Coefficient Range:**")
            st.write(f"Min U: {results['segments']['U_local'].min():.0f} W/m²·K")
            st.write(f"Max U: {results['segments']['U_local'].max():.0f} W/m²·K")
        
        with col2:
            st.write("**LMTD Range:**")
            st.write(f"Min: {results['segments']['LMTD'].min():.1f}°C")
            st.write(f"Max: {results['segments']['LMTD'].max():.1f}°C")
        
        with col3:
            st.write("**Heat Transfer Range:**")
            st.write(f"Min: {results['segments']['Q_segment'].min()/1000:.2f} kW")
            st.write(f"Max: {results['segments']['Q_segment'].max()/1000:.2f} kW")
    
    def display_subcool_analysis(self, results: Dict):
        """Display subcool zone analysis"""
        
        subcool_analysis = results['subcool_analysis']
        
        if subcool_analysis['adequate']:
            st.success("✅ Subcool zone is ADEQUATE for required subcooling")
        else:
            st.error("❌ Subcool zone is INADEQUATE for required subcooling")
        
        # Show metrics
        if 'A_subcool_actual' in subcool_analysis:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Subcool Area Available",
                    f"{subcool_analysis['A_subcool_actual']:.2f} m²"
                )
            
            with col2:
                st.metric(
                    "Subcool Area Required",
                    f"{subcool_analysis['A_subcool_required']:.2f} m²"
                )
            
            with col3:
                ratio = subcool_analysis['area_ratio']
                delta = "sufficient" if ratio >= 1.0 else f"{(1-ratio)*100:.0f}% short"
                st.metric(
                    "Area Ratio",
                    f"{ratio:.2f}",
                    delta
                )
        
        # Show warnings
        if subcool_analysis['warnings']:
            st.markdown("### ⚠️ Issues Detected")
            for warning in subcool_analysis['warnings']:
                st.warning(warning)
        
        # Show recommendations
        if subcool_analysis['recommendations']:
            st.markdown("### 💡 Recommendations")
            for rec in subcool_analysis['recommendations']:
                st.markdown(f"- {rec}")
    
    def display_visualizations(self, results: Dict):
        """Display comprehensive visualizations"""
        
        from segment_by_segment_model import plot_segment_results
        
        fig = plot_segment_results(results)
        st.plotly_chart(fig, use_container_width=True)
    
    def display_recommendations(self, results: Dict):
        """Display actionable recommendations"""
        
        st.markdown("### 🎯 Design Recommendations")
        
        subcool_analysis = results['subcool_analysis']
        
        if subcool_analysis['adequate']:
            st.success(
                "✅ **Current design is adequate!** "
                "The subcool zone has sufficient area to achieve required subcooling."
            )
            
            st.markdown("#### Optimization Opportunities:")
            st.markdown("""
            - Consider reducing tube length slightly to save cost
            - Current design has margin - could handle higher subcooling if needed
            - Verify pressure drop is within acceptable limits
            """)
        
        else:
            st.error(
                "❌ **Design needs improvement!** "
                "The subcool zone is insufficient for required subcooling."
            )
            
            st.markdown("#### Priority Actions (Choose One):")
            
            for i, rec in enumerate(subcool_analysis['recommendations'], 1):
                st.markdown(f"**Option {i}:** {rec}")
            
            st.markdown("---")
            
            st.markdown("#### Detailed Guidance:")
            
            with st.expander("1️⃣ Increase Tube Length / Tube Count"):
                st.markdown("""
                **Pros:**
                - Simplest modification
                - Increases area uniformly
                
                **Cons:**
                - Increases cost proportionally
                - May not be space-efficient
                
                **How much to increase:**
                - Current deficit: Calculate from area ratio
                - Add 10-20% margin for safety
                
                **Implementation:**
                ```python
                # If area_ratio = 0.7 (30% short)
                # New length = current_length / 0.7 * 1.1
                # = 1.57 × current length
                ```
                """)
            
            with st.expander("2️⃣ Lower Water Inlet Temperature"):
                st.markdown("""
                **Pros:**
                - No mechanical changes needed
                - Improves LMTD in subcool zone
                
                **Cons:**
                - Requires colder water source
                - May increase cooling tower load
                
                **Effectiveness:**
                - Each 1°C reduction improves subcool capacity by ~5-10%
                - Most effective if currently pinch-limited
                
                **Typical Targets:**
                - Standard: 30-35°C
                - Improved: 25-30°C
                - Optimal: 20-25°C (chilled water)
                """)
            
            with st.expander("3️⃣ Add Separate Subcooler (RECOMMENDED) ⭐"):
                st.markdown("""
                **Pros:**
                - Most effective solution
                - Can use colder water source
                - Better control
                - Cheaper than oversizing main condenser
                
                **Cons:**
                - Requires additional equipment
                - Two units instead of one
                
                **Sizing:**
                - Area needed: (shown in analysis)
                - Typical: 10-15% of main condenser duty
                
                **Configuration:**
                ```
                [Main Condenser] → [Subcooler] → Expansion Valve
                   (Desup + Condense)  (Subcool)
                ```
                
                **Why This Works:**
                - Dedicated area for subcooling
                - Can use coldest water
                - Doesn't compete with condensation
                """)
            
            with st.expander("4️⃣ Enable Zoned Design"):
                if not st.session_state.enable_zoned:
                    st.markdown("""
                    **Currently Not Enabled**
                    
                    Zoned design allows separate tube banks for each zone,
                    with dedicated water flow paths.
                    
                    **Benefits:**
                    - Better control of each zone
                    - Can route coldest water to subcool zone
                    - More efficient use of available area
                    
                    **To Enable:**
                    - Go back to Step 1
                    - Check "Enable Zoned Condenser"
                    - Assign 15-20% of tubes to subcool zone
                    - Route cold water inlet to subcool zone
                    """)
                else:
                    st.markdown("""
                    **Already Enabled ✓**
                    
                    Consider adjusting zone assignments:
                    - Increase subcool zone tube count
                    - Ensure cold water routed to subcool zone
                    - Verify tube assignments are optimal
                    """)
            
            with st.expander("5️⃣ Increase Water Flow Rate"):
                st.markdown("""
                **Effectiveness:** ⚠️ Limited
                
                **Pros:**
                - Easy to implement (pump speed)
                - No mechanical changes
                
                **Cons:**
                - Only helps if NOT pinch-limited
                - Increases pumping power
                - May reduce overall effectiveness
                
                **When It Works:**
                - When LMTD in subcool zone is >5°C
                - When water outlet temp is still low
                
                **When It DOESN'T Work (Pinch-Limited):**
                - When LMTD in subcool zone is <3°C
                - When water outlet temp approaches refrigerant temp
                - More flow won't help - need more area or colder water
                
                **Check Your Situation:**
                ```
                Subcool zone LMTD from analysis:
                - If >5°C: Increasing flow may help
                - If 3-5°C: Marginal benefit
                - If <3°C: WON'T HELP - use other options
                ```
                """)
    
    def export_design_report(self, results: Dict):
        """Export comprehensive PDF report"""
        
        st.success("📊 Report generation feature coming soon!")
        st.info(
            "For now, you can download the segment data as CSV "
            "and create plots using the 'Download Data' button."
        )


# ============================================================================
# STREAMLIT APP ENTRY POINT
# ============================================================================

def main():
    """Main application entry point"""
    
    # Check password first
    if not check_password():
        return
    
    # Run integrated designer
    designer = IntegratedCondenserDesigner()
    designer.run()


if __name__ == "__main__":
    main()
