# Validation and reproducibility

## What was checked

The audit reads the four business tables from the committed Power BI file using [PBIXRay](https://github.com/Hugoberry/pbixray). It executes no DAX, Power Query, or source refresh.

For the current snapshot, every check in [summary.json](../analysis/summary.json) passes:

- Unique, non-null primary keys in all four tables.
- Every sales product, store, and date key exists in its dimension.
- No missing required sales fields; Units is a positive integer.
- The calendar contains consecutive dates.
- Stored unit Price and Cost match the products dimension.
- All 829,262 stored Revenue and Profit values match independent calculations using integer cents.
- Revenue, profit, and record counts reconcile across each monthly, category, location, and store aggregation.

Eight independent synthetic-fixture tests cover currency precision and weighted margins, duplicate product and sale keys, an unmatched product, corrupted stored profit, a missing calendar day, missing units, and zero-revenue margin behavior. A zero-revenue margin is undefined and is represented as missing, not zero.

## Run

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/analyze.py
python scripts/render_preview.py
```

`analyze.py` overwrites only generated files in `analysis/`; `render_preview.py` overwrites the two preview images. Neither modifies `Toys_Project.pbix`. Run from the repository root. Verified locally with Python 3.13, PBIXRay 0.15.5, pandas 3.0.6, and Matplotlib 3.10.6.

The [GitHub Actions workflow](../.github/workflows/validate.yml) repeats the tests, full PBIX audit, and preview generation on pushes and pull requests. It fails if regenerated analysis files differ from the committed evidence. The Power BI theme was separately validated against Microsoft's report-theme JSON schema 2.159; native Desktop import remains a separate check.

The analysis exports metadata and aggregates, not raw sale rows or machine-specific CSV source paths. `summary.json` records the source SHA-256 so the evidence can be tied to an exact PBIX version. Compare that hash after downloading a different report revision.

## Scope of assurance

The successful checks establish consistency of the cached tables, stored arithmetic, and published aggregate outputs. They do not establish that the source dataset reflects a real business, that refreshed data will match the old snapshot, or that optional new DAX measures have executed in Microsoft's engine. The PBIX was not opened or modified in Power BI Desktop during this repository upgrade.

The SVG/PNG preview is generated with Matplotlib and was visually reviewed. It is a separate static analysis view, not an export of the current Power BI page. See the separate [Desktop checklist](power-bi-guide.md#native-validation-checklist) for native report validation.
