"""
Forecasting Service - LSTM-based Ticket Volume Prediction
Predicts future ticket volumes for staffing optimization
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pickle

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    from sklearn.preprocessing import MinMaxScaler
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️  TensorFlow not available. Install with: pip install tensorflow")


class TicketForecastingService:
    """
    LSTM-based forecasting service for ticket volume prediction
    """
    
    def __init__(self, model_path: str = "./models/lstm_forecast.h5"):
        """
        Initialize forecasting service
        
        Args:
            model_path: Path to save/load trained model
        """
        self.model_path = model_path
        self.scaler_path = model_path.replace('.h5', '_scaler.pkl')
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.sequence_length = 24  # Use 24 hours of data to predict next hour
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Load model if exists
        if os.path.exists(model_path):
            self.load_model()
    
    def create_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """
        Create LSTM model architecture
        
        Args:
            input_shape: (sequence_length, num_features)
        
        Returns:
            Compiled LSTM model
        """
        model = Sequential([
            # First LSTM layer with return sequences
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            
            # Second LSTM layer
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            
            # Dense layers
            Dense(25, activation='relu'),
            Dense(1)  # Output: predicted ticket count
        ])
        
        model.compile(
            optimizer='adam',
            loss='mean_squared_error',
            metrics=['mae']  # Mean Absolute Error
        )
        
        return model
    
    def prepare_sequences(
        self,
        data: np.ndarray,
        sequence_length: int = 24
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training
        
        Args:
            data: Time series data
            sequence_length: Number of timesteps to look back
        
        Returns:
            X (sequences), y (targets)
        """
        X, y = [], []
        
        for i in range(len(data) - sequence_length):
            X.append(data[i:i + sequence_length])
            y.append(data[i + sequence_length])
        
        return np.array(X), np.array(y)
    
    def train(
        self,
        ticket_history: pd.DataFrame,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train LSTM model on historical ticket data
        
        Args:
            ticket_history: DataFrame with columns ['timestamp', 'ticket_count']
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data for validation
        
        Returns:
            Training history and metrics
        """
        if not TENSORFLOW_AVAILABLE:
            return {"error": "TensorFlow not installed"}
        
        print("\n🤖 Training LSTM Forecasting Model...")
        print("="*60)
        
        # Prepare data
        ticket_counts = ticket_history['ticket_count'].values.reshape(-1, 1)
        
        # Normalize data
        scaled_data = self.scaler.fit_transform(ticket_counts)
        
        # Create sequences
        X, y = self.prepare_sequences(scaled_data, self.sequence_length)
        
        print(f"✓ Prepared {len(X)} training sequences")
        print(f"✓ Sequence length: {self.sequence_length} timesteps")
        
        # Create model
        self.model = self.create_model(input_shape=(X.shape[1], X.shape[2]))
        
        print(f"✓ Model created with {self.model.count_params():,} parameters")
        
        # Early stopping to prevent overfitting
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train model
        print("\n🔄 Training in progress...")
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=1
        )
        
        # Save model
        self.save_model()
        
        print("\n✅ Training complete!")
        print(f"Final loss: {history.history['loss'][-1]:.4f}")
        print(f"Final MAE: {history.history['mae'][-1]:.2f} tickets")
        
        return {
            "loss": history.history['loss'][-1],
            "mae": history.history['mae'][-1],
            "epochs_trained": len(history.history['loss']),
            "sequences": len(X)
        }
    
    def predict_next_hours(self, recent_data: List[int], hours: int = 24) -> List[Dict[str, Any]]:
        """
        Predict ticket volumes for next N hours
        
        Args:
            recent_data: Last 24 hours of ticket counts
            hours: Number of hours to forecast
        
        Returns:
            List of predictions with timestamps
        """
        if not self.model:
            return [{"error": "Model not trained"}]
        
        predictions = []
        current_sequence = np.array(recent_data[-self.sequence_length:]).reshape(-1, 1)
        current_sequence = self.scaler.transform(current_sequence)
        
        base_time = datetime.utcnow()
        
        for h in range(hours):
            # Reshape for prediction
            X = current_sequence.reshape(1, self.sequence_length, 1)
            
            # Predict next value
            scaled_pred = self.model.predict(X, verbose=0)[0, 0]
            
            # Inverse transform to get actual ticket count
            pred_count = self.scaler.inverse_transform([[scaled_pred]])[0, 0]
            pred_count = max(0, int(round(pred_count)))  # Ensure non-negative integer
            
            # Store prediction
            predictions.append({
                "timestamp": (base_time + timedelta(hours=h+1)).isoformat(),
                "predicted_tickets": pred_count,
                "hour_offset": h + 1
            })
            
            # Update sequence for next prediction
            current_sequence = np.append(current_sequence[1:], [[scaled_pred]], axis=0)
        
        return predictions
    
    def predict_daily_volume(self, recent_data: List[int], days: int = 7) -> List[Dict[str, Any]]:
        """
        Predict daily ticket volumes
        
        Args:
            recent_data: Recent hourly ticket counts
            days: Number of days to forecast
        
        Returns:
            Daily predictions
        """
        # Predict hourly for the period
        hourly_predictions = self.predict_next_hours(recent_data, hours=days*24)
        
        # Aggregate by day
        daily_predictions = []
        current_day = []
        current_date = datetime.utcnow().date()
        
        for i, pred in enumerate(hourly_predictions):
            current_day.append(pred['predicted_tickets'])
            
            if (i + 1) % 24 == 0:
                daily_predictions.append({
                    "date": (current_date + timedelta(days=len(daily_predictions)+1)).isoformat(),
                    "predicted_tickets": sum(current_day),
                    "day_offset": len(daily_predictions) + 1
                })
                current_day = []
        
        return daily_predictions
    
    def get_staffing_recommendation(self, predicted_tickets: int) -> Dict[str, Any]:
        """
        Recommend staff count based on predicted ticket volume
        
        Args:
            predicted_tickets: Predicted number of tickets
        
        Returns:
            Staffing recommendation
        """
        # Assume each agent can handle 15 tickets per day
        tickets_per_agent = 15
        
        # Calculate required agents
        base_agents = max(1, int(np.ceil(predicted_tickets / tickets_per_agent)))
        
        # Add buffer for high volumes
        if predicted_tickets > 100:
            buffer = 1
        elif predicted_tickets > 50:
            buffer = 0.5
        else:
            buffer = 0
        
        recommended_agents = int(base_agents + buffer)
        
        # Determine urgency level
        if predicted_tickets > 150:
            urgency = "critical"
            message = "🔴 Very high volume expected - hire temp staff!"
        elif predicted_tickets > 100:
            urgency = "high"
            message = "🟠 High volume expected - all hands on deck"
        elif predicted_tickets > 50:
            urgency = "medium"
            message = "🟡 Moderate volume - standard staffing"
        else:
            urgency = "low"
            message = "🟢 Low volume - minimal staffing needed"
        
        return {
            "predicted_tickets": predicted_tickets,
            "recommended_agents": recommended_agents,
            "tickets_per_agent": tickets_per_agent,
            "urgency": urgency,
            "message": message
        }
    
    def save_model(self):
        """Save trained model and scaler"""
        if self.model:
            self.model.save(self.model_path)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            print(f"✅ Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model and scaler"""
        try:
            self.model = load_model(self.model_path)
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            print(f"✅ Model loaded from {self.model_path}")
            return True
        except Exception as e:
            print(f"⚠️  Could not load model: {str(e)}")
            return False


# Global forecasting service instance
_forecasting_service = None


def get_forecasting_service() -> TicketForecastingService:
    """Get or create the global forecasting service instance"""
    global _forecasting_service
    if _forecasting_service is None:
        _forecasting_service = TicketForecastingService()
    return _forecasting_service


def predict_ticket_volume(hours: int = 24) -> List[Dict[str, Any]]:
    """
    Convenience function to predict ticket volumes
    
    Usage:
        predictions = predict_ticket_volume(hours=48)
        for pred in predictions[:10]:
            print(f"{pred['timestamp']}: {pred['predicted_tickets']} tickets")
    """
    service = get_forecasting_service()
    
    # In production, fetch recent_data from database
    # For now, use dummy data
    recent_data = [20] * 24  # Placeholder
    
    return service.predict_next_hours(recent_data, hours)
