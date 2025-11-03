"""
Generate Sample Historical Ticket Data
Creates realistic ticket volume data with patterns for LSTM training
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict
import json


def generate_historical_tickets(days: int = 180) -> pd.DataFrame:
    """
    Generate realistic historical ticket data
    
    Patterns included:
    - Daily cycle (more tickets during business hours)
    - Weekly cycle (more on Mondays, less on weekends)
    - Monthly cycle (spike at start of month for billing)
    - Random noise
    - Special events (Black Friday, holiday surges)
    
    Args:
        days: Number of days of historical data
    
    Returns:
        DataFrame with hourly ticket counts
    """
    
    # Generate timestamps (hourly for N days)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    timestamps = pd.date_range(start=start_time, end=end_time, freq='H')
    
    ticket_counts = []
    
    for ts in timestamps:
        # Base volume (average 60 tickets/day = 2.5 tickets/hour)
        base = 2.5
        
        # Daily pattern (more during business hours 9am-5pm)
        hour = ts.hour
        if 9 <= hour <= 17:
            hourly_multiplier = 2.0  # Double during business hours
        elif 18 <= hour <= 21:
            hourly_multiplier = 1.2  # Some evening activity
        else:
            hourly_multiplier = 0.3  # Low overnight
        
        # Weekly pattern
        weekday = ts.weekday()
        if weekday == 0:  # Monday - highest
            weekly_multiplier = 1.4
        elif weekday == 1:  # Tuesday
            weekly_multiplier = 1.2
        elif weekday == 2:  # Wednesday
            weekly_multiplier = 1.1
        elif weekday == 3:  # Thursday
            weekly_multiplier = 1.0
        elif weekday == 4:  # Friday
            weekly_multiplier = 0.9
        elif weekday == 5:  # Saturday
            weekly_multiplier = 0.5
        else:  # Sunday
            weekly_multiplier = 0.4
        
        # Monthly pattern (billing spike on 1st-3rd)
        if ts.day <= 3:
            monthly_multiplier = 1.5
        elif ts.day >= 28:
            monthly_multiplier = 1.2  # End of month inquiries
        else:
            monthly_multiplier = 1.0
        
        # Special events
        special_multiplier = 1.0
        
        # Black Friday (last Friday of November)
        if ts.month == 11 and ts.day >= 20 and ts.day <= 30 and weekday == 4:
            special_multiplier = 3.0
        
        # Holiday season (Dec 15 - Dec 25)
        if ts.month == 12 and 15 <= ts.day <= 25:
            special_multiplier = 2.0
        
        # New Year sale (Jan 1-7)
        if ts.month == 1 and ts.day <= 7:
            special_multiplier = 1.8
        
        # Calculate ticket count
        count = (base * 
                hourly_multiplier * 
                weekly_multiplier * 
                monthly_multiplier * 
                special_multiplier)
        
        # Add random noise (±30%)
        noise = np.random.uniform(0.7, 1.3)
        count *= noise
        
        # Ensure non-negative integer
        count = max(0, int(round(count)))
        
        ticket_counts.append(count)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'ticket_count': ticket_counts
    })
    
    # Add derived features for analysis
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['day_of_month'] = df['timestamp'].dt.day
    df['month'] = df['timestamp'].dt.month
    df['is_business_hours'] = df['hour'].apply(lambda h: 1 if 9 <= h <= 17 else 0)
    df['is_weekend'] = df['day_of_week'].apply(lambda d: 1 if d >= 5 else 0)
    
    return df


def save_historical_data(df: pd.DataFrame, filepath: str = './data/historical_tickets.csv'):
    """Save historical data to CSV"""
    df.to_csv(filepath, index=False)
    print(f"✅ Saved {len(df)} records to {filepath}")


def load_historical_data(filepath: str = './data/historical_tickets.csv') -> pd.DataFrame:
    """Load historical data from CSV"""
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def get_data_summary(df: pd.DataFrame) -> Dict[str, any]:
    """Get summary statistics of the data"""
    return {
        "total_records": len(df),
        "date_range": {
            "start": df['timestamp'].min().isoformat(),
            "end": df['timestamp'].max().isoformat(),
            "days": (df['timestamp'].max() - df['timestamp'].min()).days
        },
        "ticket_stats": {
            "total_tickets": int(df['ticket_count'].sum()),
            "avg_per_hour": round(df['ticket_count'].mean(), 2),
            "avg_per_day": round(df['ticket_count'].sum() / ((df['timestamp'].max() - df['timestamp'].min()).days), 2),
            "max_hour": int(df['ticket_count'].max()),
            "min_hour": int(df['ticket_count'].min())
        },
        "patterns": {
            "busiest_hour": int(df.groupby('hour')['ticket_count'].mean().idxmax()),
            "busiest_day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][
                int(df.groupby('day_of_week')['ticket_count'].mean().idxmax())
            ],
            "business_hours_avg": round(df[df['is_business_hours'] == 1]['ticket_count'].mean(), 2),
            "after_hours_avg": round(df[df['is_business_hours'] == 0]['ticket_count'].mean(), 2)
        }
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  📊 Generating Historical Ticket Data")
    print("="*70 + "\n")
    
    # Generate 6 months of data
    print("🔄 Generating 6 months of hourly ticket data...")
    df = generate_historical_tickets(days=180)
    
    print(f"✅ Generated {len(df)} hourly records\n")
    
    # Show summary
    summary = get_data_summary(df)
    print("📈 Data Summary:")
    print(f"   Period: {summary['date_range']['start'][:10]} to {summary['date_range']['end'][:10]}")
    print(f"   Total Tickets: {summary['ticket_stats']['total_tickets']:,}")
    print(f"   Avg per Hour: {summary['ticket_stats']['avg_per_hour']}")
    print(f"   Avg per Day: {summary['ticket_stats']['avg_per_day']}")
    print(f"\n   Busiest Hour: {summary['patterns']['busiest_hour']}:00")
    print(f"   Busiest Day: {summary['patterns']['busiest_day']}")
    print(f"   Business Hours Avg: {summary['patterns']['business_hours_avg']} tickets/hour")
    print(f"   After Hours Avg: {summary['patterns']['after_hours_avg']} tickets/hour")
    
    # Save to file
    print("\n💾 Saving to file...")
    save_historical_data(df)
    
    # Show sample
    print("\n📋 Sample Data (first 10 hours):")
    print(df[['timestamp', 'ticket_count', 'hour', 'day_of_week']].head(10).to_string(index=False))
    
    print("\n" + "="*70)
    print("  ✅ Historical Data Generation Complete!")
    print("="*70 + "\n")
