import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database Setup (SQLite)
DATABASE_URL = "sqlite:///./ecommerce.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBOrder(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    sales = Column(Float)

class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise BI & ML Engine")

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

# Seed initial data if empty
def init_db():
    db = SessionLocal()
    if db.query(DBOrder).count() == 0:
        initial = [
            DBOrder(order_id=101, category="Electronics", sales=1200),
            DBOrder(order_id=102, category="Clothing", sales=450),
            DBOrder(order_id=103, category="Electronics", sales=800),
            DBOrder(order_id=104, category="Home", sales=300),
            DBOrder(order_id=105, category="Clothing", sales=600)
        ]
        db.add_all(initial)
        db.commit()
    db.close()

init_db()

# Train & Save Dummy Scikit-Learn Model via Joblib
model_path = "model.joblib"
if not os.path.exists(model_path):
    from sklearn.linear_model import LinearRegression
    import numpy as np
    X = np.array([[1], [5], [10], [20], [50]])
    y = np.array([125.5, 627.5, 1255, 2510, 6275])
    lr = LinearRegression().fit(X, y)
    joblib.dump(lr, model_path)

class OrderCreate(BaseModel):
    category: str
    sales: float

class UserAuth(BaseModel):
    username: str
    password: str

@post_route := app.post("/api/signup")
def signup(user: UserAuth, db: Session = Depends(get_db)):
    existing = db.query(DBUser).filter(DBUser.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = DBUser(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    return {"message": "Signup successful"}

@app.post("/api/login")
def login(user: UserAuth, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == user.username, DBUser.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login success", "token": "jwt-token-pro-mock-v2"}

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    orders = db.query(DBOrder).all()
    if not orders:
        return {"total_sales": 0, "average_order_value": 0, "category_breakdown": {}, "total_orders": 0, "sales_trend": []}
    
    total_sales = sum(o.sales for o in orders)
    avg_order = total_sales / len(orders)
    
    breakdown = {}
    for o in orders:
        breakdown[o.category] = breakdown.get(o.category, 0) + o.sales
        
    trend = [{"order_id": o.order_id, "sales": o.sales} for o in orders]
    
    return {
        "total_sales": float(total_sales),
        "average_order_value": round(float(avg_order), 2),
        "category_breakdown": breakdown,
        "total_orders": len(orders),
        "sales_trend": trend
    }

@app.post("/api/orders")
def add_order(order: OrderCreate, db: Session = Depends(get_db)):
    max_id = db.query(DBOrder).order_by(DBOrder.order_id.desc()).first()
    new_id = (max_id.order_id + 1) if max_id else 101
    
    new_order = DBOrder(order_id=new_id, category=order.category, sales=order.sales)
    db.add(new_order)
    db.commit()
    
    total_count = db.query(DBOrder).count()
    return {"message": "Success", "total_orders": total_count}

@app.get("/api/predict/{quantity}")
def predict_sales(quantity: int):
    model = joblib.load(model_path)
    prediction = float(model.predict([[quantity]])[0])
    return {"predicted_revenue": round(prediction, 2)}

@app.get("/api/export")
def export_csv(db: Session = Depends(get_db)):
    orders = db.query(DBOrder).all()
    df = pd.DataFrame([{"order_id": o.order_id, "category": o.category, "sales": o.sales} for o in orders])
    export_path = "export_sales.csv"
    df.to_csv(export_path, index=False)
    return FileResponse(export_path, media_type='text/csv', filename="sales_report.csv")