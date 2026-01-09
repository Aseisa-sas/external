from fastapi import FastAPI, HTTPException, status
from app.scraper import AdresScraper
from app.models import AdresResponse

app = FastAPI(
    title="ADRES Consultation API",
    description="API to query health entity affiliation in Colombia",
    version="1.0.0"
)

scraper = AdresScraper()

@app.get("/consult/{identity}", response_model=AdresResponse)
def consult_identity(identity: str):
    """
    Endpoint to query ADRES by identity number.

    Args:
        identity (str): The citizenship card number (CC).

    Returns:
        AdresResponse: JSON object with specific affiliate details.
    """
    if not identity.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identity must contain only numbers."
        )

    data = scraper.get_adres_info(identity)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No records found or timeout waiting for external service."
        )

    return data

@app.get("/")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "ADRES API"}
