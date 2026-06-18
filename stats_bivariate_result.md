# Bivariate Inferential Analysis

The analysis comprises two families of tests:

1. **Cochran–Armitage trend tests**
   - Dependent variable (DV): sanction duration (ordinal)
   - Independent variable (IV): binary feature (present/absent)
   - Evaluates whether the proportion of a feature changes systematically across ordered duration categories.

2. **Chi-square tests of independence with Cramér's V**
   - Dependent variable (DV): termination outcome (nominal)
   - Evaluates whether two categorical variables are associated.
   - Cramér's V is reported as a measure of effect size.

---

# Duration Analyses (Cochran–Armitage Trend Test)

## Expiry × Duration

| Statistic | Value |
|------------|--------|
| z | 3.12 |
| p | 0.0018 |
| r | 0.157 |

The test indicates a statistically significant positive trend.

**Interpretation:**  
Sanctions including an expiry clause tend to be associated with longer sanction durations. The effect size is small.

---

## Review × Duration

| Statistic | Value |
|------------|--------|
| z | 3.86 |
| p | < 0.001 |
| r | 0.196 |

The test indicates a statistically significant positive trend.

**Interpretation:**  
Sanctions including review mechanisms are more common among longer-lasting sanctions. The effect size is small to moderate.

---

## Requested Termination × Duration

| Statistic | Value |
|------------|--------|
| z | -2.55 |
| p | 0.011 |
| r | 0.129 |

The test indicates a statistically significant negative trend.

**Interpretation:**  
Requested termination mechanisms appear more frequently among shorter-duration sanctions. The effect size is small.

---

## Gradual × Duration

| Statistic | Value |
|------------|--------|
| z | -9.55 |
| p | < 0.000001 |
| r | 0.479 |

This is the strongest result among the duration analyses.

**Interpretation:**  
Gradual termination mechanisms are strongly associated with sanction duration. Gradual termination appears substantially more common among shorter sanctions. The effect size is large.


---

## Negotiations × Duration

| Statistic | Value |
|------------|--------|
| z | -2.66 |
| p | 0.0079 |
| r | 0.133 |

The test indicates a statistically significant negative trend.

**Interpretation:**  
Negotiated endings appear somewhat more common among shorter-duration sanctions. The effect size is small.

---

# Outcome Analyses (Chi-square Tests)

The following conventional guidelines may be used for interpreting Cramér's V:

| Cramér's V | Interpretation |
|------------|---------------|
| 0.10 | Small |
| 0.30 | Medium |
| 0.50 | Large |

These thresholds should be considered approximate and context-dependent.

---

## Expiry × Outcome

| χ² | p | V |
|----|---|---|
| 7.58 | 0.023 | 0.172 |

**Interpretation:**  
Termination outcomes differ significantly depending on whether sanctions contain an expiry provision. The effect size is small.

---

## Review × Outcome

| χ² | p | V |
|----|---|---|
| 2.19 | 0.334 | 0.093 |

**Interpretation:**  
No statistically significant association was found between review mechanisms and termination outcomes.

---

## Requested Termination × Outcome

| χ² | p | V |
|----|---|---|
| 0.45 | 0.797 | 0.042 |

**Interpretation:**  
No statistically significant association was found between requested termination mechanisms and termination outcomes.

---

## Gradual × Outcome

| χ² | p | V |
|----|---|---|
| 9.97 | 0.0068 | 0.196 |

**Interpretation:**  
Gradual termination mechanisms are associated with differences in termination outcomes. The effect size is small to moderate.

---

## Adapt Goal × Outcome

| χ² | p | V |
|----|---|---|
| 9.60 | 0.0082 | 0.193 |

**Interpretation:**  
Goal adaptation is associated with differences in termination outcomes. The effect size is small to moderate.

---

## Negotiations × Outcome

| χ² | p | V |
|----|---|---|
| 0.28 | 0.870 | 0.033 |

**Interpretation:**  
No statistically significant association was found between negotiations and termination outcomes.

---

## Multilateralism × Outcome

| χ² | p | V |
|----|---|---|
| 40.58 | < 0.00000001 | 0.395 |

This is the strongest result among the outcome analyses.

**Interpretation:**  
Termination outcomes differ substantially between multilateral and non-multilateral sanctions. The effect size is moderate to large and likely reflects a substantively important relationship.

---

## Duration × Outcome

| χ² | p | V |
|----|---|---|
| 23.60 | 0.0087 | 0.216 |

**Interpretation:**  
Termination outcomes vary significantly across sanction duration categories. The effect size is small to moderate.

Because duration is an ordinal variable, the chi-square test treats duration only as categorical. More specialized ordinal methods could potentially capture additional structure in the relationship.

---

# Overall Pattern of Results

The strongest findings are:

1. **Gradual termination × Duration**
   - Strongest association in the study.
   - Large effect size (*r* ≈ 0.48).

2. **Multilateralism × Outcome**
   - Strongest association involving termination outcomes.
   - Moderate-to-large effect size (*V* ≈ 0.40).

3. **Duration × Outcome**
   - Meaningful association between sanction duration and termination outcomes.
   - Moderate effect size (*V* ≈ 0.22).

4. **Expiry clauses, review mechanisms, and goal adaptation**
   - Consistent statistically significant associations.
   - Generally small-to-moderate effect sizes.

5. **Requested termination and negotiations**
   - Associated with sanction duration.
   - Not associated with termination outcomes.

---

# Multiple Testing Considerations

A total of **13 hypothesis tests** were conducted.

Applying a Bonferroni correction yields:

\[
\alpha = \frac{0.05}{13} \approx 0.0038
\]

Under this more conservative threshold, the following findings remain clearly significant:

- Expiry × Duration
- Review × Duration
- Gradual × Duration
- Multilateralism × Outcome

Several other associations that are significant at the conventional 0.05 level would no longer meet the corrected threshold.

For publication-quality reporting, it is advisable to supplement raw p-values with either:

- **Holm–Bonferroni adjusted p-values**, or
- **Benjamini–Hochberg false discovery rate (FDR) adjusted p-values**.

These procedures provide stronger control for the increased risk of Type I errors arising from multiple comparisons.