from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field


app = FastAPI(title="Typed Validation API", docs_url=None, redoc_url=None, openapi_url=None, redirect_slashes=False)

CENTS = Decimal("0.01")
class QuoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=4)
    quantity: int = Field(ge=1, le=1000, strict=True)


class QuoteResponse(BaseModel):
    total: str

@app.post("/quotes", response_model=QuoteResponse)
def create_quote(request: QuoteRequest):
    total = (request.unit_price * request.quantity).quantize(CENTS, rounding=ROUND_HALF_UP)
    return QuoteResponse(total=str(total))


class ProductResponse(BaseModel):
    id: UUID
    name: str








class ProductRecord(BaseModel):
    id: UUID
    name: str
    supplier_password: str


PRODUCTS = {
        UUID("3f2b8c1e-7a4d-4e9b-9c6f-1d2e3a4b5c6d"): ProductRecord(
            id=UUID("3f2b8c1e-7a4d-4e9b-9c6f-1d2e3a4b5c6d"),
            name="Notebook",
            supplier_password="canary-supplier-password-7d1f",
        ),
    } 


@app.get("/products/{product_id}", response_model=ProductResponse)

def get_product(product_id: UUID):
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
