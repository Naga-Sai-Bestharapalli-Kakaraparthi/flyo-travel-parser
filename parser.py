import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError

# ==========================================
# 1. Pydantic v2 Schemas (Strict Typing)
# ==========================================
class FlightSegment(BaseModel):
    airline_code: str = Field(..., description="2-letter IATA airline code (e.g., AI, 6E)")
    flight_number: str = Field(..., description="3 to 4 digit flight number")
    origin: str = Field(..., min_length=3, max_length=3, description="3-letter IATA origin airport code")
    destination: str = Field(..., min_length=3, max_length=3, description="3-letter IATA destination airport code")
    departure_time: Optional[datetime] = None
    price_inr: float = Field(..., gt=0, description="Total price in INR")

class TravelItinerary(BaseModel):
    passenger_name: str
    pnr_code: str = Field(..., min_length=6, max_length=6, description="6-character alphanumeric PNR")
    segments: List[FlightSegment]

# ==========================================
# 2. Deterministic Fallback Parser (Regex)
# ==========================================
def parse_with_regex_fallback(raw_email_text: str) -> dict:
    """
    Fallback parser using strict Regex patterns when LLM or primary structured output fails.
    Prevents pipeline failures on unstructured raw text.
    """
    flight_match = re.search(r'\b([A-Z0-9]{2})\s?(\d{3,4})\b', raw_email_text)
    pnr_match = re.search(r'\b[A-Z0-9]{6}\b', raw_email_text)
    
    return {
        "airline_code": flight_match.group(1) if flight_match else "UNKNOWN",
        "flight_number": flight_match.group(2) if flight_match else "0000",
        "pnr_code": pnr_match.group(0) if pnr_match else "N/A",
        "parsing_strategy": "REGEX_FALLBACK"
    }

# ==========================================
# 3. Main Ingestion Pipeline
# ==========================================
def ingest_travel_document(payload: dict, raw_text_backup: str):
    """
    Ingests and validates unstructured booking payload using Pydantic.
    Falls back to deterministic regex parsing if validation fails.
    """
    try:
        itinerary = TravelItinerary(**payload)
        return {
            "status": "SUCCESS",
            "data": itinerary.model_dump(),
            "strategy": "PYDANTIC_V2_STRICT"
        }
    except ValidationError as err:
        fallback_data = parse_with_regex_fallback(raw_text_backup)
        return {
            "status": "PARTIAL_SUCCESS",
            "data": fallback_data,
            "errors": err.errors(),
            "strategy": "REGEX_FALLBACK"
        }

if __name__ == "__main__":
    sample_email_text = "Booking Confirmation PNR: ABC123 Flight 6E 204 from HYD to DEL"
    valid_payload = {
        "passenger_name": "Naga Sai",
        "pnr_code": "ABC123",
        "segments": [
            {"airline_code": "6E", "flight_number": "204", "origin": "HYD", "destination": "DEL", "price_inr": 4500.00}
        ]
    }
    print("Ingestion Result:", ingest_travel_document(valid_payload, sample_email_text))
