# HydroTwin: Hackathon Live Demo Script & Pitch Guide

> **TARGET TIME**: 3 Minutes Live Presentation + 2 Minutes Jury Q&A.  
> **CONTEXT**: Embassy of Japan in Tunisia Hackathon (Water + Energy Track).  
> **AUDIENCE**: Hackathon Jury, Embassy Representatives, JICA Water Experts, SONEDE Engineers.  
> **CORE MOTTO**: *"The system ADVISES, humans DECIDE."*

---

## Part 1: 3-Minute Live Stage Presentation

### Minute 0:00 - 0:30 | The Bilateral Challenge & Baseline Digital Twin
- **Screen Action**:
  - Open HydroTwin at `http://localhost:8501`.
  - Ensure the sidebar toggle **"🚀 Guided 3-Minute Demo Mode"** is enabled and **Step 1** is selected.
  - Point to the yellow **Honesty Banner** and the blue **Advisory Badge** at the top.
- **Spoken Talk Track**:
  > *"Excellencies, esteemed jury members, and colleagues:*  
  > *Tunisia faces critical water stress: non-revenue water losses range between **25% and 50%** across municipal sectors, exacerbated by summer electricity grid shedding that cuts power to pumping stations. Meanwhile, Japanese utilities are world leaders in network efficiency, maintaining physical losses below 7% through high-density telemetry and proactive management.*  
  > *We present **HydroTwin**: an open-source, physics-driven digital twin designed to run on a standard laptop. It connects water conservation with energy optimization.*  
  > *First, notice our mandatory honesty rule: all data is 100% simulated, and our system only advises—human operators always decide.*  
  > *In **Step 1**, we observe our digital twin of 92 junctions divided into 5 municipal districts. Our Random Forest demand forecaster predicts district consumption 24 hours ahead with 90% confidence intervals, enabling predictive storage management."*

---

### Minute 0:30 - 1:05 | Leak Detection, Localization & Multilingual Work Order
- **Screen Action**:
  - In sidebar, click **"Next ➡️"** (advances to **Step 2: Physical Leak Injection**).
  - The map highlights the burst location in red and suspect pipes in orange.
  - In the sidebar language dropdown, switch language from **English** to **Français** or **العربية** (observe native RTL layout).
- **Spoken Talk Track**:
  > *"Now, in **Step 2**, a major pipe joint fails in the Centre-Ville district at 06:00, discharging over 35 cubic meters per hour.*  
  > *HydroTwin triggers a dual-track alarm: our district water balance detects an unexplained 14% gap, while spatial pressure analysis flags the anomaly.*  
  > *Crucially: HydroTwin does not claim to see underground cracks. Instead, using topological graph smoothing along the pipe network, it computes a ranked list of the **Top-5 suspect pipes**.*  
  > *Within seconds, the system generates an actionable work order in French, Arabic with native right-to-left formatting, or Japanese. Field technicians receive exact asset IDs, GPS-calibrated nodes, and acoustic inspection priorities."*

---

### Minute 1:05 - 1:45 | Water + Energy Nexus: Time-of-Use Pump Optimization
- **Screen Action**:
  - Click **"Next ➡️"** (advances to **Step 3: Diurnal Pumping Optimization**).
  - Point to the four metric cards and the 24-hour pump dispatch schedule graph.
- **Spoken Talk Track**:
  > *"Water and energy are deeply linked. In **Step 3**, we optimize pump dispatch through physical duty rebalancing.*  
  > *Under default operations, high-head intake Pump 10 (head ~73.8m) runs 14 hours/day, drawing 2,805 kWh. Our optimizer rebalances transmission pumping duty by shutting off Pump 10 at 12:00 (-3 hours ON, saving +602 kWh) and relying on lower-head distribution booster Pump 335 (head ~28.8m, +1 hour ON, consuming +310 kWh).*  
  > *Net daily electricity saved is exactly **292.1 kWh/day (-5.5%)**, yielding 86.2 TND/day under a flat tariff and 33.6 TND/day under assumed TOU tariffs, while delivering 100% of customer demand (62,124 m³ delivered in both plans; 0.0% curtailment) and ending the day with +92.4 m³ higher stored reservoir volume. Crucially, as proven by our decomposition, the savings stem from duty rebalancing across pump heads under the assumption of source interchangeability, not from off-peak timing."*

---

### Minute 1:45 - 2:20 | Honest Science: Robustness to Sparse Sensors
- **Screen Action**:
  - Click **"Next ➡️"** (advances to **Step 4: Transition to Sparse Telemetry**).
  - Show the side-by-side comparison table of Dense (24 sensors) vs. Sparse (6 sensors + 1 faulty).
- **Spoken Talk Track**:
  > *"A critical requirement of this hackathon is technical honesty. Japanese networks enjoy dense sensor coverage. But in emerging regional networks, operators may have only 6 pressure loggers across an entire town, and one might be broken.*  
  > *In **Step 4**, we evaluate robustness to sparse telemetry with one failing transducer.*  
  > *We do not make inflated claims: evaluated across 220 unseen leak scenarios, Top-5 exact localization is **30.9%** (37.7% adjacent) in dense mode, degrading to **12.7%** (19.5% adjacent) in sparse mode, while mean topological hop error increases from 3.3 to 7.4 hops.*  
  > *We evaluate spatial representations to help resource-constrained utilities assess leak risks without requiring millions in immediate telemetry Capex."*

---

### Minute 2:20 - 2:45 | Grid Blackout Stress-Testing & Stored Volume Resilience
- **Screen Action**:
  - Click **"Next ➡️"** (advances to **Step 5: Grid Power Crisis & Resilience**).
  - Highlight the reservoir drawdown volume analysis and the hospital clinic compliance (92.3%).
- **Spoken Talk Track**:
  > *"In **Step 5**, we stress-test the network under a severe summer grid failure: primary intake Pump 10 loses power for 4 hours (14:00 - 18:00).*  
  > *Because of Net3’s massive elevated storage in Tank 3, gravity distribution sustains **92.3% compliance (12 of 13 clinic junctions)** above the assumed hospital threshold (18 m) in both unmitigated and resilience scenarios (+0.0 pp binary gain, as Node 20 sits at high elevation).*  
  > *HydroTwin’s resilience module acts as a critical **stress-testing tool**: it quantifies reservoir volume depletion rates (~250 to 500 m³/h), alerts operators to storage autonomy limits, and advises pre-filling storage tanks before scheduled rolling blackouts to prevent total reservoir drainage."*

---

### Minute 2:45 - 3:00 | Conclusion & Bilateral Pilot Roadmap
- **Screen Action**:
  - Click **"Next ➡️"** (advances to **Step 6: Operational Advisory Sign-Off**).
  - Point to the live counters and the JICA roadmap box.
- **Spoken Talk Track**:
  > *"To conclude: HydroTwin demonstrates that physics-driven digital twins and transparent AI can run on standard laptops without proprietary cloud subscriptions or foreign SaaS lock-in.*  
  > *Our proposed next step is a **1-district pilot sandbox** in Greater Tunis or Sfax in collaboration with SONEDE and JICA engineers, operating strictly in advisory mode.*  
  > *Thank you very much. Arigatou gozaimasu. Chokran jazeelan. We welcome your questions."*

---

## Part 2: 2-Minute Jury Q&A Pitch Guide

### Question 1: *"Why do you refuse to let the AI control the pumps and valves automatically?"*
**Answer**:
> *"Water distribution is critical national infrastructure. Autonomous algorithmic control introduces severe risks of water hammer, pressure surges that rupture aging pipes, or unintended de-pressurization of fire hydrants. HydroTwin follows the fundamental human-in-the-loop principle: **the system advises, certified municipal operators decide**. The operator signs off on every dispatch change and field work order."*

### Question 2: *"How can this tool be useful in Tunisia if sensor density is low and meters are imprecise?"*
**Answer**:
> *"That is precisely why we developed the dual-track detection and sparse transfer engine. Even with just 6 pressure sensors and aging mechanical meters, HydroTwin isolates anomalies to a specific district and provides a ranked topological inspection radius of ~3 pipe segments. This transforms blind manual acoustic surveys across 100 kilometers into targeted field inspections of 300 meters, saving days of lost water."*

### Question 3: *"Is the multilingual AI assistant capable of hallucinating leaks that don't exist?"*
**Answer**:
> *"No. The multilingual engine uses deterministic template generation and structured intent matching grounded strictly in the simulation results JSON. The template-based assistant is tested to never mention a leak the detector did not report. All responses include an advisory footer and simulation reference."*

### Question 4: *"Why do you report Tunisian water losses as a range (25% to 50%) instead of a single official number?"*
**Answer**:
> *"Because municipal water distribution in Tunisia is heterogeneous. Published studies by the Ministry of Agriculture, CESE, and L'Economiste Maghrébin show that physical losses vary widely: from ~25% in newly developed urban sectors to over 45-50% in historical urban centers like the Medina or older distribution zones in Sfax. Quoting a single static national average would be technically misleading."*

### Question 5: *"What hardware is needed to run HydroTwin in a regional SONEDE district office?"*
**Answer**:
> *"Nothing more than an ordinary office laptop running Python. There are no GPU requirements, no external cloud dependencies, and zero proprietary software licenses. The entire stack uses open-source EPANET/WNTR and standard scientific libraries, making it immediately deployable across regional utility offices."*
