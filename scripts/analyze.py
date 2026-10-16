"""Rebuild portfolio evidence from the cached tables in Toys_Project.pbix.

Read-only: never refreshes, rewrites, or executes the Power BI model.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import zipfile

import pandas as pd


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def cents(values: pd.Series) -> pd.Series:
    def convert(value):
        number = Decimal(str(value)) * 100
        require(number.is_finite() and number == number.to_integral_value(),
                "Currency must be non-null and expressed in whole cents")
        return int(number)
    return values.map(convert).astype('int64')


def validate_key(frame: pd.DataFrame, key: str) -> None:
    require(frame[key].notna().all() and frame[key].is_unique,
            f"{key} must be unique and non-null")


def prepare(sales: pd.DataFrame, products: pd.DataFrame,
            stores: pd.DataFrame, calendar: pd.DataFrame) -> pd.DataFrame:
    for frame, key in [(sales, 'Sale_ID'), (products, 'Product_ID'),
                       (stores, 'Store_ID'), (calendar, 'Date')]:
        validate_key(frame, key)
    require(not sales.empty, 'Sales must not be empty')
    require(sales[['Date', 'Store_ID', 'Product_ID', 'Units']].notna().all().all(),
            'Sales contains missing required fields')
    require(((sales.Units > 0) & (sales.Units % 1 == 0)).all(),
            'Units must be positive integers')
    for key, dimension in [('Product_ID', products), ('Store_ID', stores), ('Date', calendar)]:
        require(sales[key].isin(dimension[key]).all(), f'Unmatched sales {key}')
    dates = pd.to_datetime(calendar.Date).sort_values().reset_index(drop=True)
    require((dates.diff().dropna() == pd.Timedelta(days=1)).all(),
            'Calendar must contain consecutive daily dates')
    require(products[['Product_Category', 'Product_Name']].notna().all().all(),
            'Missing product labels')
    require(stores[['Store_Location', 'Store_Name']].notna().all().all(),
            'Missing store labels')
    dim = products.copy()
    dim['unit_price_cents'] = cents(dim.Product_Price)
    dim['unit_cost_cents'] = cents(dim.Product_Cost)
    require((dim[['unit_price_cents', 'unit_cost_cents']] >= 0).all().all(),
            'Prices and costs must be non-negative')
    joined = sales.merge(dim, on='Product_ID', validate='many_to_one').merge(
        stores, on='Store_ID', validate='many_to_one')
    joined['revenue_cents'] = joined.Units.astype('int64') * joined.unit_price_cents
    joined['cost_cents'] = joined.Units.astype('int64') * joined.unit_cost_cents
    joined['profit_cents'] = joined.revenue_cents - joined.cost_cents
    require((cents(joined.Revenue) == joined.revenue_cents).all(),
            'Stored Revenue differs from Units x Product_Price')
    require((cents(joined.Profit) == joined.profit_cents).all(),
            'Stored Profit differs from Revenue - Units x Product_Cost')
    require((cents(joined.Price) == joined.unit_price_cents).all(),
            'Stored Price differs from Product_Price')
    require((cents(joined.Cost) == joined.unit_cost_cents).all(),
            'Stored Cost differs from Product_Cost')
    joined['month'] = pd.to_datetime(joined.Date).dt.strftime('%Y-%m')
    return joined


def aggregate(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    result = frame.groupby(key, observed=True).agg(
        transactions=('Sale_ID', 'nunique'), units=('Units', 'sum'),
        revenue_cents=('revenue_cents', 'sum'), cost_cents=('cost_cents', 'sum'),
        profit_cents=('profit_cents', 'sum')).reset_index()
    denominator = result.revenue_cents.replace(0, float('nan'))
    result['gross_margin_pct'] = (100 * result.profit_cents / denominator).round(4)
    require(int(result.revenue_cents.sum()) == int(frame.revenue_cents.sum()),
            f'{key} revenue does not reconcile')
    require(int(result.profit_cents.sum()) == int(frame.profit_cents.sum()),
            f'{key} profit does not reconcile')
    require(int(result.transactions.sum()) == len(frame), f'{key} count does not reconcile')
    return result


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n',
                    encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pbix', type=Path, default=Path('Toys_Project.pbix'))
    parser.add_argument('--output', type=Path, default=Path('analysis'))
    args = parser.parse_args()
    from pbixray import PBIXRay

    model = PBIXRay(str(args.pbix))
    names = ['sales', 'products', 'stores', 'calendar']
    tables = {name: model.get_table(name) for name in names}
    sales = prepare(**tables)
    args.output.mkdir(parents=True, exist_ok=True)
    groups = {}
    for filename, key in [('monthly', 'month'), ('categories', 'Product_Category'),
                          ('locations', 'Store_Location'), ('stores', 'Store_Name')]:
        grouped = aggregate(sales, key)
        groups[filename] = grouped
        grouped.to_csv(args.output / (filename + '.csv'), index=False, lineterminator='\n')
    total_revenue = int(sales.revenue_cents.sum())
    total_profit = int(sales.profit_cents.sum())
    summary = {
        'source_file': args.pbix.name,
        'source_sha256': hashlib.sha256(args.pbix.read_bytes()).hexdigest(),
        'date_start': str(sales.Date.min().date()), 'date_end': str(sales.Date.max().date()),
        'transactions': len(sales), 'units': int(sales.Units.sum()),
        'products': len(tables['products']), 'stores': len(tables['stores']),
        'categories': int(tables['products'].Product_Category.nunique()),
        'revenue_cents': total_revenue, 'cost_cents': int(sales.cost_cents.sum()),
        'profit_cents': total_profit,
        'gross_margin_pct': round(total_profit / total_revenue * 100, 4) if total_revenue else None,
        'currency_note': 'Dollar-denominated dataset values; no currency conversion.',
        'checks': {
            'unique_non_null_keys': True, 'complete_foreign_keys': True,
            'consecutive_calendar': True, 'positive_integer_units': True,
            'stored_revenue_matches_recalculation': True,
            'stored_profit_matches_recalculation': True,
            'stored_unit_price_and_cost_match_products': True,
            'all_group_totals_reconcile': True,
        },
    }
    write_json(args.output / 'summary.json', summary)
    with zipfile.ZipFile(args.pbix) as archive:
        layout = json.loads(archive.read('Report/Layout').decode('utf-16-le'))
    visuals = []
    for page in layout['sections']:
        for visual in page.get('visualContainers', []):
            config = json.loads(visual['config']).get('singleVisual', {})
            visuals.append({'page': page['displayName'], 'type': config.get('visualType'),
                            'fields': config.get('projections', {})})
    def records(frame):
        return json.loads(frame.to_json(orient='records', date_format='iso'))
    metadata = {
        'tables': {name: len(frame) for name, frame in tables.items()},
        'schema': records(model.schema[model.schema.TableName.isin(names)]),
        'relationships': records(model.relationships),
        'measures': records(model.dax_measures),
        'calculated_columns': records(model.dax_columns[model.dax_columns.TableName.isin(names)]),
        'visuals': visuals,
        'power_query_sources': ['calendar.csv', 'products.csv', 'sales.csv', 'stores.csv'],
    }
    write_json(args.output / 'model.json', metadata)
    print(json.dumps(summary, indent=2))
    print(groups['categories'].to_string(index=False))
    print(groups['locations'].to_string(index=False))
    print(groups['monthly'].to_string(index=False))


if __name__ == '__main__':
    main()
