```markdown
# TEMA Heat Exchanger Designer

Professional design tool for DX evaporators and condensers.

## Features
- ❄️ DX Evaporator Designer
- 🔥 Condenser Designer (Standard)
- 🔬 Condenser Designer (Advanced Segment Model)

## Installation
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Password
Semaanju
```

---

## 🔧 IMPORTANT: Fix Import in integrated_condenser_designer.py

After placing the file in modules/, open `modules/integrated_condenser_designer.py` and make these changes:

**Find these lines (around line 450):**
```python
from interactive_tube_sheet_designer import InteractiveTubeSheet
from segment_by_segment_model import SegmentBySegmentCondenser
```

**Change to (add a dot):**
```python
from .interactive_tube_sheet_designer import InteractiveTubeSheet
from .segment_by_segment_model import SegmentBySegmentCondenser
```

**Also find this line (if it exists around line 960):**
```python
from modules.integrated_condenser_designer import IntegratedCondenserDesigner
```

**Delete it** (you're already inside that file!)

---

## ✅ FINAL STRUCTURE VERIFICATION

Your folder should look exactly like this:

```
heat-exchanger-designer/
│
├── app.py
├── shell_tube_evap_condenser_CORRECTED.py
├── requirements.txt
├── .gitignore
├── README.md
│
└── modules/
    ├── __init__.py
    ├── integrated_condenser_designer.py
    ├── segment_by_segment_model.py
    └── interactive_tube_sheet_designer.py
```

**File Count Check:**
- Root directory: 5 files
- modules/ directory: 4 files
- **Total: 9 files**

---

## 🧪 TEST LOCALLY

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Should open at http://localhost:8501
# Password: Semaanju
```

---

## ☁️ DEPLOY TO STREAMLIT CLOUD

```bash
# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Add remote (replace with your GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/heat-exchanger-designer.git

# Push
git branch -M main
git push -u origin main
```

Then:
1. Go to https://share.streamlit.io/
2. Click "New app"
3. Repository: YOUR_USERNAME/heat-exchanger-designer
4. Branch: main
5. Main file: app.py
6. Deploy!

---

## 📋 CHECKLIST

Before deploying:
- [ ] All 9 files in correct locations
- [ ] modules/__init__.py exists (even if empty)
- [ ] integrated_condenser_designer_COMPLETE.py renamed to integrated_condenser_designer.py
- [ ] Imports fixed in integrated_condenser_designer.py (add dots)
- [ ] Tested locally with `streamlit run app.py`
- [ ] All three modes work (Evaporator, Condenser Standard, Condenser Advanced)
- [ ] Password works (Semaanju)
- [ ] Pushed to GitHub
- [ ] Ready to deploy!

---

## 🎉 YOU'RE DONE!

All files are available for download above.
Follow this guide to organize them correctly.
Deploy to Streamlit Cloud.
Enjoy your professional heat exchanger designer!
