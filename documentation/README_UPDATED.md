# TEMA Heat Exchanger Designer - Updated Version
## February 2026

### 🎯 What's New

#### ✅ REMOVED:
- ❌ Advanced Segment Model (was not working)

#### ⭐ NEW: Professional Condenser Designer

Complete condenser design tool with **TWO operating modes**:

### Mode A: Shell-Side Refrigerant (Traditional)
- Refrigerant: Shell side (condensing)
- Water/Glycol: Tube side  
- TEMA Types: BEM, AEM, AES
- Baffles: **Vertical cut** (for condensate drainage)
- Calculation: Simple area distribution
- **Best for:** Large tonnage, flooded condensers, standard HVAC

### Mode B: Tube-Side Refrigerant (DX) ⭐ **YOUR REQUEST!**
- Refrigerant: **Tube side** (phase-changing)
- Water/Glycol: **Shell side** (cross-flow)
- TEMA Types: BEM, BEU
- Baffles: **Horizontal cut** (up-down zigzag)
- Calculation: **ROW-BASED with user allocation** ⭐
- **Best for:** DX systems, high-pressure refrigerants, precise subcooling control

---

## 📂 File Structure

```
your_directory/
├── app.py                                    # Main application (UPDATED)
├── professional_condenser_designer.py        # NEW! Professional condenser designer
├── shell_tube_evap_condenser_CORRECTED.py   # Calculation engine (existing)
└── assets/                                   # TEMA diagrams
    ├── TEMA_TYPES_OFFICIAL_DIAGRAM.png
    ├── TEMA_COMPONENTS_BEM_AEP_CFU.png
    └── TEMA_COMPONENTS_AES_DIAGRAM.png
```

---

## 🚀 How to Run

1. **Place all files in the same directory**

2. **Create an `assets` folder and add TEMA images:**
   ```
   mkdir assets
   # Copy TEMA images to assets/
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Enter password:** `Semaanju`

5. **Navigate to applications:**
   - ❄️ DX Evaporator Designer (unchanged)
   - 🔥 Condenser Designer (Standard) (unchanged)
   - 🔧 Condenser Designer (Professional) ⭐ **NEW!**

---

## 🎯 DX Condenser Workflow (Tube-Side Refrigerant)

### Step 1: Calculate Requirements
1. Enter design parameters (refrigerant, temperatures, flow rates, geometry)
2. Click "📊 Calculate Required Rows"
3. Program shows:
   - Rows needed for desuperheat zone
   - Rows needed for condensing zone
   - Rows needed for subcooling zone (based on target subcool)

### Step 2: Allocate Rows
1. See recommended allocation from Step 1
2. Adjust row allocation for each zone
3. Program validates total = allocated
4. Click "🎯 Calculate with This Allocation"

### Step 3: Results & Optimization
1. View actual subcooling achieved
2. See zone-by-zone performance
3. Get warnings if zones are undersized
4. Follow recommendations:
   - "Add X more rows to subcooling zone"
   - "Reduce water inlet temperature"
5. Iterate allocation and recalculate until satisfied

---

## 📊 Key Features

### DX Mode Features:
✅ **Row-based segmentation** - Physical rows of tubes
✅ **User allocation control** - You decide how many rows per zone
✅ **Actual subcooling calculation** - See real performance
✅ **Warnings & recommendations** - Guided optimization
✅ **Iterative design** - Adjust and recalculate easily
✅ **TEMA compliance** - BEM/BEU type selection with official diagrams

### Shell-Side Mode Features:
✅ **Traditional design** - Refrigerant on shell side
✅ **Simple calculation** - Fast area distribution method
✅ **TEMA types** - BEM, AEM, AES support
✅ **Vertical baffles** - Proper condensate drainage

---

## 🔧 Technical Details

### Why Row-Based for DX?

**Tube-Side Refrigerant Configuration:**
- Refrigerant flows **through tubes** (desuperheat → condense → subcool)
- Water flows **across tube rows** on shell side (horizontal baffles)
- Each row of tubes = discrete heat transfer unit
- Natural segmentation by rows (not by length)

**User Control:**
- Total rows: 40 (example)
- Desuperheat: Rows 1-8
- Condensing: Rows 9-35
- Subcooling: Rows 36-40

**Calculation:**
- Program calculates heat transfer row-by-row
- Water temperature increases as it crosses each row
- Refrigerant temperature decreases zone-by-zone
- Actual subcooling determined by rows allocated

### Why Simple Calculation for Shell-Side?

**Shell-Side Refrigerant Configuration:**
- Refrigerant condenses **uniformly** in shell
- Vertical baffles allow condensate drainage
- No distinct row-based zones
- Area distribution method appropriate

---

## 🎨 TEMA Diagrams

The application uses **official TEMA 10th Edition diagrams**:

1. **Figure N-1.2** - Complete TEMA nomenclature
2. **Figure N-2** - Detailed component configurations
   - BEM, BEU, AEP, CFU
   - AES

These diagrams appear during TEMA type selection for professional presentation.

---

## ⚙️ Application Modes Summary

| Application | Refrigerant Location | Water Location | TEMA Types | Segmentation | Status |
|------------|---------------------|----------------|-----------|--------------|--------|
| **Evaporator** | Tube side | Shell side | BEM/BEU | None | ✅ Unchanged |
| **Condenser (Standard)** | Shell side | Tube side | BEM/AEM | None | ✅ Unchanged |
| **Condenser (Professional) - Mode A** | Shell side | Tube side | BEM/AEM/AES | Simple | 🆕 New |
| **Condenser (Professional) - Mode B** | **Tube side** ⭐ | **Shell side** ⭐ | BEM/BEU | **Row-Based** ⭐ | 🆕 **YOUR REQUEST** |

---

## 💡 Example Usage (DX Mode)

### Scenario:
Design a DX condenser for R410A refrigeration system

**Inputs:**
- Refrigerant: R410A
- Condensing temp: 40°C
- Superheat: 10K
- Target subcool: 5K
- Refrigerant flow: 1.0 kg/s
- Water inlet: 25°C
- Water flow: 5.0 kg/s
- Tubes: 5/8" BWG 18
- Length: 3m
- Tubes per row: 10

**Step 1 Results:**
- Desuperheat needs: 8 rows
- Condensing needs: 27 rows  
- Subcooling needs: 5 rows for 5K subcool
- Total: 40 rows

**Step 2 - User Allocates:**
- User tries: 8 + 27 + 5 = 40 rows
- Calculates...

**Step 3 - Results:**
- Actual subcool: 5.1K ✅
- All zones adequate ✅
- Design accepted!

**Alternative Scenario - Insufficient Subcooling:**
- User tries: 8 + 29 + 3 = 40 rows
- Actual subcool: 3.2K ❌
- Warning: "Need 5 rows for 5K subcool"
- Recommendation: "Add 2 more rows to subcool zone"
- User adjusts: 8 + 27 + 5 = 40 rows
- Recalculates ✅

---

## 🛠️ Troubleshooting

### Issue: TEMA images not showing
**Solution:** Create `assets/` folder and place images there, or update image paths in `professional_condenser_designer.py`

### Issue: Import error for calculation engine
**Solution:** Make sure `shell_tube_evap_condenser_CORRECTED.py` is in the same directory

### Issue: Professional condenser not appearing
**Solution:** Make sure `professional_condenser_designer.py` is in the same directory as `app.py`

---

## 📞 Support

For questions or issues, refer to the code comments or contact the developer.

---

**Version:** 2.0  
**Date:** February 2026  
**Compliance:** TEMA 10th Edition
