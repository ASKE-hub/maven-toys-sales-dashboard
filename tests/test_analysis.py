"""Small independent fixtures exercise failures that could distort portfolio KPIs."""
import sys
from pathlib import Path
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from analyze import aggregate, prepare


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.products = pd.DataFrame({
            'Product_ID': [1, 2], 'Product_Name': ['A', 'B'],
            'Product_Category': ['Toys', 'Games'],
            'Product_Price': ['0.30', '2.50'], 'Product_Cost': ['0.10', '1.00']})
        self.stores = pd.DataFrame({'Store_ID': [1], 'Store_Name': ['Test'],
                                    'Store_Location': ['Downtown']})
        self.calendar = pd.DataFrame({'Date': pd.date_range('2023-01-01', periods=2)})
        self.sales = pd.DataFrame({
            'Sale_ID': [1, 2], 'Date': pd.date_range('2023-01-01', periods=2),
            'Store_ID': [1, 1], 'Product_ID': [1, 2], 'Units': [3, 2],
            'Price': ['0.30', '2.50'], 'Cost': ['0.10', '1.00'],
            'Revenue': ['0.90', '5.00'], 'Profit': ['0.60', '3.00']})

    def build(self):
        return prepare(self.sales, self.products, self.stores, self.calendar)

    def test_currency_and_weighted_margin(self):
        frame = self.build()
        result = aggregate(frame, 'month').iloc[0]
        self.assertEqual(int(result.revenue_cents), 590)
        self.assertEqual(int(result.profit_cents), 360)
        self.assertEqual(int(result.units), 5)
        self.assertAlmostEqual(result.gross_margin_pct, 100 * 360 / 590, places=4)

    def test_duplicate_dimension_key_rejected(self):
        self.products = pd.concat([self.products, self.products.iloc[[0]]])
        with self.assertRaisesRegex(ValueError, 'Product_ID must be unique'):
            self.build()

    def test_unmatched_product_rejected(self):
        self.sales.loc[0, 'Product_ID'] = 99
        with self.assertRaisesRegex(ValueError, 'Unmatched sales Product_ID'):
            self.build()

    def test_corrupt_stored_profit_rejected(self):
        self.sales.loc[0, 'Profit'] = '0.61'
        with self.assertRaisesRegex(ValueError, 'Stored Profit differs'):
            self.build()

    def test_duplicate_sale_rejected(self):
        self.sales.loc[1, 'Sale_ID'] = 1
        with self.assertRaisesRegex(ValueError, 'Sale_ID must be unique'):
            self.build()

    def test_missing_calendar_day_rejected(self):
        self.calendar = pd.DataFrame({'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-04'])})
        with self.assertRaisesRegex(ValueError, 'consecutive daily dates'):
            self.build()

    def test_zero_revenue_has_no_margin(self):
        self.products['Product_Price'] = '0.00'
        self.products['Product_Cost'] = '0.00'
        self.sales[['Price', 'Cost', 'Revenue', 'Profit']] = '0.00'
        result = aggregate(self.build(), 'month')
        self.assertTrue(result.gross_margin_pct.isna().all())

    def test_missing_units_rejected(self):
        self.sales.loc[0, 'Units'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'missing required fields'):
            self.build()


if __name__ == '__main__':
    unittest.main()
