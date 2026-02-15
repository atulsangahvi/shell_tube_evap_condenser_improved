"""
INTERACTIVE TUBE SHEET DESIGNER
Visual interface for condenser zone configuration

Features:
1. TEMA general arrangement drawings
2. Interactive tube sheet layout
3. Mouse-based tube zone assignment
4. Water inlet/outlet marking
5. Visual validation of design
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math
from typing import Dict, List, Tuple, Optional
import pandas as pd


class TEMAArrangementDrawings:
    """
    TEMA General Arrangement Drawings
    Based on TEMA 10th Edition nomenclature
    """
    
    TEMA_TYPES = {
        "AES": {
            "front_head": "A - Channel and Removable Cover",
            "shell": "E - One Pass Shell",
            "rear_head": "S - Floating Head with Backing Device",
            "description": "Fixed tubesheet, single-pass shell, floating head",
            "typical_use": "General purpose, easy maintenance"
        },
        "AEL": {
            "front_head": "A - Channel and Removable Cover",
            "shell": "E - One Pass Shell",
            "rear_head": "L - Fixed Tubesheet Like A Stationary Head",
            "description": "Fixed tubesheet both ends, single-pass shell",
            "typical_use": "No thermal expansion issues, lowest cost"
        },
        "AET": {
            "front_head": "A - Channel and Removable Cover",
            "shell": "E - One Pass Shell",
            "rear_head": "T - Pull-Through Floating Head",
            "description": "Fixed front, floating rear, single-pass shell",
            "typical_use": "Medium thermal expansion, good maintenance"
        },
        "BEM": {
            "front_head": "B - Bonnet (Integral Cover)",
            "shell": "E - One Pass Shell",
            "rear_head": "M - Fixed Tubesheet Like B Stationary Head",
            "description": "Bonnet front, fixed rear, single-pass shell",
            "typical_use": "High pressure, compact design"
        },
        "AEP": {
            "front_head": "A - Channel and Removable Cover",
            "shell": "E - One Pass Shell",
            "rear_head": "P - Outside Packed Floating Head",
            "description": "Removable channel, floating head with packing",
            "typical_use": "Good for fouling service"
        },
        "BEU": {
            "front_head": "B - Bonnet (Integral Cover)",
            "shell": "E - One Pass Shell",
            "rear_head": "U - U-Tube Bundle",
            "description": "Bonnet front, U-tube bundle",
            "typical_use": "Excellent for thermal expansion"
        },
        "CFU": {
            "front_head": "C - Channel Integral with Tubesheet and Removable Cover",
            "shell": "F - Two Pass Shell with Longitudinal Baffle",
            "rear_head": "U - U-Tube Bundle",
            "description": "Integral channel, two-pass shell, U-tubes",
            "typical_use": "Compact, good heat transfer"
        },
        "AES-Z": {
            "front_head": "A - Channel and Removable Cover",
            "shell": "E - One Pass Shell WITH ZONE PARTITION",
            "rear_head": "S - Floating Head with Backing Device",
            "description": "Fixed tubesheet, zoned shell, floating head",
            "typical_use": "ZONED CONDENSER - Separate desuperheat/condense/subcool zones",
            "special": "zone_partition"
        },
        "AEL-Z": {
            "front_head": "A - Channel and Removable Cover",
            "shell": "E - One Pass Shell WITH ZONE PARTITION",
            "rear_head": "L - Fixed Tubesheet Like A Stationary Head",
            "description": "Fixed tubesheet both ends, zoned shell",
            "typical_use": "ZONED CONDENSER - Lowest cost zoned design",
            "special": "zone_partition"
        }
    }
    
    @staticmethod
    def draw_tema_arrangement(tema_type: str, with_dimensions: bool = True) -> go.Figure:
        """
        Draw TEMA general arrangement for specified type
        
        Args:
            tema_type: TEMA designation (e.g., "AES", "BEU", "AES-Z")
            with_dimensions: Include dimensional annotations
        
        Returns:
            Plotly figure with TEMA arrangement
        """
        
        if tema_type not in TEMAArrangementDrawings.TEMA_TYPES:
            tema_type = "AES"  # Default
        
        config = TEMAArrangementDrawings.TEMA_TYPES[tema_type]
        
        fig = go.Figure()
        
        # Draw shell
        fig.add_shape(
            type="rect",
            x0=1, y0=0.5, x1=9, y1=2.5,
            line=dict(color="black", width=3),
            fillcolor="lightgray",
            opacity=0.3
        )
        
        # Draw tubesheets
        fig.add_shape(
            type="line",
            x0=1, y0=0.5, x1=1, y1=2.5,
            line=dict(color="black", width=5)
        )
        fig.add_shape(
            type="line",
            x0=9, y0=0.5, x1=9, y1=2.5,
            line=dict(color="black", width=5)
        )
        
        # Draw front head
        if config["front_head"].startswith("A"):
            # Channel with removable cover
            fig.add_shape(
                type="rect",
                x0=0, y0=0.8, x1=1, y1=2.2,
                line=dict(color="blue", width=2),
                fillcolor="lightblue",
                opacity=0.3
            )
            fig.add_annotation(
                x=0.5, y=2.5, text="A<br>Removable<br>Cover",
                showarrow=False, font=dict(size=10)
            )
        elif config["front_head"].startswith("B"):
            # Bonnet
            fig.add_shape(
                type="circle",
                x0=0, y0=1, x1=1, y1=2,
                line=dict(color="blue", width=2),
                fillcolor="lightblue",
                opacity=0.3
            )
            fig.add_annotation(
                x=0.5, y=2.5, text="B<br>Bonnet",
                showarrow=False, font=dict(size=10)
            )
        
        # Draw shell type
        fig.add_annotation(
            x=5, y=3, text=f"E - Single Pass Shell",
            showarrow=False, font=dict(size=12, color="black")
        )
        
        # Draw rear head
        rear_head_code = config["rear_head"].split("-")[0].strip()
        
        if "U" in rear_head_code:
            # U-tube bundle
            fig.add_shape(
                type="path",
                path=f"M 9 0.5 Q 10 1.5 9 2.5",
                line=dict(color="red", width=3)
            )
            fig.add_annotation(
                x=9.5, y=2.5, text="U<br>U-Tube",
                showarrow=False, font=dict(size=10)
            )
        elif "S" in rear_head_code:
            # Floating head with backing device
            fig.add_shape(
                type="circle",
                x0=8.5, y0=1, x1=10, y1=2,
                line=dict(color="green", width=2, dash="dash"),
                fillcolor="lightgreen",
                opacity=0.3
            )
            fig.add_annotation(
                x=9.5, y=2.5, text="S<br>Floating<br>Head",
                showarrow=False, font=dict(size=10)
            )
        elif "L" in rear_head_code or "M" in rear_head_code:
            # Fixed tubesheet
            fig.add_shape(
                type="rect",
                x0=9, y0=0.8, x1=10, y1=2.2,
                line=dict(color="green", width=2),
                fillcolor="lightgreen",
                opacity=0.3
            )
            fig.add_annotation(
                x=9.5, y=2.5, text="L/M<br>Fixed",
                showarrow=False, font=dict(size=10)
            )
        
        # Add zone partition if zoned design
        if config.get("special") == "zone_partition":
            # Draw vertical partitions
            fig.add_shape(
                type="line",
                x0=3.5, y0=0.5, x1=3.5, y1=2.5,
                line=dict(color="red", width=3, dash="dash")
            )
            fig.add_shape(
                type="line",
                x0=7, y0=0.5, x1=7, y1=2.5,
                line=dict(color="red", width=3, dash="dash")
            )
            
            # Zone labels
            fig.add_annotation(x=2.25, y=1.5, text="Desuperheat<br>Zone",
                             showarrow=False, bgcolor="lightyellow")
            fig.add_annotation(x=5.25, y=1.5, text="Condensation<br>Zone",
                             showarrow=False, bgcolor="lightcoral")
            fig.add_annotation(x=8, y=1.5, text="Subcool<br>Zone",
                             showarrow=False, bgcolor="lightblue")
        
        # Add nozzles
        # Inlet nozzle (refrigerant)
        fig.add_annotation(
            x=0.5, y=2.2,
            ax=0.5, ay=3,
            text="Refrigerant IN",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="red"
        )
        
        # Outlet nozzle (refrigerant)
        fig.add_annotation(
            x=9.5, y=0.8,
            ax=9.5, ay=0,
            text="Refrigerant OUT",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="blue"
        )
        
        # Title
        fig.add_annotation(
            x=5, y=3.5,
            text=f"<b>TEMA Type: {tema_type}</b><br>{config['description']}",
            showarrow=False,
            font=dict(size=14)
        )
        
        fig.update_xaxes(range=[-0.5, 10.5], showgrid=False, zeroline=False, visible=False)
        fig.update_yaxes(range=[0, 4], showgrid=False, zeroline=False, visible=False)
        
        fig.update_layout(
            height=400,
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        return fig


class InteractiveTubeSheet:
    """
    Interactive tube sheet designer for zone assignment
    """
    
    def __init__(self, n_tubes: int, tube_layout: str = "triangular", 
                 tube_pitch: float = 15.0):
        """
        Initialize tube sheet
        
        Args:
            n_tubes: Total number of tubes
            tube_layout: "triangular" or "square"
            tube_pitch: Tube pitch in mm
        """
        self.n_tubes = n_tubes
        self.tube_layout = tube_layout
        self.tube_pitch = tube_pitch
        
        # Generate tube positions
        self.tube_positions = self.generate_tube_layout()
        
        # Initialize zone assignments (all tubes start in "condense" zone)
        self.tube_zones = {i: "condense" for i in range(n_tubes)}
        
        # Water flow path (inlet/outlet positions)
        self.water_inlet = None
        self.water_outlet = None
    
    def generate_tube_layout(self) -> np.ndarray:
        """
        Generate tube positions based on layout pattern
        
        Returns:
            Array of (x, y) coordinates for each tube
        """
        
        positions = []
        
        if self.tube_layout == "triangular":
            # Triangular pitch (60° pattern)
            n_rows = int(np.ceil(np.sqrt(self.n_tubes / 0.866)))
            
            for row in range(n_rows):
                n_tubes_in_row = int(np.sqrt(self.n_tubes / n_rows))
                y = row * self.tube_pitch * 0.866
                
                for col in range(n_tubes_in_row):
                    x = col * self.tube_pitch + (row % 2) * self.tube_pitch / 2
                    positions.append([x, y])
                    
                    if len(positions) >= self.n_tubes:
                        break
                
                if len(positions) >= self.n_tubes:
                    break
        
        else:  # square
            # Square pitch (90° pattern)
            n_rows = int(np.ceil(np.sqrt(self.n_tubes)))
            
            for row in range(n_rows):
                for col in range(n_rows):
                    x = col * self.tube_pitch
                    y = row * self.tube_pitch
                    positions.append([x, y])
                    
                    if len(positions) >= self.n_tubes:
                        break
                
                if len(positions) >= self.n_tubes:
                    break
        
        return np.array(positions[:self.n_tubes])
    
    def draw_tube_sheet_interactive(self, show_zones: bool = True) -> go.Figure:
        """
        Draw interactive tube sheet with zone coloring
        
        Args:
            show_zones: Color tubes by zone assignment
        
        Returns:
            Plotly figure with clickable tubes
        """
        
        fig = go.Figure()
        
        # Zone colors
        zone_colors = {
            "desuperheat": "red",
            "condense": "orange",
            "subcool": "blue",
            "inactive": "lightgray"
        }
        
        # Plot tubes by zone
        if show_zones:
            for zone in ["desuperheat", "condense", "subcool", "inactive"]:
                tube_indices = [i for i, z in self.tube_zones.items() if z == zone]
                
                if tube_indices:
                    positions = self.tube_positions[tube_indices]
                    
                    fig.add_trace(go.Scatter(
                        x=positions[:, 0],
                        y=positions[:, 1],
                        mode='markers',
                        marker=dict(
                            size=self.tube_pitch * 0.6,
                            color=zone_colors[zone],
                            line=dict(width=2, color='black'),
                            opacity=0.8
                        ),
                        name=f"{zone.capitalize()} ({len(tube_indices)} tubes)",
                        text=[f"Tube {i}<br>Zone: {zone}" for i in tube_indices],
                        hoverinfo='text',
                        customdata=tube_indices  # Store tube indices for clicking
                    ))
        else:
            # Show all tubes in gray
            fig.add_trace(go.Scatter(
                x=self.tube_positions[:, 0],
                y=self.tube_positions[:, 1],
                mode='markers',
                marker=dict(
                    size=self.tube_pitch * 0.6,
                    color='lightgray',
                    line=dict(width=2, color='black')
                ),
                name="Tubes",
                text=[f"Tube {i}" for i in range(self.n_tubes)],
                hoverinfo='text'
            ))
        
        # Draw shell boundary (circle)
        shell_diameter = np.max(self.tube_positions) * 1.2
        theta = np.linspace(0, 2*np.pi, 100)
        shell_x = shell_diameter/2 * np.cos(theta)
        shell_y = shell_diameter/2 * np.sin(theta)
        
        fig.add_trace(go.Scatter(
            x=shell_x, y=shell_y,
            mode='lines',
            line=dict(color='black', width=3),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add water inlet/outlet markers if set
        if self.water_inlet is not None:
            fig.add_annotation(
                x=self.water_inlet[0], y=self.water_inlet[1],
                text="WATER IN",
                showarrow=True,
                arrowhead=2,
                arrowsize=2,
                arrowcolor="blue",
                bgcolor="lightblue",
                bordercolor="blue"
            )
        
        if self.water_outlet is not None:
            fig.add_annotation(
                x=self.water_outlet[0], y=self.water_outlet[1],
                text="WATER OUT",
                showarrow=True,
                arrowhead=2,
                arrowsize=2,
                arrowcolor="red",
                bgcolor="lightcoral",
                bordercolor="red"
            )
        
        fig.update_layout(
            title="Interactive Tube Sheet - Click to Assign Zones",
            xaxis=dict(
                scaleanchor="y",
                scaleratio=1,
                showgrid=True,
                gridcolor='lightgray',
                title="X Position (mm)"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                title="Y Position (mm)"
            ),
            height=600,
            hovermode='closest',
            plot_bgcolor='white'
        )
        
        return fig
    
    def assign_zone_by_position(self, zone_name: str, 
                               x_range: Tuple[float, float],
                               y_range: Tuple[float, float]):
        """
        Assign tubes to a zone based on position ranges
        
        Args:
            zone_name: "desuperheat", "condense", or "subcool"
            x_range: (x_min, x_max) in mm
            y_range: (y_min, y_max) in mm
        """
        
        for i, (x, y) in enumerate(self.tube_positions):
            if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
                self.tube_zones[i] = zone_name
    
    def assign_zone_by_rows(self, zone_name: str, row_start: int, row_end: int):
        """
        Assign tubes to a zone by row numbers
        
        Args:
            zone_name: "desuperheat", "condense", or "subcool"
            row_start: Starting row (0-indexed)
            row_end: Ending row (inclusive)
        """
        
        # Determine row for each tube based on y-position
        y_positions = self.tube_positions[:, 1]
        unique_y = np.unique(y_positions)
        
        for i, y in enumerate(y_positions):
            row_idx = np.where(unique_y == y)[0][0]
            if row_start <= row_idx <= row_end:
                self.tube_zones[i] = zone_name
    
    def get_zone_summary(self) -> Dict:
        """Get summary of zone assignments"""
        
        summary = {}
        for zone in ["desuperheat", "condense", "subcool", "inactive"]:
            count = sum(1 for z in self.tube_zones.values() if z == zone)
            percentage = count / self.n_tubes * 100
            summary[zone] = {
                "count": count,
                "percentage": percentage
            }
        
        return summary
    
    def export_tube_zones(self) -> Dict:
        """Export tube zone assignments for use in segment calculation"""
        return self.tube_zones.copy()


def create_tube_sheet_interface_streamlit():
    """
    Create Streamlit interface for interactive tube sheet design
    """
    import streamlit as st
    
    st.markdown("## 🎨 Interactive Tube Sheet Designer")
    
    # Initialize session state
    if 'tube_sheet' not in st.session_state:
        st.session_state.tube_sheet = None
    if 'zona_mode' not in st.session_state:
        st.session_state.zone_mode = "condense"
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        n_tubes = st.number_input("Number of Tubes", 
                                 min_value=10, max_value=500, value=200)
        tube_layout = st.selectbox("Tube Layout", ["triangular", "square"])
    
    with col2:
        tube_pitch = st.number_input("Tube Pitch (mm)", 
                                     min_value=10.0, max_value=50.0, value=15.0)
        
        enable_zoned = st.checkbox("Enable Zoned Condenser (Integral Subcooler)")
    
    # Create/update tube sheet
    if st.button("Generate Tube Sheet") or st.session_state.tube_sheet is None:
        st.session_state.tube_sheet = InteractiveTubeSheet(
            n_tubes=n_tubes,
            tube_layout=tube_layout,
            tube_pitch=tube_pitch
        )
        st.success("Tube sheet generated!")
    
    if st.session_state.tube_sheet is not None:
        tube_sheet = st.session_state.tube_sheet
        
        # Zone assignment controls
        if enable_zoned:
            st.markdown("### Zone Assignment")
            
            tab1, tab2, tab3 = st.tabs(["By Rows", "By Position", "Manual Selection"])
            
            with tab1:
                st.markdown("**Assign zones by row ranges**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    desup_rows = st.slider("Desuperheat Rows", 
                                          0, n_tubes//20, (0, n_tubes//20//3))
                    if st.button("Assign Desuperheat"):
                        tube_sheet.assign_zone_by_rows("desuperheat", 
                                                       desup_rows[0], desup_rows[1])
                
                with col2:
                    cond_rows = st.slider("Condense Rows",
                                         0, n_tubes//20, (n_tubes//20//3, n_tubes//20*2//3))
                    if st.button("Assign Condense"):
                        tube_sheet.assign_zone_by_rows("condense",
                                                       cond_rows[0], cond_rows[1])
                
                with col3:
                    sub_rows = st.slider("Subcool Rows",
                                        0, n_tubes//20, (n_tubes//20*2//3, n_tubes//20))
                    if st.button("Assign Subcool"):
                        tube_sheet.assign_zone_by_rows("subcool",
                                                       sub_rows[0], sub_rows[1])
            
            with tab2:
                st.markdown("**Assign zones by position ranges**")
                st.info("Select rectangular regions on the tube sheet")
                
                zone_to_assign = st.selectbox("Zone to Assign",
                                             ["desuperheat", "condense", "subcool"])
                
                col1, col2 = st.columns(2)
                with col1:
                    x_range = st.slider("X Range (mm)", 
                                       0.0, float(np.max(tube_sheet.tube_positions[:, 0])),
                                       (0.0, float(np.max(tube_sheet.tube_positions[:, 0])/3)))
                
                with col2:
                    y_range = st.slider("Y Range (mm)",
                                       0.0, float(np.max(tube_sheet.tube_positions[:, 1])),
                                       (0.0, float(np.max(tube_sheet.tube_positions[:, 1]))))
                
                if st.button("Assign Selected Region"):
                    tube_sheet.assign_zone_by_position(zone_to_assign, x_range, y_range)
                    st.success(f"Assigned region to {zone_to_assign} zone")
        
        # Display tube sheet
        fig = tube_sheet.draw_tube_sheet_interactive(show_zones=enable_zoned)
        st.plotly_chart(fig, use_container_width=True)
        
        # Zone summary
        if enable_zoned:
            summary = tube_sheet.get_zone_summary()
            
            st.markdown("### 📊 Zone Distribution")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Desuperheat Tubes",
                         f"{summary['desuperheat']['count']} ({summary['desuperheat']['percentage']:.0f}%)")
            
            with col2:
                st.metric("Condense Tubes",
                         f"{summary['condense']['count']} ({summary['condense']['percentage']:.0f}%)")
            
            with col3:
                st.metric("Subcool Tubes",
                         f"{summary['subcool']['count']} ({summary['subcool']['percentage']:.0f}%)")
        
        # Export button
        if st.button("✅ Confirm Zone Assignment & Calculate"):
            tube_zones = tube_sheet.export_tube_zones()
            st.session_state['confirmed_tube_zones'] = tube_zones
            st.success("Zone assignment confirmed! Ready for segment calculation.")
            
            # Show what will be calculated
            st.info(
                f"Segment-by-segment calculation will use:\n"
                f"- {summary['desuperheat']['count']} tubes for desuperheat zone\n"
                f"- {summary['condense']['count']} tubes for condensation zone\n"
                f"- {summary['subcool']['count']} tubes for subcool zone"
            )
