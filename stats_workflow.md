# Statistical Approach for Sanctions Termination Analysis

## Variable Overview

| Variable | Role | Type |
|---|---|---|
| `outcome_type` | Dependent | Nominal, 5 unordered categories |
| `expiry` | Independent | Boolean (0/1) |
| `requirement_termination` | Independent | Nominal, 2 unordered categories |
| `review` | Independent | Boolean (0/1) |

---

## 1. Descriptive Statistics

Before any inferential test, describe your data thoroughly.

### Univariate — each variable in isolation

For each of the 4 variables:

- **Frequency tables** (counts + percentages)
- **Bar charts** for visual inspection
- **Check for rare categories** — cells with very low counts will affect test validity later

### Bivariate — each independent variable crossed with `outcome_type`

- **Contingency tables (crosstabs)** for each pair:
  - `expiry × outcome_type`
  - `requirement_termination × outcome_type`
  - `review × outcome_type`
- **Row/column percentages** to show conditional distributions
- These reveal the raw patterns before any formal testing

---

## 2. Inferential Tests

### Step 1 — Bivariate tests (each IV separately)

Use a **Chi-square test of independence (χ²)** for each pair.

Since both boolean IVs produce 2×5 contingency tables and the nominal IV also produces a 2×5 table, chi-square is appropriate throughout.

> **Critical assumption to check:** no more than 20% of cells should have an expected frequency < 5.
> If this assumption is violated, use **Fisher's Exact Test** instead (computationally heavier, but exact for small-cell situations).

Report **Cramér's V** as the effect size for each χ² result — it is directly interpretable for nominal variables regardless of table dimensions.

### Step 2 — Multivariate test (all IVs together)

Chi-square only handles two variables at a time. To assess the joint effect of all three IVs on `outcome_type`, use one of the following:

| Method | When to use | Pros | Cons |
|---|---|---|---|
| **Multinomial Logistic Regression** | Your primary choice | Handles all IVs simultaneously, produces odds ratios, controls for confounding | Requires sufficient N per category combination |
| **Log-linear models** | If you want symmetric modelling of all associations | Very flexible | Harder to interpret |

**Multinomial logistic regression** is almost certainly the right choice here. It directly models the probability of each `outcome_type` category as a function of your three predictors, treating one outcome category as the reference. It answers whether each IV has a significant effect *net of the others*.

---

## 3. Key Assumptions to Verify

- **Sample size**: multinomial logit needs roughly 10–20 observations per outcome category per predictor combination — check your cell counts early
- **Independence of observations**: each case should appear only once — your schema suggests this is satisfied
- **No perfect separation**: no predictor should perfectly predict one outcome category

---

## 4. Recommended Workflow

1. Frequency tables → identify thin cells
2. Crosstabs + χ² for each IV × `outcome_type`
3. Cramér's V as effect size for each χ² result
4. Multinomial logistic regression with all three IVs entered simultaneously
5. Report pseudo-R² (McFadden or Nagelkerke) + likelihood ratio test for overall model fit
