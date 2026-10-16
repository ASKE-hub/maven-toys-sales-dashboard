# Open, refresh, and extend the Power BI report

## Open the current report

Download [Toys_Project.pbix](../Toys_Project.pbix) and open it in a current Windows version of Power BI Desktop. The file contains imported data, so its existing report can be viewed without first refreshing CSV sources. Use the Store Location slicer and category chart to explore the existing Dashboard page.

The repository upgrade adds a generated analysis preview and supporting resources. It does not alter the report's binary file or claim a native Desktop validation run.

## Refresh with source files

The four Power Query sources are **sales.csv**, **products.csv**, **stores.csv**, and **calendar.csv**. Their original queries point to a local folder on the author's machine, so they must be repointed on another computer.

1. Obtain the matching source files from your original project folder or [Maven Analytics Data Playground](https://mavenanalytics.io/data-playground). Check the dataset edition and dates: this cached model spans January 2022–September 2023.
2. In Desktop, open **Transform data**. For each query, edit its **Source** step to point to the corresponding CSV on your machine. Use **Data source settings → Change Source** where available.
3. Keep the exact field names and data types listed in the [model dictionary](data-model.md). Parse date and currency fields with a consistent locale rather than relying on the computer's default locale.
4. Confirm the calendar contains every sales date and no duplicate dates. For the existing snapshot it contains 638 daily rows.
5. Close & Apply, refresh, and compare unfiltered Card visuals with the [reference totals](../analysis/summary.json). New source data will legitimately change the totals.

The raw CSVs are not included in this repository. Python validation reads the cached PBIX tables directly, so no raw source download is needed for that workflow.

## Apply the included appearance upgrade

In Desktop choose **View → Themes → Browse for themes**, then import [themes/maven-toys.json](../themes/maven-toys.json). It supplies a navy/teal palette with amber for a secondary series. Existing explicit visual colors may override a theme; reset those colors to their defaults as needed.

Suggested layout for an executive overview:

1. A title and a clearly visible selected date range.
2. Cards for Total Revenue, Total Profit (displayed as Gross profit), Gross Margin %, and Total Orders (displayed as Sale records).
3. A monthly revenue/profit trend with chronological sorting and explicit units.
4. Revenue and margin by category, followed by a store-location comparison.
5. Date and Store Location slicers placed consistently, with descriptive visual titles and alt text.

Use a Card when the intended headline is the total for the selected period. The existing three KPI visuals include a trend axis and are designed around a point in that trend. Do not label an endpoint value as an all-period total. Do not add invented targets; the current model contains no target table.

The “(m)” / “(M)” measure names do not scale the values. Choose **Millions** in the visual's display units, or show full currency amounts, instead of assuming the formula divides by one million.

## Add the optional measures

Open [additional-measures.dax](../dax/additional-measures.dax) and create each definition separately with **New measure**. Keep the existing canonical `Total Revenue` and `Total Profit` measures. Format `Gross Margin %`, `Revenue MoM %`, and `Revenue YoY %` as percentages; format revenue/cost measures as currency.

Mark `calendar[Date]` as the date column before using time intelligence. Use month-level context for MoM and matching date selections for YoY. Keep selections contiguous when using these date-column formulas; `DATEADD` can error for disconnected date selections. The first available month/year has no earlier data and should return blank rather than a fabricated growth rate.

These optional formulas and the theme are provided as source resources. Their native Desktop import, filtering behavior, and appearance still need to be checked when applied.

## Native validation checklist

- [ ] No slicers: Cards match $14,444,572.35 revenue, $4,014,029.00 gross profit, and 829,262 sale records for the original snapshot.
- [ ] Downtown: revenue is $8,219,596.27; gross profit is $2,248,728.00.
- [ ] Electronics: revenue is $2,246,771.25; margin rounds to 44.57%.
- [ ] January–September 2023 versus the same dates in 2022: revenue growth rounds to 30.86%.
- [ ] Missing prior-period data shows blank; a zero denominator does not create infinity.
- [ ] Clearing all slicers restores the all-period totals.
- [ ] Labels, currency display units, keyboard order, and chart contrast remain readable.

## References

- [Microsoft: report themes](https://learn.microsoft.com/power-bi/create-reports/desktop-report-themes)
- [Microsoft: custom theme JSON](https://learn.microsoft.com/power-bi/create-reports/report-themes-create-custom)
- [Microsoft: KPI visuals](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-kpi)
- [Microsoft: DATEADD](https://learn.microsoft.com/en-us/dax/dateadd-function-dax)
