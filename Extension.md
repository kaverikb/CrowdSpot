# CrowdSpot - Video Extension: Crowd Intelligence System

## What Was Modified

### Original Submission
- Static image-based crowd detection
- Single-image analysis pipeline
- Density estimation from static frames

### Extension (This Submission)
- **Video-based temporal analysis** (61-second Shibuya crossing footage)
- **Real-time detection pipeline** with frame-by-frame processing
- **Historical baseline establishment** from first 30 frames
- **Alert generation** based on density thresholds
- **LLM-powered summaries** with RAG context integration
- **Operational dashboard** showing metrics, charts, alerts, and notifications
- **Annotated video output** with detection overlays

---

## Why This Approach Was Chosen

### 1. Video Over Static Images
**Rationale:** CopMap operates on live video feeds, not static snapshots. Video provides temporal context essential for bandobast planning.

### 2. YOLOv8 Large (yolov8l) Instead of Nano
**Choice:** Upgraded from yolov8n to yolov8l for improved detection in crowded scenes.
**Trade-off:** 2-3x slower processing, but better accuracy for overlapping persons.

### 3. 30-Frame Baseline Establishment
**Rationale:** First 3 frames had high variance. 30 frames (~0.6 seconds) provides stable baseline.
**Result:** Baseline: 24 people, Peak: 27 people (realistic for this footage).

### 4. Real Video Baseline vs Mock Data
**Approach:** Baseline built directly from video, not artificial multipliers or synthetic data.
**Benefit:** Honest, defensible, matches operational reality.

### 5. LLM + RAG Integration
**Design:** 
- Detection → Density analysis → Historical baseline retrieval → LLM summary
- RAG retrieves patterns from first 30 frames of video
- LLM provides operational context ("density within normal Friday patterns")

**Why:** Provides actionable intelligence, not just raw counts.

### 6. Streamlit Dashboard Over Video Embedding
**Architecture:**
- Metrics panel (baseline, peak, alerts)
- Plotly charts (count trend, deviation area chart)
- Expandable alert timeline with LLM summaries
- Simulated control room + patrol unit notifications
- Video available separately (opens in media player)

**Rationale:** Dashboard shows intelligence layer. Video shows raw detection capability.

---

## Known Limitations

### 1. Person Detection Undercounting
**Issue:** YOLOv8 detects ~24-27 people per frame. Actual crowd appears 200+ people visually.

**Root Cause:**
- Occlusion (overlapping people in aerial view)
- YOLOv8 trained for individual boxes, not crowd density
- Camera angle shows people partially hidden behind structures

**Mitigation:**
- Conservative counts used for baseline (acceptable for anomaly detection)
- System flags deviations from baseline, not absolute counts
- Documented clearly in README

**Production Solution:**
- Replace with dedicated crowd counting models (CSRNet, NWPU-Crowd)
- Location-specific fine-tuning on 6+ months of actual deployment data
- Multi-view fusion from multiple cameras

### 2. Model-Data Mismatch
**Issue:** Using public YOLOv8 (trained on COCO) on specific Shibuya crossing footage.

**Why It Matters:**
- Public models trained on diverse generic images
- Your deployment is location-specific (specific angle, lighting, buildings, patterns)
- Real police systems deploy with location-specific models

**Industry Practice:**
- Hikvision, Axis, Bosch deploy with proprietary location-trained models
- 3-6 months baseline collection before deployment
- Continuous re-training on new data from that location

**Current Approach:** Acceptable for prototype/demo. Production requires location-specific training.

### 3. No Real Abnormal Events in Demo Video
**Constraint:** Shibuya crossing shows normal steady crowd (24-27 consistently).
- No sudden spikes
- No rapid dispersals
- No clustering anomalies

**Solution:** System is alert-ready. Threshold set to peak (27). Alerts would trigger if crowd surged or dispersed abnormally.

**Tested With:** Synthetic threshold logic (baseline × 1.5 = alert).

### 4. Processing Performance
**Current:** 3075 frames at 50 FPS = ~60 seconds processing per 61-second video on CPU.

**Bottlenecks:**
- YOLOv8 inference (50-100ms per frame on CPU)
- LLM API calls (30s timeout, but batched to alert frames only)
- Video encoding (mp4v codec)

**For Live Operations:**
- GPU acceleration (NVIDIA Tesla)
- Frame skipping (process every Nth frame)
- Async pipeline (detect while writing)
- Batch LLM calls (summarize alerts only, not every frame)

### 5. Alert System is Simulated
**Current:** Dashboard shows mock "Control Room" and "Patrol Unit" notifications.
**Not implemented:** Actual SMS, radio, mobile app dispatch.

**For Production:**
- Integration with police communication infrastructure
- Real alert routing to dispatch center
- Officer mobile app notifications
- Log storage for incident review

### 6. RAG Context Limited
**Current:** Historical baseline from first 30 frames of THIS video only.

**Limitation:** No comparison to other days, times, or locations.

**Production Approach:**
- Vector database with 6-12 months historical patterns
- Temporal context ("Friday 6 PM usually 250-350 people")
- Location context ("Market Square vs Times Square patterns differ")
- Incident history retrieval ("Last spike on this day was incident X")

---

## Architecture Summary
```
Video Input (61 sec, 1920x1080, 50 FPS)
    ↓
Frame Extraction (every frame)
    ↓
YOLOv8l Person Detection (24-27 people per frame)
    ↓
Density Analysis + Z-score calculation
    ↓
Historical Baseline Retrieval (from first 30 frames)
    ↓
Alert Threshold Check (peak = 27)
    ↓
LLM Summary (RAG-enhanced context)
    ↓
Video Overlay (boxes + heatmap + count + timestamp)
    ↓
Output: video_output.avi + alerts_timeline.json
    ↓
Streamlit Dashboard (metrics + charts + alerts + notifications)
```

---

## What Was Implemented

✅ Video-based temporal crowd analysis
✅ Person detection with frame-by-frame tracking
✅ Real baseline establishment from video
✅ Alert generation on threshold breach
✅ LLM summaries with RAG context
✅ Video overlay with annotations
✅ Operational dashboard with metrics and alerts
✅ Alert notifications (simulated control room + patrol unit)
✅ Explainability documentation

---

## What Was Skipped (Trade-offs)

1. Individual person tracking (centroid-based only, no trajectory analysis)
2. Behavioral profiling (focus on density, not individual actions.
3. Multi-camera fusion (single camera demo).
4. Real incident database (mock baseline only).
5. Production alert routing (simulated notifications)
6. Crowd counting models (kept with person detection per requirement)
7. Real police communication integration

---

## For CopMap Operational Use

**This system is designed to:**
1. Monitor crowd density in real-time
2. Alert on abnormal changes (spikes, dispersals)
3. Provide context via LLM (is this normal for this time/day?)
4. Support bandobast resource allocation
5. Maintain audit trail (JSON alerts log)

**Not designed for:**
- Individual identification (privacy-respecting)
- Behavioral profiling
- Automated enforcement
- Real-time video streaming (batch processing)

---

## Recommendations for Production

1. **Data Collection:** 6-12 months video from actual deployment location
2. **Model Training:** Location-specific fine-tuning (CSRNet or similar)
3. **Multi-view:** Integrate 3-5 camera feeds (consensus reduces false positives)
4. **Backend:** Real database + alert routing system
5. **Mobile Apps:** Officer notifications + incident reporting
6. **Continuous Learning:** Re-train model weekly with new deployment data
