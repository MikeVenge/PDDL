# Extracted PDDL Action Steps from Warrant Analysis Framework

## Overview
This document contains the extracted action steps from the PDDL-style plan for analyzing U.S. listed company warrants (2022-2025).

## Domain Definition
- **Domain**: warrant-analysis
- **Requirements**: :typing :negative-preconditions

## Action Steps

### 1. Collect SEC Filings
```pddl
(:action collect-sec-filings
    :parameters (?c - company ?w - warrant)
    :precondition (and (not (has-data ?c ?w)))
    :effect (has-data ?c ?w)
)
```
**Purpose**: Pull all 10-K, 10-Q, and 8-K filings that mention "warrants" for each U.S. public company.

**Details**:
- **Parameters**: 
  - `?c` - company entity
  - `?w` - warrant entity
- **Precondition**: Data has not been collected for this company-warrant pair
- **Effect**: Marks the data as collected for the company-warrant pair

---

### 2. Fetch Market Data
```pddl
(:action fetch-market-data
    :parameters (?c - company ?w - warrant)
    :precondition (has-data ?c ?w)
    :effect (and
        (market-price ?c (calc-market-price ?c))
        (strike-price ?w (calc-strike-price ?w))
        (expiration ?w (calc-expiration ?w))
    )
)
```
**Purpose**: Pull current and historical stock prices, strike prices, and expiration dates from Bloomberg/Refinitiv.

**Details**:
- **Parameters**: 
  - `?c` - company entity
  - `?w` - warrant entity
- **Precondition**: SEC filing data has been collected
- **Effects**: 
  - Calculates and stores market price for the company
  - Calculates and stores strike price for the warrant
  - Calculates and stores expiration date for the warrant

---

### 3. Compute Metrics
```pddl
(:action compute-metrics
    :parameters (?w - warrant)
    :precondition (and
        (strike-price ?w ?sp)
        (market-price ?c ?mp)          ; underlying company
        (expiration ?w ?exp)
    )
    :effect (and
        (exercise-rate ?w (calc-exercise-rate ?w))
        (liquidity ?w (calc-liquidity ?w))
        (volatility ?w (calc-volatility ?w))
        (return ?w (calc-annualized-return ?w))
    )
)
```
**Purpose**: Calculate key financial metrics including exercise rate, liquidity (average daily volume), volatility, and annualized return for each warrant.

**Details**:
- **Parameters**: 
  - `?w` - warrant entity
- **Preconditions**: 
  - Strike price is defined for the warrant
  - Market price is defined for the underlying company
  - Expiration date is defined for the warrant
- **Effects**: 
  - Calculates exercise rate
  - Calculates liquidity metrics
  - Calculates volatility
  - Calculates annualized return

---

### 4. Sector Aggregation
```pddl
(:action sector-aggregation
    :parameters (?sec - string)
    :precondition (forall (?c - company) (sector ?c ?sec))
    :effect (and
        (total-warrants ?sec (sum ?w (has-data ?c ?w)))
        (avg-strike-vs-price ?sec (avg (ratio ?sp ?mp)))
        (avg-expiration-years ?sec (avg (years-to-exp ?exp)))
    )
)
```
**Purpose**: Summarize total face value, average moneyness, average time-to-expiration, and sector-specific trends.

**Details**:
- **Parameters**: 
  - `?sec` - sector string identifier
- **Precondition**: All companies in the sector have been classified
- **Effects**: 
  - Aggregates total warrants for the sector
  - Calculates average strike-to-market price ratio
  - Calculates average years to expiration

---

### 5. Generate Report
```pddl
(:action generate-report
    :parameters ()
    :precondition (and
        (forall (?w - warrant) (return ?w ?r))
        (forall (?sec - string) (total-warrants ?sec ?t))
    )
    :effect (report (compose
        (summary-by-sector)
        (top-issuers-list)
        (risk-matrix)
        (investment-guidelines)
    ))
)
```
**Purpose**: Generate the final comprehensive analysis report.

**Details**:
- **Parameters**: None
- **Preconditions**: 
  - All warrant returns have been calculated
  - All sector totals have been aggregated
- **Effect**: Produces a report containing:
  - Executive summary with overall market size, growth, and sector breakdown
  - List of top issuers with their warrant structures
  - Risk matrix covering dilution, liquidity, and expiration risks
  - Investment guidelines for screening attractive warrants

---

## Execution Sequence

The actions should be executed in the following order to ensure all preconditions are met:

1. **collect-sec-filings** → Gather raw data from SEC filings
2. **fetch-market-data** → Obtain market pricing information
3. **compute-metrics** → Calculate financial metrics for each warrant
4. **sector-aggregation** → Aggregate data by sector
5. **generate-report** → Compile final analysis report

## Supporting Types and Predicates

### Types
- `company` - Company entities
- `security` - Security instruments
- `warrant` - Warrant instruments
- `data_source` - Data source entities
- `analysis_step` - Analysis process steps

### Key Predicates
- `(has-data ?c ?w)` - Data availability flag
- `(strike-price ?w ?price)` - Warrant strike price
- `(market-price ?c ?price)` - Company market price
- `(expiration ?w ?date)` - Warrant expiration date
- `(exercise-rate ?w ?pct)` - Warrant exercise rate
- `(liquidity ?w ?vol)` - Warrant liquidity volume
- `(volatility ?w ?vol)` - Warrant volatility measure
- `(return ?w ?annualized)` - Warrant annualized return
