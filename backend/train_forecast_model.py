"""
Train LSTM Forecasting Model
Trains the model on historical ticket data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.forecasting_service import TicketForecastingService
from data.generate_historical_data import (
    generate_historical_tickets,
    save_historical_data,
    load_historical_data,
    get_data_summary,
)
import os


def train_forecasting_model():
    """Train the LSTM model on historical data"""

    print("\n" + "=" * 70)
    print("  LSTM Forecasting Model Training")
    print("=" * 70 + "\n")

    # Check if historical data exists
    data_file = "./data/historical_tickets.csv"

    if not os.path.exists(data_file):
        print("Generating historical data...")
        df = generate_historical_tickets(days=180)
        save_historical_data(df, data_file)
    else:
        print("Loading existing historical data...")
        df = load_historical_data(data_file)

    # Show summary
    summary = get_data_summary(df)
    print(f"\nLoaded {len(df)} hourly records")
    print(
        f"Date range: {summary['date_range']['start'][:10]} to {summary['date_range']['end'][:10]}"
    )
    print(f"Total tickets: {summary['ticket_stats']['total_tickets']:,}")
    print(f"Avg per day: {summary['ticket_stats']['avg_per_day']:.1f}")

    # Initialize forecasting service
    print("\nInitializing forecasting service...")
    service = TicketForecastingService()

    # Train model
    print("\nStarting model training...")
    print("   (This may take a few minutes...)\n")

    results = service.train(
        ticket_history=df[["timestamp", "ticket_count"]],
        epochs=50,
        batch_size=32,
        validation_split=0.2,
    )

    # Test predictions
    print("\n" + "=" * 70)
    print("  Testing Predictions")
    print("=" * 70 + "\n")

    # Use last 24 hours as input
    recent_data = df["ticket_count"].tail(24).tolist()

    # Predict next 24 hours
    predictions = service.predict_next_hours(recent_data, hours=24)

    print("Next 24 Hours Forecast:")
    print("-" * 70)
    for i, pred in enumerate(predictions[:10]):  # Show first 10
        print(f"   Hour {i+1}: {pred['predicted_tickets']} tickets")
    print("   ...")

    # Daily predictions
    daily_preds = service.predict_daily_volume(recent_data, days=7)

    print("\nNext 7 Days Forecast:")
    print("-" * 70)
    for pred in daily_preds:
        staffing = service.get_staffing_recommendation(pred["predicted_tickets"])
        print(
            f"   {pred['date']}: {pred['predicted_tickets']} tickets → {staffing['recommended_agents']} agents {staffing['message']}"
        )

    print("\n" + "=" * 70)
    print("  Training Complete!")
    print("=" * 70 + "\n")

    print("Model Performance:")
    print(f"   Final MAE: {results['mae']:.2f} tickets")
    print(f"   Epochs trained: {results['epochs_trained']}")
    print(f"   Training sequences: {results['sequences']:,}")

    print(f"\nModel saved to: {service.model_path}")
    print("\nYou can now use the forecasting API to get predictions!")

    return service, results


if __name__ == "__main__":
    try:
        service, results = train_forecasting_model()
    except Exception as e:
        print(f"\nTraining Error: {str(e)}")
        print("\nMake sure to install dependencies:")
        print("   pip install tensorflow pandas scikit-learn")
        import traceback

        traceback.print_exc()
