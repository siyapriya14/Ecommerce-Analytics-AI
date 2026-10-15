from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os

# Absolute path for SQLite database on Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'ecommerce.db')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    sales = Column(Float)

# Smart auto-migration check: Recreate tables only if schema mismatch occurs
inspector = inspect(engine)
if "users" in inspector.get_table_names():
    columns = [c["name"] for c in inspector.get_columns("users")]
    if "email" not in columns:
        Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce Analytics & AI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserSignup(BaseModel):
    email: str
    password: str

class UserCredentials(BaseModel):
    username: str
    password: str

class OrderInput(BaseModel):
    category: str
    sales: float

class PredictionInput(BaseModel):
    category_id: int
    discount: float
    marketing_spend: float
    customer_rating: float

@app.post("/api/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    try:
        db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = UserDB(email=user.email, password=user.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User created successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
def login(credentials: UserCredentials, db: Session = Depends(get_db)):
    try:
        user = db.query(UserDB).filter(UserDB.email == credentials.username).first()
        if not user or user.password != credentials.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return {"access_token": user.email, "token_type": "bearer"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    try:
        orders = db.query(OrderDB).all()
    except Exception:
        orders = []
        
    base_sales = 142580
    base_orders = 342
    
    total_sales = base_sales + sum(o.sales for o in orders)
    total_orders = base_orders + len(orders)
    
    category_breakdown = {"Electronics": 45000, "Apparel": 32000, "Home & Kitchen": 28000, "Beauty": 22000, "Sports": 15580}
    for o in orders:
        category_breakdown[o.category] = category_breakdown.get(o.category, 0) + o.sales

    categories = [{"name": k, "sales": v} for k, v in category_breakdown.items()]

    return {
        "total_sales": total_sales,
        "monthly_growth": "+18.4%",
        "active_orders": total_orders,
        "categories": categories
    }

@app.post("/api/orders")
def add_order(order: OrderInput, db: Session = Depends(get_db)):
    try:
        new_order = OrderDB(category=order.category, sales=order.sales)
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return {"message": "Order added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
def predict_revenue(data: PredictionInput):
    predicted_val = (data.marketing_spend * 1.8) + (data.customer_rating * 5000) - (data.discount * 1000) + 12000
    return {"predicted_revenue": max(round(predicted_val, 2), 1000.0)}

# Mount Frontend Build
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        if full_path.startswith("api/"):
            return {"detail": "API endpoint not found"}, 404
        return FileResponse(os.path.join(frontend_dist, "index.html"))