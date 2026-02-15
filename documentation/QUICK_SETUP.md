# Quick Setup Instructions

## 1. Files You Need

### Core Files (Required):
- ✅ `app.py` - Main application (UPDATED)
- ✅ `professional_condenser_designer.py` - NEW Professional condenser designer
- ✅ `shell_tube_evap_condenser_CORRECTED.py` - Calculation engine

### TEMA Diagrams (Required):
Create an `assets/` folder and place these images:
- ✅ `TEMA_TYPES_OFFICIAL_DIAGRAM.png`
- ✅ `TEMA_COMPONENTS_BEM_AEP_CFU.png`
- ✅ `TEMA_COMPONENTS_AES_DIAGRAM.png`

## 2. Directory Structure

```
your_project/
├── app.py
├── professional_condenser_designer.py
├── shell_tube_evap_condenser_CORRECTED.py
└── assets/
    ├── TEMA_TYPES_OFFICIAL_DIAGRAM.png
    ├── TEMA_COMPONENTS_BEM_AEP_CFU.png
    └── TEMA_COMPONENTS_AES_DIAGRAM.png
```

## 3. Run the Application

```bash
streamlit run app.py
```

## 4. Password

Enter: `Semaanju`

## 5. Navigate to New Feature

Select: **🔧 Condenser Designer (Professional)**

Then choose:
- Mode A: Shell-Side Refrigerant (traditional)
- Mode B: **Tube-Side Refrigerant (DX)** ⭐ **NEW!**

## 6. DX Mode Quick Start

### Step 1: Calculate Requirements
- Enter your design parameters
- Click "Calculate Required Rows"
- See how many rows each zone needs

### Step 2: Allocate Rows
- Adjust row allocation
- Click "Calculate with This Allocation"

### Step 3: Optimize
- View actual subcooling achieved
- Follow recommendations
- Iterate until satisfied

---

## What's Different from Before?

### REMOVED:
- ❌ Advanced Segment Model (wasn't working)

### NEW:
- ✅ Professional Condenser Designer
- ✅ Two modes: Shell-side OR Tube-side refrigerant
- ✅ DX mode with ROW-BASED allocation
- ✅ Interactive subcooling optimization
- ✅ Official TEMA diagrams

### UNCHANGED:
- ✅ Evaporator Designer (still works the same)
- ✅ Standard Condenser (still works the same)

---

## Need Help?

See `README_UPDATED.md` for full documentation including:
- Complete feature list
- Technical details
- Example calculations
- Troubleshooting

---

**Ready to use!** 🚀
