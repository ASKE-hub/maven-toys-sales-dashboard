"""Create a static overview from validated aggregates, not a Power BI screenshot."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    summary = json.loads((ROOT / 'analysis/summary.json').read_text(encoding='utf-8'))
    monthly = pd.read_csv(ROOT / 'analysis/monthly.csv')
    categories = pd.read_csv(ROOT / 'analysis/categories.csv').sort_values('revenue_cents')
    locations = pd.read_csv(ROOT / 'analysis/locations.csv').sort_values('revenue_cents')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'maven-toys'})
    navy, teal, muted, grid = '#142B45', '#087F8C', '#60748A', '#E0E8EF'
    fig = plt.figure(figsize=(16, 10), facecolor='#F3F6FA')
    fig.text(.055, .94, 'MAVEN TOYS', fontsize=13, fontweight='bold', color=teal)
    fig.text(.055, .895, 'Sales performance overview', fontsize=30,
             fontweight='bold', color=navy)
    date_range = f"{summary['date_start']} to {summary['date_end']}"
    fig.text(.055, .858, f"{date_range}   /   {summary['stores']} stores   /   {summary['products']} products",
             fontsize=12, color=muted)
    cards = [('REVENUE', f"${summary['revenue_cents'] / 1e8:.2f}M"),
             ('GROSS PROFIT', f"${summary['profit_cents'] / 1e8:.2f}M"),
             ('GROSS MARGIN', f"{summary['gross_margin_pct']:.2f}%"),
             ('SALE RECORDS', f"{summary['transactions']:,}")]
    for i, (label, value) in enumerate(cards):
        x = .055 + i * .235
        ax = fig.add_axes([x, .71, .215, .105], facecolor='white')
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.text(.07, .72, label, transform=ax.transAxes, fontsize=10,
                color=muted, fontweight='bold')
        ax.text(.07, .21, value, transform=ax.transAxes, fontsize=28,
                color=navy, fontweight='bold')
    def style(ax, title):
        ax.set_facecolor('white')
        ax.set_title(title, loc='left', pad=18, color=navy, fontsize=14, fontweight='bold')
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.tick_params(colors=muted, length=0, pad=7)
        ax.set_axisbelow(True)
    trend = fig.add_axes([.065, .405, .88, .225])
    style(trend, 'Monthly revenue and gross profit')
    dates = pd.to_datetime(monthly.month)
    trend.plot(dates, monthly.revenue_cents / 1e8, color=teal, lw=2.5,
               marker='o', markersize=4, label='Revenue')
    trend.plot(dates, monthly.profit_cents / 1e8, color='#E19B35', lw=2.5,
               marker='o', markersize=4, label='Gross profit')
    trend.set_ylim(bottom=0)
    trend.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'${v:.1f}M'))
    trend.yaxis.set_major_locator(MaxNLocator(5, steps=[1, 2, 5, 10]))
    trend.grid(axis='y', color=grid)
    ticks = list(range(0, len(monthly), 3))
    if len(monthly)-1 not in ticks: ticks.append(len(monthly)-1)
    trend.set_xticks(dates.iloc[ticks], dates.iloc[ticks].dt.strftime('%b %y'))
    trend.legend(loc='upper left', frameon=False, ncols=2, fontsize=10)
    for left, width, data, key, title in [
        (.15, .36, categories, 'Product_Category', 'Revenue by product category'),
        (.665, .28, locations, 'Store_Location', 'Revenue by store location')]:
        ax = fig.add_axes([left, .105, width, .205])
        style(ax, title)
        bars = ax.barh(data[key], data.revenue_cents / 1e8, color=teal, height=.55)
        ax.set_xlim(0, max(data.revenue_cents / 1e8) * 1.23)
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'${v:.0f}M'))
        ax.xaxis.set_major_locator(MaxNLocator(4)); ax.grid(axis='x', color=grid)
        ax.bar_label(bars, labels=[f'${v / 1e8:.2f}M' for v in data.revenue_cents],
                     padding=7, fontsize=10, color=navy)
    fig.text(.055, .035,
             'Static analysis preview • Recomputed from the PBIX cached data • Gross profit excludes operating expenses',
             color=muted, fontsize=10)
    (ROOT / 'images').mkdir(exist_ok=True)
    fig.savefig(ROOT / 'images/sales-overview.svg', metadata={'Date': None}, facecolor=fig.get_facecolor())
    fig.savefig(ROOT / 'images/sales-overview.png', dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == '__main__':
    main()
