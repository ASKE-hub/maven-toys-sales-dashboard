# Findings and business interpretation

All figures below come from the cached tables in `Toys_Project.pbix`, with no slicers applied. They are descriptive findings from a fictional practice dataset, not measured outcomes of business interventions.

## 1. Revenue growth outpaced profit growth

Compare the same nine months in each year; 2023 stops at September.

| January–September | 2022 | 2023 | Change |
| --- | ---: | ---: | ---: |
| Revenue | $5,320,115.85 | $6,962,074.27 | +30.86% |
| Gross profit | $1,572,037.00 | $1,824,242.00 | +16.04% |
| Gross margin | 29.55% | 26.20% | −3.35 percentage points |
| Sale records | 297,055 | 408,417 | +111,362 |

**Interpretation:** revenue expanded, but each revenue dollar generated less gross profit. Investigate changes in the mix of products and categories. The model contains one cost and price per product rather than historical price records, so it cannot establish a history of price changes or discounts.

**Next analysis:** decompose the margin change into product/category mix effects. Track revenue and margin together; a revenue-only target can obscure the trade-off.

Source: [monthly.csv](../analysis/monthly.csv). Growth = current / previous − 1. Margin = total gross profit / total revenue, not the average of monthly margins.

## 2. Category revenue and margin tell different stories

| Category | Revenue | Gross profit | Gross margin |
| --- | ---: | ---: | ---: |
| Toys | $5,093,241.00 | $1,079,527.00 | 21.20% |
| Art & Crafts | $2,705,364.26 | $753,354.00 | 27.85% |
| Electronics | $2,246,771.25 | $1,001,437.00 | 44.57% |
| Games | $2,226,836.27 | $673,993.00 | 30.27% |
| Sports & Outdoors | $2,172,359.57 | $505,718.00 | 23.28% |

Toys provides 35.26% of revenue. Electronics produces nearly as much gross profit as Toys from less than half its revenue. A useful follow-up is product-level assortment analysis, including demand and inventory constraints before making stocking decisions.

Source: [categories.csv](../analysis/categories.csv).

## 3. Downtown is the largest revenue contributor

Downtown stores generate $8,219,596.27 in revenue, or 56.90% of the total, and $2,248,728.00 in gross profit. This is a contribution measure, not a store-efficiency ranking: the groups contain different numbers of stores and may have different trading histories.

**Next analysis:** compare like-for-like stores, normalize revenue by active store-days, and check category mix by location. The [store aggregates](../analysis/stores.csv) support an initial store-level comparison.

Source: [locations.csv](../analysis/locations.csv).

## Interpretation limits

- `Sale_ID` identifies a sale record. It does not establish a multi-item customer order, unique customer, or basket.
- Gross profit deducts product cost only. Rent, staff, tax, delivery, and other operating expenses are absent.
- There are no inventory or customer tables in this PBIX. Stockout, retention, customer acquisition cost, and customer lifetime value claims would be unsupported.
- The source uses dollar amounts. No exchange-rate conversion has been applied.
- Compare matching periods. Do not compare nine months of 2023 with all twelve months of 2022 as a year-over-year growth rate.
- These totals use all cached rows. Interactive filters and monthly KPI callouts can produce different values.
