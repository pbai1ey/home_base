from fastapi import APIRouter
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


@router.get("/")
def track_visit():
    """Track petitions page visit"""
    conn = get_connection("homelab")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE page_visits SET visit_count = visit_count + 1 WHERE page_name = 'petitions'"
    )
    conn.commit()
    conn.close()
    return {"status": "tracked"}


@router.get("/items")
def get_items():
    """Get active petition types only"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price_per_sig FROM items WHERE active = TRUE ORDER BY price_per_sig DESC"
    )
    items = cursor.fetchall()
    conn.close()
    return {"items": items}


@router.get("/items/all")
def get_all_items():
    """Get ALL petition types (including inactive) - for admin"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price_per_sig, sigs_per_book, active FROM items ORDER BY price_per_sig DESC"
    )
    items = cursor.fetchall()
    conn.close()
    return {"items": items}


@router.put("/items/{item_id}/toggle")
def toggle_item_active(item_id: int):
    """Toggle active status of a petition type"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET active = NOT active WHERE id = %s", (item_id,))
    cursor.execute("SELECT active FROM items WHERE id = %s", (item_id,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return {"id": item_id, "active": result["active"]}


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


@router.put("/entries/{entry_id}")
def update_entry(entry_id: int, entry: EntryCreate):
    """Update existing entry"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE entries 
        SET books = %s, signatures = %s, is_draft = %s
        WHERE id = %s
    """,
        (entry.books, entry.signatures, entry.is_draft, entry_id),
    )
    conn.commit()
    conn.close()
    return {"id": entry_id, "message": "Entry updated"}


@router.delete("/entries/{entry_id}")
def delete_entry(entry_id: int):
    """Delete entry"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entries WHERE id = %s", (entry_id,))
    conn.commit()
    conn.close()
    return {"id": entry_id, "message": "Entry deleted"}
