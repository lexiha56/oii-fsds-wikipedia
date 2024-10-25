# Save this as wiki_time_plots.py (using underscores instead of hyphens)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Module-level configuration
DEFAULT_FIGSIZE = (15, 18)
DEFAULT_DPI = 300

def set_plot_style():
    """Set consistent plot style."""
    sns.set_theme(style="whitegrid")
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"]
    sns.set_palette(colors)

def load_and_process_data(feather_path):
    """Load data from feather file and ensure proper datetime format."""
    df = pd.read_feather(feather_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def load_wiki_data(feather_path):
    """
    Load Wikipedia revision data from a feather file.
    
    Parameters:
    -----------
    feather_path : str or Path
        Path to the feather file containing Wikipedia revision data
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with processed timestamp column
    """
    df = pd.read_feather(feather_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def plot_revision_counts(df, article_name, output_dir=None, moving_average=False):
    """
    Create revision count plots either with or without moving averages.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing Wikipedia revision data
    article_name : str
        Name of the article for plot titles
    output_dir : str or Path, optional
        Directory to save the plot
    moving_average : bool, default=False
        Whether to include moving averages in the plots
    
    Returns:
    --------
    matplotlib.figure.Figure
        The generated figure object
    """
    if moving_average:
        return create_time_series_plots_with_ma(df, article_name, output_dir)
    else:
        return create_time_series_plots_raw(df, article_name, output_dir)

def create_time_series_plots_raw(df, article_name, output_dir=None):
    """Create three time series plots showing raw counts at different time scales."""
    set_plot_style()
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=DEFAULT_FIGSIZE)
    fig.suptitle(f'Revision Activity for {article_name}', fontsize=16, y=0.95)
    
    # Weekly plot
    weekly_counts = df.resample('W', on='timestamp')['revision_id'].count()
    ax1.plot(weekly_counts.index, weekly_counts.values)
    ax1.set_title('Weekly Revision Count')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number of Revisions')
    
    # Monthly plot
    monthly_counts = df.resample('ME', on='timestamp')['revision_id'].count()
    ax2.plot(monthly_counts.index, monthly_counts.values)
    ax2.set_title('Monthly Revision Count')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Number of Revisions')
    
    # Yearly plot
    yearly_counts = df.resample('YE', on='timestamp')['revision_id'].count()
    ax3.plot(yearly_counts.index, yearly_counts.values)
    ax3.set_title('Yearly Revision Count')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Number of Revisions')
    
    # Add statistics
    stats_text = (
        f"Total Revisions: {len(df):,}\n"
        f"Time Range: {df['timestamp'].min().year} to {df['timestamp'].max().year}\n"
        f"Peak Weekly: {weekly_counts.max():,.0f} revisions\n"
        f"Peak Monthly: {monthly_counts.max():,.0f} revisions\n"
        f"Peak Yearly: {yearly_counts.max():,.0f} revisions"
    )
    plt.figtext(0.02, 0.02, stats_text, fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.8))
    
    # Adjust layout
    plt.tight_layout()
    
    # Save if output directory is provided
    if output_dir:
        output_path = Path(output_dir) / f"{article_name}_revision_activity_raw.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_path}")
    
    return fig

def create_time_series_plots_with_ma(df, article_name, output_dir=None):
    """Create three time series plots with moving averages."""
    set_plot_style()
        
    # Create figure
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 18))
    fig.suptitle(f'Revision Activity for {article_name}\nwith Moving Averages', fontsize=16, y=0.95)
    
    # Weekly plot with 4-week moving average
    weekly_counts = df.resample('W', on='timestamp')['revision_id'].count()
    weekly_ma = weekly_counts.rolling(window=4, center=True, min_periods=3).mean()
    
    ax1.plot(weekly_counts.index, weekly_counts.values, alpha=0.4, label='Weekly Count')
    ax1.plot(weekly_ma.index, weekly_ma.values, linewidth=2, label='4-Week Moving Average')
    ax1.set_title('Weekly Revision Count with 4-Week Moving Average')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number of Revisions')
    ax1.legend()
    
    # Monthly plot with 3-month moving average
    monthly_counts = df.resample('ME', on='timestamp')['revision_id'].count()
    monthly_ma = monthly_counts.rolling(window=3, center=True, min_periods=2).mean()
    
    ax2.plot(monthly_counts.index, monthly_counts.values, alpha=0.4, label='Monthly Count')
    ax2.plot(monthly_ma.index, monthly_ma.values, linewidth=2, label='3-Month Moving Average')
    ax2.set_title('Monthly Revision Count with 3-Month Moving Average')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Number of Revisions')
    ax2.legend()
    
    # Yearly plot with 2-year moving average
    yearly_counts = df.resample('YE', on='timestamp')['revision_id'].count()
    yearly_ma = yearly_counts.rolling(window=2, center=True, min_periods=2).mean()
    
    ax3.plot(yearly_counts.index, yearly_counts.values, alpha=0.4, label='Yearly Count')
    ax3.plot(yearly_ma.index, yearly_ma.values, linewidth=2, label='2-Year Moving Average')
    ax3.set_title('Yearly Revision Count with 2-Year Moving Average')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Number of Revisions')
    ax3.legend()
    
       # Add statistics and trend analysis
    stats_text = (
        f"Total Revisions: {len(df):,}\n"
        f"Time Range: {df['timestamp'].min().year} to {df['timestamp'].max().year}\n"
        f"Peak Weekly MA: {weekly_ma.max():,.0f} revisions\n"
        f"Peak Monthly MA: {monthly_ma.max():,.0f} revisions\n"
        f"Peak Yearly MA: {yearly_ma.max():,.0f} revisions"
    )
    plt.figtext(0.02, 0.02, stats_text, fontsize=10, 
                bbox=dict(facecolor='white', alpha=0.8))
    
    # Add trend analysis
    def get_trend_description(start_val, end_val):
        if pd.isna(start_val) or pd.isna(end_val):
            return "Insufficient Data"
        change = (end_val - start_val) / start_val * 100
        if change > 20:
            return "Strong Increase"
        elif change > 5:
            return "Moderate Increase"
        elif change < -20:
            return "Strong Decrease"
        elif change < -5:
            return "Moderate Decrease"
        else:
            return "Stable"
    
    trend_text = (
        f"Trend Analysis:\n"
        f"Short-term (4W): {get_trend_description(weekly_ma.iloc[-5] if len(weekly_ma) >= 5 else None, weekly_ma.iloc[-1])}\n"
        f"Medium-term (3M): {get_trend_description(monthly_ma.iloc[-4] if len(monthly_ma) >= 4 else None, monthly_ma.iloc[-1])}\n"
        f"Long-term (2Y): {get_trend_description(yearly_ma.iloc[-3] if len(yearly_ma) >= 3 else None, yearly_ma.iloc[-1])}"
    )
    plt.figtext(0.98, 0.02, trend_text, fontsize=10,
                bbox=dict(facecolor='white', alpha=0.8),
                horizontalalignment='right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save if output directory is provided
    if output_dir:
        output_path = Path(output_dir) / f"{article_name}_revision_activity_ma.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_path}")
    
    return fig

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Create time series plots from Wikipedia revision data"
    )
    parser.add_argument(
        "--input-file", 
        type=Path, 
        required=True, 
        help="Path to the input feather file"
    )
    parser.add_argument(
        "--output-dir", 
        type=Path, 
        default=Path("plots"), 
        help="Directory to save plot"
    )
    parser.add_argument(
        "--article-name",
        type=str,
        help="Name of the article (defaults to feather filename if not provided)"
    )
    parser.add_argument(
        "--ma",
        action="store_true",
        help="Include moving averages in the plots"
    )
    
    args = parser.parse_args()
    
    # Verify input file exists
    if not args.input_file.exists():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")
    
    # Create output directory if it doesn't exist
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get article name from file name if not provided
    article_name = args.article_name if args.article_name else args.input_file.stem
    
    print(f"Processing {article_name}...")
    df = load_and_process_data(args.input_file)
    
    if args.ma:
        create_time_series_plots_with_ma(df, article_name, args.output_dir)
    else:
        create_time_series_plots_raw(df, article_name, args.output_dir)
    
    plt.close()
    print("Processing complete!")


# Only run this if the script is run directly (not imported)
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Create time series plots from Wikipedia revision data"
    )
    main()