"""
Forecasting API Endpoints
Provides REST API for ticket volume predictions
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.forecasting_service import get_forecasting_service
from pydantic import BaseModel


router = APIRouter(prefix="/api/forecast", tags=["forecasting"])


class ForecastResponse(BaseModel):
    """Response model for forecast"""
    predictions: List[Dict[str, Any]]
    summary: Dict[str, Any]


@router.get("/hourly/{hours}", response_model=ForecastResponse)
async def get_hourly_forecast(hours: int = 24):
    """
    Get hourly ticket volume forecast
    
    Args:
        hours: Number of hours to forecast (default: 24, max: 168 = 1 week)
    
    Returns:
        Hourly predictions with staffing recommendations
    """
    if hours > 168:
        raise HTTPException(status_code=400, detail="Maximum forecast period is 168 hours (1 week)")
    
    service = get_forecasting_service()
    
    if not service.model:
        raise HTTPException(
            status_code=503,
            detail="Forecasting model not trained. Run train_forecast_model.py first."
        )
    
    # In production, fetch recent_data from database
    # For now, use dummy pattern
    recent_data = [3 if i % 24 < 9 or i % 24 > 17 else 6 for i in range(24)]
    
    try:
        predictions = service.predict_next_hours(recent_data, hours=hours)
        
        # Calculate summary stats
        total_tickets = sum(p['predicted_tickets'] for p in predictions)
        avg_per_hour = total_tickets / len(predictions)
        peak_hour = max(predictions, key=lambda x: x['predicted_tickets'])
        
        # Overall staffing recommendation
        avg_staffing = service.get_staffing_recommendation(int(avg_per_hour * 8))  # 8-hour shift
        
        summary = {
            "total_predicted_tickets": total_tickets,
            "avg_per_hour": round(avg_per_hour, 2),
            "peak_hour": peak_hour,
            "recommended_agents": avg_staffing['recommended_agents'],
            "forecast_period_hours": hours,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return ForecastResponse(predictions=predictions, summary=summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting error: {str(e)}")


@router.get("/daily/{days}")
async def get_daily_forecast(days: int = 7):
    """
    Get daily ticket volume forecast
    
    Args:
        days: Number of days to forecast (default: 7, max: 30)
    
    Returns:
        Daily predictions with staffing recommendations
    """
    if days > 30:
        raise HTTPException(status_code=400, detail="Maximum forecast period is 30 days")
    
    service = get_forecasting_service()
    
    if not service.model:
        raise HTTPException(
            status_code=503,
            detail="Forecasting model not trained. Run train_forecast_model.py first."
        )
    
    # Dummy recent data
    recent_data = [3 if i % 24 < 9 or i % 24 > 17 else 6 for i in range(24)]
    
    try:
        daily_predictions = service.predict_daily_volume(recent_data, days=days)
        
        # Add staffing recommendations
        for pred in daily_predictions:
            staffing = service.get_staffing_recommendation(pred['predicted_tickets'])
            pred['staffing'] = staffing
        
        # Calculate summary
        total_tickets = sum(p['predicted_tickets'] for p in daily_predictions)
        avg_per_day = total_tickets / len(daily_predictions)
        peak_day = max(daily_predictions, key=lambda x: x['predicted_tickets'])
        
        summary = {
            "total_predicted_tickets": total_tickets,
            "avg_per_day": round(avg_per_day, 2),
            "peak_day": peak_day['date'],
            "peak_day_tickets": peak_day['predicted_tickets'],
            "forecast_period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return {
            "predictions": daily_predictions,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting error: {str(e)}")


@router.get("/staffing/current")
async def get_current_staffing():
    """
    Get current staffing recommendation based on real-time data
    
    Returns:
        Current staffing needs
    """
    service = get_forecasting_service()
    
    if not service.model:
        raise HTTPException(
            status_code=503,
            detail="Forecasting model not trained. Run train_forecast_model.py first."
        )
    
    # In production, get current hour's predicted volume
    # For now, predict next hour
    recent_data = [3 if i % 24 < 9 or i % 24 > 17 else 6 for i in range(24)]
    next_hour_pred = service.predict_next_hours(recent_data, hours=1)[0]
    
    # Get staffing for 8-hour shift
    shift_tickets = next_hour_pred['predicted_tickets'] * 8
    staffing = service.get_staffing_recommendation(shift_tickets)
    
    return {
        "current_time": datetime.utcnow().isoformat(),
        "next_hour_prediction": next_hour_pred,
        "shift_prediction": {
            "tickets": shift_tickets,
            "duration_hours": 8
        },
        "staffing": staffing
    }


@router.get("/model/info")
async def get_model_info():
    """Get information about the forecasting model"""
    service = get_forecasting_service()
    
    if not service.model:
        return {
            "status": "not_trained",
            "message": "Model not trained. Run train_forecast_model.py to train the model."
        }
    
    return {
        "status": "ready",
        "model_path": service.model_path,
        "sequence_length": service.sequence_length,
        "model_type": "LSTM",
        "features": [
            "Hourly predictions",
            "Daily aggregations",
            "Staffing recommendations",
            "Pattern recognition (daily, weekly, monthly cycles)"
        ]
    }
