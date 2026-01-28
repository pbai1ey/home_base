from fastapi import APIRouter
from db.database import get_connection

router = APIRouter(prefix="/api/home", tags=["home"])


@router.get("/")
def get_home_stats():
    """Get home page stats"""
    conn = get_connection("homelab")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE page_visits SET visit_count = visit_count + 1 WHERE page_name = 'home'"
    )
    conn.commit()

    cursor.execute("SELECT page_name, visit_count, last_visit FROM page_visits")
    pages = cursor.fetchall()

    conn.close()
    return {"pages": pages}
