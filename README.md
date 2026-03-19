 # GigShield — Parametric Income Insurance for Food Delivery Partners

A platform that automatically detects external disruptions affecting food delivery workers and processes income-replacement payouts without requiring workers to file manual claims.

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Persona & Scenarios](#2-persona--scenarios)
3. [Application Workflow](#3-application-workflow)
4. [Weekly Premium Model](#4-weekly-premium-model)
5. [Parametric Triggers](#5-parametric-triggers)
6. [AI/ML Integration Plan](#6-aiml-integration-plan)
7. [Adversarial Defense & Anti-Spoofing Strategy](#7-adversarial-defense--anti-spoofing-strategy)
8. [Tech Stack](#8-tech-stack)
9. [Architecture](#9-architecture)
10. [Development Plan](#10-development-plan)
11. [Constraints & Exclusions](#11-constraints--exclusions)

## 1. Problem Statement

Food delivery workers on platforms like Zomato and Swiggy have no income safety net. When an external event — a heavy rainstorm, a sudden curfew, a severe pollution alert — makes it impossible to work, they lose that day's wages with no recourse. This platform monitors external conditions in real time, determines when a covered disruption has occurred in a worker's active zone, and initiates a payout for the estimated income lost — without requiring the worker to do anything beyond initial registration.

## 2. Persona & Scenarios

**Chosen Persona:** Food delivery partners working with Zomato or Swiggy in tier-1 Indian cities (Mumbai, Delhi, Bengaluru, Hyderabad, Chennai).

**Why this persona:** Food delivery is the highest-volume segment where income is directly tied to hours active on the platform. Disruptions that make roads impassable or reduce order volume have an immediate, measurable income impact.

**Typical worker profile:**
- Works 6–10 hours per day, 6 days a week
- Earns between Rs. 600 and Rs. 1,200 per day depending on city and hours
- Operates in 1–3 delivery zones within a city
- Does not have access to formal financial products

**Scenarios this platform covers:**

| Scenario | Disruption Type | How It Affects Income |
|---|---|---|
| Heavy rainfall makes roads impassable | Environmental | Orders drop, roads unsafe, platform reduces active zones |
| Cyclone warning triggers city-wide red alert | Environmental | Platform suspends operations in affected zones |
| AQI crosses severe threshold (500+) | Environmental | Platform activity drops in affected zones |
| Local curfew due to unplanned civil event | Social | Worker cannot reach pickup or drop locations |
| Zonal market closure due to strike | Social | Pickup locations unavailable |

## 3. Application Workflow

### 3.1 Onboarding

1. Worker registers via app or WhatsApp bot (WhatsApp chosen for low-friction access)
2. Provides delivery platform ID, city, and primary delivery zones
3. Platform API (mock) pulls 4-week earnings history to establish an income baseline
4. Risk profile is generated based on zone, city tier, and historical disruption frequency
5. Weekly premium is calculated and shown before the worker confirms
6. Payment collected via UPI; coverage starts the following Monday

### 3.2 Disruption Detection and Claim Initiation

1. Trigger engine fires when API data breaches a defined threshold in a zone
2. System identifies all active workers registered in that zone
3. A claim is automatically initiated for each qualifying worker — no manual filing required
4. Fraud detection layer evaluates each claim before approval
5. Approved claims are paid out within minutes via UPI/Razorpay
6. Worker receives a notification with payout amount and reason

## 4. Weekly Premium Model

**Why weekly pricing:** Gig workers are paid weekly by their platforms. Aligning the premium cycle with the earnings cycle reduces friction and makes coverage sustainable for the worker.

```
Base Weekly Premium = f(city_risk_tier, zone_disruption_rate, avg_daily_income, coverage_hours_per_week)
```

| Factor | Description |
|---|---|
| City risk tier | Historical frequency and severity of disruptions per city |
| Zone disruption rate | How often the worker's zone has experienced covered events in the past 12 months |
| Average daily income | Derived from 4-week earnings history at onboarding |
| Coverage hours | Worker chooses 6, 8, or 10 hours of daily coverage |

**Indicative premium range:** Rs. 30–80 per week.

**Payout calculation:**

```
Payout = avg_hourly_income x disruption_duration_in_hours
```

The disruption window is derived from API timestamps, not worker reporting.

## 5. Parametric Triggers

| Trigger | Data Source | Threshold |
|---|---|---|
| Heavy rainfall | OpenWeatherMap / IMD | > 64.5 mm in 24 hours |
| Extreme heat | OpenWeatherMap / IMD | > 45°C with heat action plan advisory |
| Severe AQI | CPCB AQI API | AQI > 400 for 3+ consecutive hours |
| Cyclone / Flood warning | IMD Disaster alerts | Red alert issued for the district |
| Curfew / Section 144 | Government civic alert API / mock | Official curfew notification for the area |
| Zone closure (strike) | Civic alert mock + admin flag | Admin-confirmed zone closure |

## 6. AI/ML Integration Plan

**Dynamic Premium Calculation:** A Gradient Boosted Decision Tree (XGBoost) trained on IMD historical weather records, CPCB AQI data, and mock delivery earnings by zone. Features include zone-level disruption frequency, seasonal risk index, and worker shift pattern. The model is retrained monthly as new data accumulates.

**Fraud Detection:** Covered in Section 7.

**Payout Estimation:** A regression model that estimates income lost based on disruption duration and the worker's historical earnings pattern during similar time windows.

**Risk Trend Prediction:** A time-series model (SARIMA) that predicts disruption probability per zone for the coming week. Used by the admin dashboard to project expected claim volumes and manage liquidity.

## 7. Adversarial Defense & Anti-Spoofing Strategy

This section addresses coordinated fraud where bad actors use GPS-spoofing tools to fake their location inside a weather alert zone and trigger mass false payouts.

### 7.1 The Differentiation: Genuine Stranded Worker vs GPS Spoofer

A genuine stranded worker leaves a consistent trail across multiple independent data sources. A GPS spoofer can falsify the location signal but cannot simultaneously falsify the delivery platform's activity logs, cell tower placement, device motion sensors, and the statistical pattern of a coordinated ring.

**A genuine stranded worker will show:**
- Active delivery attempts on the platform in the hours leading up to the disruption
- Activity drop that coincides with the disruption trigger timestamp
- Cell tower placement in or near the claimed zone
- Natural GPS coordinate variance — not a perfectly static point
- Device accelerometer data consistent with being stationary outdoors

**A GPS spoofer will likely show:**
- No prior delivery activity on the platform that day (they never left home)
- Perfectly static GPS coordinates — a signature of software-generated location data
- Mismatch between GPS and cell tower placement
- GPS coordinates at the centroid of the alert zone rather than a realistic street address
- Multiple accounts sharing near-identical coordinates within the same hour
- A tight temporal spike where dozens of accounts trigger within minutes of each other

### 7.2 Data Points Analyzed Beyond GPS

| Signal | What It Reveals |
|---|---|
| Platform activity logs (2 hrs before event) | Whether the worker was actually on duty before the disruption |
| Cell tower triangulation | General area confirmation independent of GPS |
| GPS coordinate variance over time | Distinguishes natural movement from spoofed static coordinates |
| Device accelerometer readings | Confirms physical presence in a field environment |
| Spatial clustering (workers per 100m radius) | Flags coordinated rings — genuine disruptions do not cluster this tightly |
| Temporal clustering (claim spike width) | Coordinated fraud produces a narrow spike; genuine events produce a spread |
| Historical claim frequency vs. zone peers | Flags workers claiming disproportionately relative to peers in the same zone |

### 7.3 UX Balance: Flagged Claims Without Penalizing Honest Workers

A flagged claim is a held claim, not a denied claim.

| Confidence Score | Action | Worker Experience |
|---|---|---|
| High | Auto-approve and pay immediately | Payout notification within minutes, no action needed |
| Medium | Soft hold — 2 to 4 hour review window | Worker notified that the claim is processing; no action required |
| Low | Manual review, optional worker input | Worker receives a plain-language message explaining the uncertainty and can submit one supplementary data point within 24 hours |

**Handling legitimate network drops:** Poor connectivity during a storm is expected and is not treated as a suspicious signal. Claims are accepted retroactively within a 24-hour window for workers who were offline during the disruption.

Detection thresholds are calibrated to minimize false positives. The platform accepts that a small number of fraudulent claims may pass rather than routinely denying genuine ones.

## 8. Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python (FastAPI) |
| Database | PostgreSQL + Redis |
| ML / Scoring | scikit-learn, XGBoost |
| Frontend | React (worker portal + admin dashboard) |
| Worker Notifications | WhatsApp Business API (Twilio) |
| Disruption APIs | OpenWeatherMap, IMD Alerts (mock), CPCB AQI API |
| Payment | Razorpay test mode / UPI sandbox |
| Platform Data | Simulated mock API |
| Hosting | Railway (hackathon) |

## 9. Architecture

### 9.1 High-Level System Diagram

```
+-------------------+       +----------------------+       +------------------+
|   Worker App /    |       |   External Data       |       |  Admin Dashboard |
|   WhatsApp Bot    |       |   Sources             |       |                  |
+--------+----------+       +----------+-----------+       +--------+---------+
         |                             |                             |
         v                             v                             |
+--------+-----------------------------+-----------------------------+--------+
|                              API Gateway (FastAPI)                          |
+---+---------------------------+---------------------------+-----------------+
    |                           |                           |
    v                           v                           v
+---+----------+    +-----------+----------+    +----------+----------+
| Onboarding & |    | Disruption Monitor   |    | Admin Service        |
| Policy Svc   |    | (Trigger Engine)     |    | (Dashboard + Config) |
|              |    |                      |    |                      |
| - Risk score |    | - Polls APIs (5 min) |    | - Loss ratio view    |
| - Premium    |    | - Threshold check    |    | - Manual review queue|
| - Policy CRUD|    | - Fires claim events |    | - Threshold tuning   |
+---+----------+    +-----------+----------+    +---------------------+
    |                           |
    v                           v
+---+---------------------------+-------+
|         Claims Service                |
|                                       |
| - Receives claim event                |
| - Pulls worker platform activity data |
| - Runs fraud scoring model            |
| - Auto-approve / hold / review        |
| - Initiates payout on approval        |
+---+---------------------------+-------+
    |                           |
    v                           v
+---+---------+    +------------+-------+
| ML Service  |    | Payout Service     |
|             |    |                    |
| - Premium   |    | - Razorpay test    |
|   model     |    | - UPI sandbox      |
| - Fraud     |    | - Notification     |
|   scorer    |    +--------------------+
| - Trend     |
|   predictor |
+------+------+
       |
       v
+------+-------+
| PostgreSQL   |
| + Redis      |
+--------------+
```

### 9.2 Claim Flow

```
External API (Weather / AQI / Civic)
        |
        | Threshold breached
        v
Trigger Engine — identifies affected zones
        |
        v
Worker Lookup — all active workers in zone
        |
        v
Claims Service
        |
        +---> Platform activity logs (mock API)
        +---> Cell tower area (mock)
        +---> GPS variance from app session cache
        +---> Spatial cluster count for this trigger
        |
        v
Fraud Scoring Model — confidence score assigned
        |
   +----+----------+----------+
   |               |          |
 High           Medium       Low
   |               |          |
Auto-approve   Soft hold   Manual review
   |            (2-4 hrs)  + 24hr window
   v
Razorpay / UPI Sandbox
   |
   v
Worker notified via WhatsApp / App
```

## 10. Development Plan

**Phase 1 — Ideation & Foundation (Weeks 1–2, due March 20)**
- Define persona, zones, and disruption triggers
- Set up GitHub repository and project structure
- Build mock data layer: worker profiles, earnings, disruption events
- Implement basic onboarding flow with risk scoring and premium display
- Integrate OpenWeatherMap and CPCB AQI APIs
- Deliverable: This README + 2-minute strategy video

**Phase 2 — Automation & Protection (Weeks 3–4, due April 4)**
- Complete registration and policy management flows
- Implement dynamic premium calculation model
- Build trigger engine with 3–5 automated disruption monitors
- Implement claims service with fraud scoring
- Connect Razorpay test mode for simulated payouts
- Deliverable: Working prototype + 2-minute demo video

**Phase 3 — Scale & Optimize (Weeks 5–6, due April 17)**
- Refine fraud detection with spatial and temporal clustering
- Build admin dashboard with loss ratios and predictive disruption view
- Implement soft-hold and manual review workflow
- End-to-end test: simulate a disruption and verify full auto-claim-payout cycle
- Deliverable: Full platform + 5-minute demo video + pitch deck

## 11. Constraints & Exclusions

Coverage is limited to income lost during verified environmental disruptions (heavy rain, extreme heat, severe AQI, cyclone/flood alerts) and verified social disruptions (curfews, zone closures). Health costs, life insurance, accident compensation, and vehicle repair are excluded per the problem statement.

All premiums and payouts are structured on a weekly cycle. Delivery platform APIs are simulated for the hackathon. Payment integrations use test/sandbox modes only.

*Repository maintained by [CloudMax] for Guidewire DEVTrails 2026 University Hackathon.*

