from fastapi import APIRouter
from db.database import get_connection

router = APIRouter(prefix="/api/about", tags=["about"])


@router.get("/")
def track_visit():
    """Track about page visit and return user petition stats"""
    conn = get_connection("homelab")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE page_visits SET visit_count = visit_count + 1 WHERE page_name = 'about'"
    )
    conn.commit()
    conn.close()
    return {"status": "tracked"}


@router.get("/entries")
def get_all_entries():
    """Get all petition entries with filtering"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT e.id, e.date, i.name as item_name, e.books, e.signatures,
               (e.signatures * i.price_per_sig) as earnings, e.is_draft,
               i.price_per_sig
        FROM entries e
        JOIN items i ON e.item_id = i.id
        ORDER BY e.date DESC, e.id DESC
    """
    )
    entries = cursor.fetchall()
    conn.close()
    return {"entries": entries}


@router.get("/stats")
def get_stats():
    """Get overall petition statistics"""
    conn = get_connection("petitions")
    cursor = conn.cursor()

    # Total stats
    cursor.execute(
        """
        SELECT 
            COUNT(*) as total_entries,
            SUM(signatures) as total_sigs,
            SUM(signatures * (SELECT price_per_sig FROM items WHERE id = entries.item_id)) as total_earnings
        FROM entries
        WHERE is_draft = 0
    """
    )
    totals = cursor.fetchone()

    # Per petition stats
    cursor.execute(
        """
        SELECT 
            i.name,
            COUNT(*) as entry_count,
            SUM(e.signatures) as total_sigs,
            SUM(e.signatures * i.price_per_sig) as total_earnings
        FROM entries e
        JOIN items i ON e.item_id = i.id
        WHERE e.is_draft = 0
        GROUP BY i.name
        ORDER BY total_earnings DESC
    """
    )
    by_petition = cursor.fetchall()

    conn.close()
    return {"totals": totals, "by_petition": by_petition}
