from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from db.database import get_connection

router = APIRouter(prefix="/api/petitions", tags=["petitions"])


class EntryCreate(BaseModel):
    date: date
    item_id: int
    books: int
    signatures: int
    is_draft: bool = False


@router.get("/items")
def get_items():
    """Get all petition types"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price_per_sig FROM items ORDER BY id")
    items = cursor.fetchall()
    conn.close()
    return {"items": items}


@router.get("/entries")
def get_entries():
    """Get all entries with earnings calculated"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT e.id, e.date, i.name as item_name, e.books, e.signatures,
               (e.signatures * i.price_per_sig) as earnings, e.is_draft
        FROM entries e
        JOIN items i ON e.item_id = i.id
        ORDER BY e.date DESC, e.id DESC
    """
    )
    entries = cursor.fetchall()
    conn.close()
    return {"entries": entries}


@router.post("/entries")
def create_entry(entry: EntryCreate):
    """Add new entry"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO entries (date, item_id, books, signatures, is_draft)
        VALUES (%s, %s, %s, %s, %s)
    """,
        (entry.date, entry.item_id, entry.books, entry.signatures, entry.is_draft),
    )
    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()
    return {"id": entry_id, "message": "Entry created"}
