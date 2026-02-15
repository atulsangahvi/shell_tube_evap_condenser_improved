"""
SEGMENT-BY-SEGMENT CONDENSER MODEL
Advanced physically-accurate calculation with visual tube sheet design

This module provides:
1. Segment-by-segment calculation (10-50 segments)
2. State tracking (superheat → two-phase → subcooled)
3. Local property variations
4. Subcool zone analysis
5. Interactive tube sheet design
"""

import numpy as np
import pandas as pd
import math
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class SegmentBySegmentCondenser:
    """
    Segment-by-segment condenser calculation model.
    
    Physically accurate model that:
    - Divides condenser into N segments along flow path
    - Tracks refrigerant state changes (phase transitions)
    - Calculates local properties and HTCs
    - Identifies zone boundaries
    - Provides detailed temperature profiles
    """
    
    def __init__(self, n_segments: int = 20):
        """
        Initialize segment model
        
        Args:
            n_segments: Number of segments (10-50 recommended)
        """
        self.n_segments = n_segments
        self.segments = []
        self.zone_boundaries = {}
        
    def calculate_condenser_segmented(self, inputs: Dict) -> Dict:
        """
        Main calculation method using segment-by-segment approach
        
        Args:
            inputs: Design parameters including:
                - Refrigerant properties and flow rates
                - Water/glycol properties and flow rates
                - Geometry (tubes, length, material)
                - Tube zone assignments (if zoned design)
        
        Returns:
            results: Comprehensive results including:
                - Segment-by-segment data
                - Zone boundaries
                - Temperature profiles
                - Performance metrics
        """
        
        # Extract inputs
        refrigerant = inputs["refrigerant"]
        m_dot_ref = inputs["m_dot_ref"]
        T_ref_in = inputs["T_ref_in_superheated"]
        T_cond = inputs["T_ref"]
        subcool_req = inputs["delta_T_sh_sc"]
        
        # Tube zone assignments (for zoned designs)
        tube_zones = inputs.get("tube_zones", None)  # Dict mapping tube numbers to zones
        
        # Geometry
        n_tubes = inputs["n_tubes"]
        tube_length = inputs["tube_length"]
        tube_od = inputs["tube_od"]
        tube_id = inputs["tube_id"]
        
        # Segment length
        L_segment = tube_length / self.n_segments
        
        # Initialize tracking arrays
        segments_data = []
        
        # Water properties and flow
        m_dot_water = inputs["m_dot_water"]
        C_water = inputs["C_water"]
        T_water_in = inputs["T_water_in"]
        
        # Initial conditions
        T_ref = T_ref_in  # Current refrigerant temperature
        T_water = T_water_in  # Current water temperature
        h_ref = self.get_enthalpy(refrigerant, T_ref, P=inputs["P_cond"], phase="vapor")
        
        # Refrigerant properties at saturation
        h_fg = inputs["ref_props"]["h_fg"] * 1000  # J/kg
        h_f = self.get_enthalpy(refrigerant, T_cond, P=inputs["P_cond"], phase="liquid")
        h_g = h_f + h_fg
        
        # Track cumulative heat transfer
        Q_cumulative = 0.0
        
        # Zone tracking
        zone_start_indices = {}
        current_zone = None
        
        # ====================================================================
        # SEGMENT LOOP: March along tube length
        # ====================================================================
        for i in range(self.n_segments):
            
            segment = {}
            segment["segment_number"] = i + 1
            segment["position_m"] = i * L_segment + L_segment / 2  # Midpoint
            segment["length_m"] = L_segment
            
            # ----------------------------------------------------------------
            # STEP 1: Determine refrigerant state and phase
            # ----------------------------------------------------------------
            if T_ref > T_cond + 0.1:
                # Superheated vapor
                phase = "superheat"
                quality = None
                
            elif h_ref > h_g - 100:  # Small margin for numerical stability
                # Superheated vapor near saturation
                phase = "superheat"
                quality = None
                
            elif h_ref > h_f + 100:
                # Two-phase region
                phase = "two_phase"
                quality = (h_ref - h_f) / h_fg if h_fg > 0 else 0.5
                quality = max(0.0, min(1.0, quality))  # Bound [0,1]
                
            else:
                # Subcooled liquid
                phase = "subcooled"
                quality = None
            
            segment["phase"] = phase
            segment["quality"] = quality
            segment["T_ref"] = T_ref
            
            # Track zone changes
            if phase != current_zone:
                zone_start_indices[phase] = i
                current_zone = phase
            
            # ----------------------------------------------------------------
            # STEP 2: Get local refrigerant properties
            # ----------------------------------------------------------------
            if phase == "superheat":
                # Vapor properties
                ref_props = self.get_refrigerant_properties(
                    refrigerant, T_ref, phase="vapor"
                )
                cp_ref = ref_props["cp_vapor"] * 1000  # J/kg·K
                
            elif phase == "two_phase":
                # Two-phase properties (weighted average)
                ref_props_v = self.get_refrigerant_properties(
                    refrigerant, T_cond, phase="vapor"
                )
                ref_props_l = self.get_refrigerant_properties(
                    refrigerant, T_cond, phase="liquid"
                )
                
                # For heat capacity, use phase change (infinite)
                cp_ref = 1e10  # Very large for phase change
                
            else:  # subcooled
                # Liquid properties
                ref_props = self.get_refrigerant_properties(
                    refrigerant, T_ref, phase="liquid"
                )
                cp_ref = ref_props["cp_liquid"] * 1000  # J/kg·K
            
            # ----------------------------------------------------------------
            # STEP 3: Calculate local heat transfer coefficients
            # ----------------------------------------------------------------
            
            # Determine which tubes are active in this zone (for zoned designs)
            if tube_zones is not None:
                active_tubes = self.get_active_tubes_in_zone(tube_zones, phase)
                n_tubes_active = len(active_tubes)
            else:
                # All tubes active in all zones
                n_tubes_active = n_tubes
                active_tubes = list(range(n_tubes))
            
            segment["n_tubes_active"] = n_tubes_active
            
            if n_tubes_active == 0:
                # No tubes assigned to this zone - skip
                segment["Q_segment"] = 0.0
                segment["h_tube"] = 0.0
                segment["U_local"] = 0.0
                segments_data.append(segment)
                continue
            
            # Tube-side HTC (refrigerant)
            if phase == "superheat":
                h_tube = self.calculate_single_phase_htc_local(
                    m_dot_ref, tube_id, ref_props, n_tubes_active
                )
                
            elif phase == "two_phase":
                # Condensation HTC
                h_tube = self.calculate_condensation_htc_local(
                    m_dot_ref, tube_id, T_cond, quality,
                    ref_props_l, ref_props_v, n_tubes_active
                )
                
            else:  # subcooled
                h_tube = self.calculate_single_phase_htc_local(
                    m_dot_ref, tube_id, ref_props, n_tubes_active
                )
            
            segment["h_tube"] = h_tube
            
            # Shell-side HTC (water) - depends on which tubes are active
            h_shell = self.calculate_shell_side_htc_local(
                inputs, n_tubes_active
            )
            segment["h_shell"] = h_shell
            
            # Overall U for this segment
            U_local = self.calculate_U_local(
                h_tube, h_shell, tube_od, tube_id,
                inputs["tube_k"], inputs["R_fouling_tube"], inputs["R_fouling_shell"]
            )
            segment["U_local"] = U_local
            
            # ----------------------------------------------------------------
            # STEP 4: Calculate heat transfer in this segment
            # ----------------------------------------------------------------
            
            # Surface area for active tubes in this segment
            A_segment = math.pi * tube_od * L_segment * n_tubes_active
            segment["A_segment"] = A_segment
            
            # Temperature driving force
            if phase == "two_phase":
                # For two-phase, refrigerant at constant T_cond
                LMTD_segment = T_cond - T_water
            else:
                # For single-phase, need to estimate outlet temp
                # Use simplified approach: assume linear temperature change
                dT_ref_estimate = 2.0  # K (will iterate)
                T_ref_out_est = T_ref - dT_ref_estimate if phase == "superheat" else T_ref + dT_ref_estimate
                dT_water_estimate = 0.2  # K
                T_water_out_est = T_water + dT_water_estimate
                
                # LMTD for counterflow
                dt1 = T_ref - T_water_out_est
                dt2 = T_ref_out_est - T_water
                
                if dt1 > 0 and dt2 > 0:
                    LMTD_segment = (dt1 - dt2) / math.log(dt1 / dt2) if abs(dt1 - dt2) > 0.01 else (dt1 + dt2) / 2
                else:
                    LMTD_segment = 5.0  # Fallback
            
            segment["LMTD"] = LMTD_segment
            
            # Heat transfer in this segment
            Q_segment = U_local * A_segment * LMTD_segment
            segment["Q_segment"] = Q_segment
            
            # ----------------------------------------------------------------
            # STEP 5: Update temperatures and enthalpies
            # ----------------------------------------------------------------
            
            # Refrigerant side
            if phase == "two_phase":
                # Update enthalpy
                h_ref = h_ref - Q_segment / m_dot_ref
                T_ref = T_cond  # Stays at saturation
                
            else:
                # Single phase - update temperature
                T_ref = T_ref - Q_segment / (m_dot_ref * cp_ref)
                h_ref = h_ref - Q_segment / m_dot_ref
            
            # Water side (always single phase)
            T_water = T_water + Q_segment / C_water
            
            segment["T_ref_out"] = T_ref
            segment["T_water_out"] = T_water
            segment["h_ref"] = h_ref
            
            # Cumulative heat transfer
            Q_cumulative += Q_segment
            segment["Q_cumulative"] = Q_cumulative
            
            # Store segment data
            segments_data.append(segment)
        
        # ====================================================================
        # POST-PROCESSING: Analyze results
        # ====================================================================
        
        # Create DataFrame for easy analysis
        df_segments = pd.DataFrame(segments_data)
        
        # Identify zone boundaries
        zone_boundaries = self.identify_zone_boundaries(df_segments)
        
        # Calculate zone-wise summaries
        zone_summaries = self.calculate_zone_summaries(df_segments, zone_boundaries)
        
        # Check subcool adequacy
        subcool_analysis = self.analyze_subcool_zone(
            df_segments, zone_boundaries, subcool_req,
            T_cond, inputs
        )
        
        # Overall performance
        Q_total = Q_cumulative
        T_ref_out = T_ref
        T_water_out = T_water
        
        subcool_achieved = T_cond - T_ref_out
        
        # ====================================================================
        # COMPILE RESULTS
        # ====================================================================
        
        results = {
            # Segment data
            "segments": df_segments,
            "n_segments": self.n_segments,
            
            # Zone information
            "zone_boundaries": zone_boundaries,
            "zone_summaries": zone_summaries,
            
            # Overall performance
            "Q_total": Q_total,
            "T_ref_in": T_ref_in,
            "T_ref_out": T_ref_out,
            "T_water_in": T_water_in,
            "T_water_out": T_water_out,
            "subcool_required": subcool_req,
            "subcool_achieved": subcool_achieved,
            "subcool_adequate": subcool_achieved >= subcool_req * 0.95,
            
            # Subcool analysis
            "subcool_analysis": subcool_analysis,
            
            # For visualization
            "temperature_profile": self.create_temperature_profile(df_segments),
            "htc_profile": self.create_htc_profile(df_segments),
            "phase_map": self.create_phase_map(df_segments)
        }
        
        return results
    
    def identify_zone_boundaries(self, df: pd.DataFrame) -> Dict:
        """Identify where phase transitions occur"""
        
        boundaries = {}
        
        # Find first occurrence of each phase
        for phase in ["superheat", "two_phase", "subcooled"]:
            phase_segments = df[df["phase"] == phase]
            if len(phase_segments) > 0:
                boundaries[phase] = {
                    "start_segment": phase_segments.iloc[0]["segment_number"],
                    "end_segment": phase_segments.iloc[-1]["segment_number"],
                    "start_position_m": phase_segments.iloc[0]["position_m"],
                    "end_position_m": phase_segments.iloc[-1]["position_m"],
                    "length_m": phase_segments["length_m"].sum(),
                    "n_segments": len(phase_segments)
                }
        
        return boundaries
    
    def calculate_zone_summaries(self, df: pd.DataFrame, boundaries: Dict) -> Dict:
        """Calculate summary statistics for each zone"""
        
        summaries = {}
        
        for phase, bounds in boundaries.items():
            phase_df = df[df["phase"] == phase]
            
            summaries[phase] = {
                "Q_total": phase_df["Q_segment"].sum(),
                "A_total": phase_df["A_segment"].sum(),
                "length_m": bounds["length_m"],
                "U_avg": phase_df["U_local"].mean() if len(phase_df) > 0 else 0,
                "h_tube_avg": phase_df["h_tube"].mean() if len(phase_df) > 0 else 0,
                "LMTD_avg": phase_df["LMTD"].mean() if len(phase_df) > 0 else 0,
                "n_segments": bounds["n_segments"]
            }
        
        return summaries
    
    def analyze_subcool_zone(self, df: pd.DataFrame, boundaries: Dict,
                            subcool_req: float, T_cond: float,
                            inputs: Dict) -> Dict:
        """
        Analyze subcool zone adequacy and provide recommendations
        """
        
        analysis = {
            "adequate": False,
            "warnings": [],
            "recommendations": []
        }
        
        # Check if subcool zone exists
        if "subcooled" not in boundaries:
            analysis["warnings"].append(
                "⚠️ CRITICAL: No subcooled zone detected! "
                "Refrigerant exits as saturated liquid or two-phase."
            )
            analysis["recommendations"].extend([
                "1. Increase total tube length by 20-30%",
                "2. Add separate subcooler (RECOMMENDED)",
                "3. Reduce water inlet temperature",
                "4. Increase water flow rate"
            ])
            return analysis
        
        # Subcool zone exists - analyze it
        subcool_df = df[df["phase"] == "subcooled"]
        
        # Actual subcool area
        A_subcool_actual = subcool_df["A_segment"].sum()
        
        # Calculate REQUIRED subcool area
        # Q_subcool_req = m_dot_ref × cp_liquid × subcool_req
        m_dot_ref = inputs["m_dot_ref"]
        cp_liquid = inputs["ref_props"]["cp_liquid"] * 1000  # J/kg·K
        Q_subcool_req = m_dot_ref * cp_liquid * subcool_req
        
        # Average U and LMTD in subcool zone
        U_subcool_avg = subcool_df["U_local"].mean()
        LMTD_subcool_avg = subcool_df["LMTD"].mean()
        
        # Required area
        if U_subcool_avg > 0 and LMTD_subcool_avg > 0:
            A_subcool_req = Q_subcool_req / (U_subcool_avg * LMTD_subcool_avg)
        else:
            A_subcool_req = 0.0
        
        analysis["A_subcool_actual"] = A_subcool_actual
        analysis["A_subcool_required"] = A_subcool_req
        analysis["area_ratio"] = A_subcool_actual / A_subcool_req if A_subcool_req > 0 else 999
        
        # Check adequacy
        if A_subcool_actual >= A_subcool_req * 0.95:
            analysis["adequate"] = True
        else:
            analysis["adequate"] = False
            deficit = A_subcool_req - A_subcool_actual
            deficit_percent = (deficit / A_subcool_req * 100) if A_subcool_req > 0 else 0
            
            analysis["warnings"].append(
                f"⚠️ Subcool zone area insufficient: "
                f"Has {A_subcool_actual:.2f} m², needs {A_subcool_req:.2f} m² "
                f"(deficit: {deficit:.2f} m², {deficit_percent:.0f}%)"
            )
            
            # Recommendations based on severity
            if deficit_percent > 50:
                # Severe deficit - need major changes
                analysis["recommendations"].extend([
                    "🚨 SEVERE DEFICIT - Major changes needed:",
                    f"1. Add separate subcooler with {deficit * 1.2:.2f} m² area (STRONGLY RECOMMENDED)",
                    f"2. OR increase tube length by {deficit_percent * 1.1:.0f}%",
                    "3. Consider zoned condenser with dedicated subcool section"
                ])
            elif deficit_percent > 20:
                # Moderate deficit - need changes
                analysis["recommendations"].extend([
                    "⚠️ MODERATE DEFICIT - Changes recommended:",
                    f"1. Increase tube length by {deficit_percent * 1.1:.0f}%",
                    f"2. OR add separate subcooler with {deficit * 1.2:.2f} m² area",
                    "3. Lower water inlet temperature by 3-5°C if possible",
                    "4. Increase water flow rate by 20-30%"
                ])
            else:
                # Minor deficit - optimization
                analysis["recommendations"].extend([
                    "ℹ️ MINOR DEFICIT - Optimization options:",
                    f"1. Increase tube length by {deficit_percent * 1.1:.0f}%",
                    "2. Lower water inlet temperature by 2-3°C",
                    "3. Increase water flow rate by 10-15%",
                    "4. Current design may be acceptable with slight subcool reduction"
                ])
        
        # Check for thermal pinch at subcool inlet
        if len(subcool_df) > 0:
            T_water_at_subcool_start = subcool_df.iloc[0]["T_water_out"]
            approach_at_start = T_cond - T_water_at_subcool_start
            
            if approach_at_start < 3.0:
                analysis["warnings"].append(
                    f"⚠️ THERMAL PINCH: Temperature approach at subcool zone inlet "
                    f"is only {approach_at_start:.1f}°C. This severely limits subcooling performance."
                )
                analysis["recommendations"].append(
                    "5. ⚠️ Consider zoned design to dedicate cooler water to subcool zone"
                )
        
        return analysis
    
    def get_active_tubes_in_zone(self, tube_zones: Dict, current_phase: str) -> List[int]:
        """
        Determine which tubes are active in the current zone
        
        Args:
            tube_zones: Dictionary mapping tube numbers to zones
                        e.g., {1: "desuperheat", 2: "desuperheat", ..., 180: "subcool"}
            current_phase: Current phase ("superheat", "two_phase", "subcooled")
        
        Returns:
            List of tube numbers active in this zone
        """
        
        # Map phases to zone names
        phase_to_zone = {
            "superheat": "desuperheat",
            "two_phase": "condense",
            "subcooled": "subcool"
        }
        
        zone_name = phase_to_zone.get(current_phase, "condense")
        
        # Find tubes assigned to this zone
        active_tubes = [
            tube_num for tube_num, zone in tube_zones.items()
            if zone == zone_name
        ]
        
        return active_tubes
    
    def create_temperature_profile(self, df: pd.DataFrame) -> Dict:
        """Create temperature profile data for plotting"""
        return {
            "position": df["position_m"].tolist(),
            "T_ref": df["T_ref"].tolist(),
            "T_water": df["T_water_out"].tolist(),
            "phase": df["phase"].tolist()
        }
    
    def create_htc_profile(self, df: pd.DataFrame) -> Dict:
        """Create HTC profile data for plotting"""
        return {
            "position": df["position_m"].tolist(),
            "h_tube": df["h_tube"].tolist(),
            "h_shell": df["h_shell"].tolist(),
            "U_local": df["U_local"].tolist()
        }
    
    def create_phase_map(self, df: pd.DataFrame) -> Dict:
        """Create phase distribution map"""
        return {
            "position": df["position_m"].tolist(),
            "phase": df["phase"].tolist(),
            "quality": df["quality"].tolist()
        }
    
    # ========================================================================
    # PLACEHOLDER METHODS (implement based on your existing code)
    # ========================================================================
    
    def get_refrigerant_properties(self, refrigerant, T, phase):
        """Get refrigerant properties - use your existing method"""
        # Placeholder - use your existing implementation
        pass
    
    def get_enthalpy(self, refrigerant, T, P, phase):
        """Get enthalpy - use CoolProp or your tables"""
        # Placeholder
        pass
    
    def calculate_single_phase_htc_local(self, m_dot, D, props, n_tubes):
        """Calculate single-phase HTC - use your Gnielinski correlation"""
        # Placeholder
        pass
    
    def calculate_condensation_htc_local(self, m_dot, D, T_sat, quality, props_l, props_v, n_tubes):
        """Calculate condensation HTC - use your Dobson-Chato correlation"""
        # Placeholder
        pass
    
    def calculate_shell_side_htc_local(self, inputs, n_tubes_active):
        """Calculate shell-side HTC"""
        # Placeholder
        pass
    
    def calculate_U_local(self, h_tube, h_shell, tube_od, tube_id, k, R_foul_t, R_foul_s):
        """Calculate local overall U"""
        R_wall = (tube_od / (2.0 * k)) * math.log(tube_od / tube_id)
        U = 1.0 / (
            1.0/h_tube +
            (tube_od/tube_id)/h_shell +
            R_wall +
            R_foul_t +
            (tube_od/tube_id)*R_foul_s
        )
        return U


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_segment_results(results: Dict) -> go.Figure:
    """
    Create comprehensive visualization of segment-by-segment results
    """
    
    df = results["segments"]
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=(
            "Temperature Profiles",
            "Heat Transfer Coefficients",
            "Heat Transfer Rate per Segment",
            "Phase Distribution"
        ),
        vertical_spacing=0.08,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    position = df["position_m"]
    
    # Row 1: Temperature profiles
    fig.add_trace(
        go.Scatter(x=position, y=df["T_ref"], name="Refrigerant",
                  line=dict(color="red", width=3)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=position, y=df["T_water_out"], name="Water",
                  line=dict(color="blue", width=3)),
        row=1, col=1
    )
    
    # Add zone boundaries
    for phase, bounds in results["zone_boundaries"].items():
        fig.add_vline(
            x=bounds["start_position_m"],
            line_dash="dash", line_color="gray",
            row=1, col=1
        )
    
    # Row 2: HTCs
    fig.add_trace(
        go.Scatter(x=position, y=df["h_tube"], name="h_tube",
                  line=dict(color="orange", width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=position, y=df["h_shell"], name="h_shell",
                  line=dict(color="green", width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=position, y=df["U_local"], name="U_local",
                  line=dict(color="purple", width=2)),
        row=2, col=1
    )
    
    # Row 3: Heat transfer rate
    fig.add_trace(
        go.Bar(x=position, y=df["Q_segment"]/1000, name="Q_segment (kW)",
               marker_color="lightblue"),
        row=3, col=1
    )
    
    # Row 4: Phase distribution
    phase_colors = {"superheat": "red", "two_phase": "orange", "subcooled": "blue"}
    for phase in df["phase"].unique():
        phase_df = df[df["phase"] == phase]
        fig.add_trace(
            go.Scatter(x=phase_df["position_m"], y=[1]*len(phase_df),
                      mode="markers", name=phase,
                      marker=dict(color=phase_colors.get(phase, "gray"),
                                 size=10, symbol="square")),
            row=4, col=1
        )
    
    # Update axes
    fig.update_xaxes(title_text="Position along tube (m)", row=4, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_yaxes(title_text="HTC (W/m²·K)", row=2, col=1)
    fig.update_yaxes(title_text="Heat Rate (kW)", row=3, col=1)
    fig.update_yaxes(title_text="Phase", row=4, col=1)
    
    fig.update_layout(
        height=1200,
        title_text="Segment-by-Segment Condenser Analysis",
        showlegend=True
    )
    
    return fig


def display_segment_results_streamlit(results: Dict):
    """Display segment results in Streamlit"""
    import streamlit as st
    
    st.markdown("## 📊 Segment-by-Segment Analysis")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Segments", results["n_segments"])
    
    with col2:
        st.metric("Subcool Achieved", 
                 f"{results['subcool_achieved']:.2f} K",
                 delta=f"{results['subcool_achieved'] - results['subcool_required']:.2f} K")
    
    with col3:
        adequacy = "✅ Adequate" if results["subcool_adequate"] else "❌ Insufficient"
        st.metric("Subcool Status", adequacy)
    
    with col4:
        st.metric("Total Heat Transfer", f"{results['Q_total']/1000:.1f} kW")
    
    # Zone summaries
    st.markdown("### Zone-wise Summary")
    
    zone_data = []
    for phase, summary in results["zone_summaries"].items():
        zone_data.append({
            "Zone": phase.capitalize(),
            "Length (m)": f"{summary['length_m']:.3f}",
            "Area (m²)": f"{summary['A_total']:.2f}",
            "Heat (kW)": f"{summary['Q_total']/1000:.1f}",
            "Avg U (W/m²·K)": f"{summary['U_avg']:.0f}",
            "Avg LMTD (°C)": f"{summary['LMTD_avg']:.1f}"
        })
    
    df_zones = pd.DataFrame(zone_data)
    st.dataframe(df_zones, use_container_width=True)
    
    # Subcool analysis
    if results["subcool_analysis"]["warnings"]:
        st.markdown("### ⚠️ Subcool Zone Analysis")
        for warning in results["subcool_analysis"]["warnings"]:
            st.warning(warning)
        
        if results["subcool_analysis"]["recommendations"]:
            st.markdown("**Recommendations:**")
            for rec in results["subcool_analysis"]["recommendations"]:
                st.markdown(f"- {rec}")
    
    # Plot results
    fig = plot_segment_results(results)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed segment data (expandable)
    with st.expander("📋 View Detailed Segment Data"):
        st.dataframe(results["segments"], use_container_width=True)
