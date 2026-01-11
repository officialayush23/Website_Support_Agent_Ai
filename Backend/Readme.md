backend/
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py        # env, settings
│   │   ├── database.py      # async SQLAlchemy
│   │   ├── auth.py          # Supabase JWT verification
│   │   ├── redis.py         # Redis client
│   │   └── security.py
│   │
│   ├── models/
│   │   └── models.py        # ALL SQLAlchemy models (1 file)
│   │
│   ├── schema/
│   │   └── schemas.py       # ALL Pydantic schemas (1 file)
│   │
│   ├── services/
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   ├── offer_service.py
│   │   ├── support_service.py
│   │   ├── rag_service.py
│   │   └── llm_service.py   # Gemini 2.5 Flash
│   │
│   ├── api/
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── products.py
│   │       ├── cart.py
│   │       ├── orders.py
│   │       ├── offers.py
│   │       ├── support.py
│   │       └── admin.py
│   │
│   ├── websocket/
│   │   └── chat_ws.py       # realtime support chat
│   │
│   └── utils/
│       └── pagination.py
│
├── requirements.txt

