# Statistical Approach for Sanctions Termination Analysis

## Variable Overview

### Test 1
| Variable | Role | Type |
|---|---|---|
| `duration` | Dependent | Ordinal, 7 categories |
| `expiry` | Independent | Boolean (0/1) |
| `requirement_termination` | Independent | Boolean (0/1) |
| `review` | Independent | Boolean (0/1) |

### Test 2
| Variable | Role | Type |
|---|---|---|
| `outcome` | Dependent | Nominal, 3 categories |
| `expiry` | Independent | Boolean (0/1) |
| `requirement_termination` | Independent | Nominal, 2 categories |
| `review` | Independent | Boolean (0/1) |

### Test 3
| Variable | Role | Type |
|---|---|---|
| `duration` | Dependent | Ordinal, 7 categories |
| `gradual` | Independent | Boolean (0/1) |
| `negotiations` | Independent | Boolean (0/1) |

### Test 4
| Variable | Role | Type |
|---|---|---|
| `outcome` | Dependent | Nominal, 3 categories |
| `gradual` | Independent | Boolean (0/1) |
| `adaptation_goal` | Independent | Boolean (0/1) |
| `negotiations` | Independent | Boolean (0/1) |

### Test 5
| Variable | Role | Type |
|---|---|---|
| `outcome` | Dependent | Nominal, 3 categories |
| `multilateralism` | Independent | Boolean (0/1) |
| `duration` | Indipendent | Ordinal, 7 categories |
| `gradual` | Independent | Boolean (0/1) |

---

## 0. Preprocessing (completed)

- `outcome` collapsed to 3 categories: negotiated-settlement compounds
  merged into their single-outcome counterpart, thin standalone categories
  ("Negotiated settlement", "Stalemate") dropped.
- `multilateralism` recoded from raw multi-value combinations into a binary
  variable: **Unilateral** (single value per case) vs **Multilateral**
  (more than one value per case).
- This preprocessing is applied consistently across all descriptive tables
  and all inferential models below.

---

## 1. Descriptive Statistics

### Univariate — each variable in isolation

- Frequency tables (counts + percentages)
- Bar charts for visual inspection
- Flag rare categories before they propagate into thin cells downstream

### Bivariate — each independent variable crossed with the relevant DV

- Contingency tables (crosstabs) for each IV × DV pair
- Row/column percentages for conditional distributions
- These reveal raw patterns before formal testing

---

## 2. Inferential Tests

### Step 1 — Bivariate tests (each IV separately)

**For `outcome` (nominal DV, 3 categories):** Chi-square test of
independence (χ²) for each IV × outcome pair.

Report **Cramér's V** as effect size for each pair. It tells you how strong the association is, not just whether it's statistically significant

**For `duration` (ordinal DV, Tests 1 & 3):** 

**Cochran-Armitage trend test** for boolean IVs against ordinal
  duration. 

Report the test's own effect size (e.g. standardized z
converted to a trend correlation r).

**For `duration` as predictor (Test 5):** in the bivariate step, treat
`duration` as an ordinal grouping variable against `outcome` the same way
as the other nominal/boolean IVs (χ² + Cramér's V), since `outcome` is the
DV here.

### Step 2 — Multivariate Analysis (Joint Effects of All IVs)

This step estimates multivariate models in order to assess the joint effects of all relevant institutional variables while controlling for potential confounding and co-occurrence among predictors.

Before model estimation, a preliminary **collinearity assessment** is required due to evidence from bivariate analyses suggesting that several institutional features tend to co-occur (e.g., review, expiry, gradual termination, negotiations). This is important to avoid inflated standard errors and unstable coefficient estimates.

Recommended checks include:
- correlation matrix for binary predictors (phi / tetrachoric approximation if needed)
- variance inflation factors (VIF)
- inspection of pairwise co-occurrence patterns

---

#### 2.1 Multivariate Model for Outcome (Nominal DV)

Model type: **Multinomial Logistic Regression**

The dependent variable *outcome* is nominal and is modelled using a multinomial logit specification, with one category selected as reference.

Specification

All relevant IVs are entered simultaneously:

- expiry  
- review  
- req_termination  
- gradual  
- adapt_goal  
- negotiations  
- multilateralism  
- duration (see coding options below)

---

Duration (IV in outcome model)


Duration categories are coded as increasing integers (e.g., 1–6), assuming a monotonic relationship with the log-odds of outcome categories.

Use when:
- bivariate Step 1 suggests monotonic or near-monotonic trends
- interpretability as linear trend is substantively meaningful

---

Model interpretation

Coefficients are interpreted as:
> log-odds changes in outcome category membership relative to the reference outcome category, holding all other predictors constant.

Model fit should be evaluated using:
- AIC / BIC
- likelihood ratio tests
- pseudo-R² measures

---

#### 2.2 Multivariate Model for Duration (Temporal DV)

Model type: **Survival Analysis (Cox Proportional Hazards Model)**

Given that duration represents **time-to-event structure (interval-censored time spans)** rather than purely ordinal categories, survival analysis is the preferred modelling framework.

Rationale

Duration categories correspond to underlying continuous time intervals (e.g., 0–6 months up to 10–20 years), making the variable conceptually a discretised survival process rather than a purely ordinal scale.

---

Specification

The Cox proportional hazards model is estimated as:

- DV: time-to-termination (duration intervals)
- Event: termination occurrence (as defined in dataset)
- Predictors:

  - expiry  
  - review  
  - req_termination  
  - gradual  
  - negotiations  

---

Interpretation

Effects are expressed as hazard ratios:

- HR > 1 → increased hazard (shorter expected duration)
- HR < 1 → decreased hazard (longer expected duration)

---

Assumptions and diagnostics

Proportional hazards assumption:
Must be evaluated for each predictor.

Recommended diagnostics:
- Schoenfeld residual tests
- time-varying coefficient inspection

If violations are detected:
- consider stratified Cox models, or
- introduce time-dependent covariates

---

Optional fallback strategies

If survival modelling is not feasible due to data constraints:

1. **GLM on midpoint-coded duration (log-scale preferred)**
   - treats duration as approximately continuous

2. **Ordinal logistic regression**
   - least preferred; retains ordering but ignores temporal spacing

---

#### 2.3 Summary of modelling strategy

| DV | Nature | Preferred model |
|----|--------|----------------|
| outcome | nominal categorical | multinomial logit |
| duration | time-to-event (interval censored) | Cox proportional hazards |

---

Key methodological note

This step explicitly shifts the analysis from purely categorical inference to a **process-based representation of duration**, where time is treated as a structural outcome rather than an ordinal label.

This allows:

- separation of short vs long-term termination dynamics
- estimation of hazard effects of institutional design features
- more theoretically grounded interpretation of temporal structure

---



---

