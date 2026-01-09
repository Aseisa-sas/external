from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from app.scraper import AdresScraper
from app.models import AdresResponse

app = FastAPI(
    title="ADRES Consultation API",
    description="API to query health entity affiliation in Colombia",
    version="1.0.0"
)

scraper = AdresScraper()

@app.get("/consult/{identity}")
def consult_identity(identity: str):
    """
    Endpoint to query ADRES by identity number.
    """
    if not identity.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identity must contain only numbers."
        )

    data = scraper.get_adres_info(identity)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="External service timeout or internal error."
        )

    if data.get("found") is False:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "The patient is not registered at ADRES",
                "code": "1"
            }
        )

    if "found" in data:
        del data["found"]

    return data

@app.get("/")
def health_check():
    return {"status": "ok", "service": "ADRES API"}
