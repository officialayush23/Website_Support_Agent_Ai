# app/main.py
from fastapi import FastAPI
from app.core.security import setup_cors

from app.api.routers import (
    products,
    carts,
    orders,
    support,
    admin,payments,stores,offers,delivery,complaints,product_images,recommendations,addresses,users,events,refunds,pickups,recommendations,handoff
    
)
from app.api.ws import chat
app = FastAPI(title="Website Support Agent")

setup_cors(app)

app.include_router(products.router)
app.include_router(carts.router)
app.include_router(orders.router)
app.include_router(support.router)
app.include_router(admin.router)
app.include_router(stores.router)
app.include_router(offers.router)
app.include_router(delivery.router)
app.include_router(complaints.router)
app.include_router(payments.router)
app.include_router(product_images.router)
app.include_router(recommendations.router)
app.include_router(chat.router)
app.include_router(addresses.router)
app.include_router(users.router)
app.include_router(refunds.router)
app.include_router(events.router)
app.include_router(pickups.router)
app.include_router(handoff.router)
@app.get("/health")
async def health():
    return {"status": "ok"}
