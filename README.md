# FastAPI CRUD Operations Demo

A comprehensive guide demonstrating CRUD (Create, Read, Update, Delete) operations in FastAPI with async capabilities and other powerful features.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [CRUD Operations Overview](#crud-operations-overview)
- [Complete Example](#complete-example)
- [Async Operations](#async-operations)
- [Database Integration](#database-integration)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Advanced Features](#advanced-features)
- [Running the Application](#running-the-application)

## Features

FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.8+ based on standard Python type hints. This demo showcases:

- ✅ **CRUD Operations** - Complete Create, Read, Update, Delete examples
- ✅ **Async/Await Support** - Native async/await for concurrent operations
- ✅ **Automatic API Documentation** - Interactive Swagger UI and ReDoc
- ✅ **Type Validation** - Automatic request/response validation using Pydantic
- ✅ **Dependency Injection** - Clean and reusable dependency system
- ✅ **High Performance** - Built on Starlette and Pydantic for speed
- ✅ **Standards-based** - Based on OpenAPI and JSON Schema

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/MOHIT-KUMAR0001/FastApi.git
cd FastApi
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install fastapi uvicorn[standard] sqlalchemy aiosqlite pydantic
```

## Project Structure

```
FastApi/
├── main.py              # Main application file
├── models.py            # Pydantic models
├── database.py          # Database configuration
├── crud.py              # CRUD operations
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## CRUD Operations Overview

CRUD operations are the foundation of any data-driven application:

- **C**reate - Add new items (POST)
- **R**ead - Retrieve items (GET)
- **U**pdate - Modify existing items (PUT/PATCH)
- **D**elete - Remove items (DELETE)

## Complete Example

### 1. Models (models.py)

Define your data models using Pydantic for automatic validation:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    is_available: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None

class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 2. Database Setup (database.py)

Using SQLAlchemy with async SQLite:

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./items.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)
```

### 3. CRUD Operations (crud.py)

Async CRUD functions for database operations:

```python
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import database

async def create_item(db: Session, item: models.ItemCreate) -> database.ItemDB:
    """Create a new item in the database"""
    db_item = database.ItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

async def get_item(db: Session, item_id: int) -> Optional[database.ItemDB]:
    """Retrieve a single item by ID"""
    return db.query(database.ItemDB).filter(database.ItemDB.id == item_id).first()

async def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[database.ItemDB]:
    """Retrieve multiple items with pagination"""
    return db.query(database.ItemDB).offset(skip).limit(limit).all()

async def update_item(db: Session, item_id: int, item: models.ItemUpdate) -> Optional[database.ItemDB]:
    """Update an existing item"""
    db_item = db.query(database.ItemDB).filter(database.ItemDB.id == item_id).first()
    if db_item:
        update_data = item.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

async def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item from the database"""
    db_item = db.query(database.ItemDB).filter(database.ItemDB.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False
```

### 4. Main Application (main.py)

FastAPI application with all CRUD endpoints:

```python
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
import models
import crud
import database

app = FastAPI(
    title="FastAPI CRUD Demo",
    description="A comprehensive demonstration of CRUD operations with async support",
    version="1.0.0"
)

# Dependency to get database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", tags=["Root"])
async def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to FastAPI CRUD Demo",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# CREATE - Add a new item
@app.post("/items/", response_model=models.Item, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item: models.ItemCreate, db: Session = Depends(get_db)):
    """
    Create a new item with the following information:
    - **title**: Item name (required, 1-100 characters)
    - **description**: Item description (optional, max 500 characters)
    - **price**: Item price (required, must be positive)
    - **is_available**: Availability status (default: true)
    """
    return await crud.create_item(db=db, item=item)

# READ - Get all items (with pagination)
@app.get("/items/", response_model=List[models.Item], tags=["Items"])
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all items with pagination:
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Maximum number of items to return (default: 100)
    """
    items = await crud.get_items(db=db, skip=skip, limit=limit)
    return items

# READ - Get a single item by ID
@app.get("/items/{item_id}", response_model=models.Item, tags=["Items"])
async def read_item(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific item by ID:
    - **item_id**: Unique identifier of the item
    """
    db_item = await crud.get_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# UPDATE - Modify an existing item
@app.put("/items/{item_id}", response_model=models.Item, tags=["Items"])
async def update_item(item_id: int, item: models.ItemUpdate, db: Session = Depends(get_db)):
    """
    Update an existing item:
    - **item_id**: Unique identifier of the item
    - Only provided fields will be updated
    """
    db_item = await crud.update_item(db=db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# DELETE - Remove an item
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    """
    Delete an item:
    - **item_id**: Unique identifier of the item to delete
    """
    success = await crud.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return None

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is running"""
    return {"status": "healthy"}
```

## Async Operations

FastAPI leverages Python's `async`/`await` syntax for high-performance concurrent operations:

### Why Async?

- **Non-blocking I/O**: Handle multiple requests simultaneously
- **Better resource utilization**: Doesn't waste CPU time waiting for I/O
- **Scalability**: Support more concurrent connections
- **Performance**: Faster response times under load

### Async Example

```python
import asyncio
from typing import List

@app.get("/items/batch", tags=["Async Demo"])
async def get_items_batch(item_ids: List[int], db: Session = Depends(get_db)):
    """Fetch multiple items concurrently"""
    tasks = [crud.get_item(db=db, item_id=item_id) for item_id in item_ids]
    items = await asyncio.gather(*tasks)
    return [item for item in items if item is not None]
```

### Async vs Sync Performance

```python
# Sync (blocking) - handles one request at a time
def sync_operation():
    time.sleep(1)  # Blocks the entire thread
    return "Done"

# Async (non-blocking) - can handle multiple requests
async def async_operation():
    await asyncio.sleep(1)  # Other requests can be processed
    return "Done"
```

## Database Integration

### Using Async SQLAlchemy

For true async database operations, use async SQLAlchemy:

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./items.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_async_db():
    async with async_session() as session:
        yield session
```

### Popular Database Choices

- **SQLite**: Simple, file-based (demo/development)
- **PostgreSQL**: Production-grade, async support via `asyncpg`
- **MySQL**: Widely used, async support via `aiomysql`
- **MongoDB**: NoSQL option with `motor` async driver

## API Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI
- Navigate to `http://localhost:8000/docs`
- Interactive API testing interface
- Try out endpoints directly from the browser

### ReDoc
- Navigate to `http://localhost:8000/redoc`
- Alternative documentation interface
- Clean, three-panel design

### OpenAPI Schema
- Access raw schema at `http://localhost:8000/openapi.json`
- Use for code generation in other languages

## Testing

### Example Test File (test_main.py)

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_create_item():
    response = client.post(
        "/items/",
        json={"title": "Test Item", "description": "Test description", "price": 10.99}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Item"

def test_read_items():
    response = client.get("/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_item():
    # Create an item first
    create_response = client.post(
        "/items/",
        json={"title": "Test Item", "description": "Test", "price": 10.99}
    )
    item_id = create_response.json()["id"]
    
    # Read the item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id

def test_update_item():
    # Create an item first
    create_response = client.post(
        "/items/",
        json={"title": "Test Item", "description": "Test", "price": 10.99}
    )
    item_id = create_response.json()["id"]
    
    # Update the item
    response = client.put(
        f"/items/{item_id}",
        json={"title": "Updated Item", "price": 15.99}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Item"
    assert response.json()["price"] == 15.99

def test_delete_item():
    # Create an item first
    create_response = client.post(
        "/items/",
        json={"title": "Test Item", "description": "Test", "price": 10.99}
    )
    item_id = create_response.json()["id"]
    
    # Delete the item
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204
    
    # Verify item is deleted
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404

def test_item_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404
```

### Running Tests

```bash
pip install pytest httpx
pytest test_main.py -v
```

## Advanced Features

### 1. Dependency Injection

```python
from fastapi import Header, HTTPException

async def verify_token(x_token: str = Header(...)):
    if x_token != "secret-token":
        raise HTTPException(status_code=400, detail="Invalid token")
    return x_token

@app.get("/protected/items/")
async def read_protected_items(token: str = Depends(verify_token)):
    return {"message": "Access granted"}
```

### 2. Background Tasks

```python
from fastapi import BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as log:
        log.write(f"{message}\n")

@app.post("/items/{item_id}/notify")
async def notify_item_created(item_id: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, f"Item {item_id} was created")
    return {"message": "Notification will be sent"}
```

### 3. CORS (Cross-Origin Resource Sharing)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Request Validation

```python
from pydantic import validator

class ItemCreate(BaseModel):
    title: str
    price: float
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

### 5. Response Models

```python
@app.get("/items/{item_id}", response_model=models.Item, response_model_exclude={"id"})
async def read_item_without_id(item_id: int, db: Session = Depends(get_db)):
    return await crud.get_item(db=db, item_id=item_id)
```

## Running the Application

### Development Mode

```bash
uvicorn main:app --reload
```

- Server runs on `http://localhost:8000`
- Auto-reloads on code changes
- Access docs at `http://localhost:8000/docs`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn with Uvicorn Workers

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Requirements.txt

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
aiosqlite==0.19.0
pydantic==2.5.0
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |
| POST | `/items/` | Create a new item |
| GET | `/items/` | Get all items (with pagination) |
| GET | `/items/{item_id}` | Get a specific item |
| PUT | `/items/{item_id}` | Update an item |
| DELETE | `/items/{item_id}` | Delete an item |
| GET | `/health` | Health check |

## Example API Usage

### Using cURL

```bash
# Create an item
curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"title":"Laptop","description":"High-performance laptop","price":999.99,"is_available":true}'

# Get all items
curl -X GET "http://localhost:8000/items/"

# Get a specific item
curl -X GET "http://localhost:8000/items/1"

# Update an item
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{"title":"Gaming Laptop","price":1299.99}'

# Delete an item
curl -X DELETE "http://localhost:8000/items/1"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Create an item
response = requests.post(
    f"{BASE_URL}/items/",
    json={"title": "Laptop", "description": "High-performance", "price": 999.99}
)
print(response.json())

# Get all items
response = requests.get(f"{BASE_URL}/items/")
print(response.json())

# Update an item
response = requests.put(
    f"{BASE_URL}/items/1",
    json={"title": "Gaming Laptop", "price": 1299.99}
)
print(response.json())

# Delete an item
response = requests.delete(f"{BASE_URL}/items/1")
print(response.status_code)
```

## Performance Benchmarks

FastAPI is one of the fastest Python frameworks available:

- **FastAPI**: ~20,000 requests/second
- **Starlette**: ~20,000 requests/second (FastAPI is built on Starlette)
- **Flask**: ~4,000 requests/second
- **Django**: ~2,000 requests/second

*Benchmarks vary based on hardware and configuration*

## Key Takeaways

1. **Type Hints**: FastAPI uses Python type hints for validation and documentation
2. **Async Support**: Native async/await for high performance
3. **Automatic Docs**: OpenAPI/Swagger documentation generated automatically
4. **Data Validation**: Pydantic models ensure data integrity
5. **Dependency Injection**: Clean, reusable code with DI system
6. **Standards-Based**: Built on OpenAPI, JSON Schema standards
7. **Developer Experience**: Fast to code, easy to debug, intuitive API design

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI GitHub Repository](https://github.com/tiangolo/fastapi)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

---

**Happy Coding with FastAPI! 🚀**
