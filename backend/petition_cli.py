# backend/petition_cli.py
from db.database import get_connection
from datetime import date


def get_todays_entries():
    """Get entries already logged for today"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    today = date.today()
    cursor.execute(
        """
        SELECT e.id, e.item_id, e.books, e.signatures, e.is_draft, i.price_per_sig,
               (e.signatures * i.price_per_sig) as earnings
        FROM entries e
        JOIN items i ON e.item_id = i.id
        WHERE e.date = %s
    """,
        (today,),
    )
    entries = {row["item_id"]: row for row in cursor.fetchall()}
    conn.close()
    return entries


def display_petitions():
    """Show all petitions with today's status"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price_per_sig FROM items ORDER BY price_per_sig DESC"
    )
    items = cursor.fetchall()
    conn.close()

    today_entries = get_todays_entries()

    print(f"\n📅 {date.today().strftime('%A, %B %d, %Y')}")
    print("Available Petitions:")
    print("-" * 90)

    total_sigs = 0
    total_earnings = 0

    for i, item in enumerate(items, 1):
        item_id = item["id"]
        status = ""
        if item_id in today_entries:
            entry = today_entries[item_id]
            draft = " (DRAFT)" if entry["is_draft"] else ""
            sigs = entry["signatures"]
            earnings = entry["earnings"]

            if not entry["is_draft"]:
                total_sigs += sigs
                total_earnings += earnings

            status = (
                f" ← {entry['books']} books, {sigs:3} sigs, ${earnings:7.2f}{draft}"
            )

        print(f"{i:2}. {item['name']:<15} (${item['price_per_sig']:5.2f}/sig){status}")

    print("-" * 90)
    print(f"{'TOTALS:':<45} {total_sigs:3} sigs  ${total_earnings:7.2f}")
    print("-" * 90)


def edit_entry(item, existing):
    """Edit menu for existing entry"""
    while True:
        print(f"\n📋 {item['name']}")
        print(
            f"   Current: {existing['books']} books, {existing['signatures']} sigs",
            end="",
        )
        print(" (DRAFT)" if existing["is_draft"] else "")
        print("\n   1. Update books/signatures")
        print(
            "   2. Convert to REAL"
            if existing["is_draft"]
            else "   2. Convert to DRAFT"
        )
        print("   3. Delete entry")
        print("   Enter to go back")

        choice = input("\n   Select: ").strip()

        if not choice:
            break

        if choice == "1":
            try:
                books = int(input("   New books: "))
                expected_sigs = books * item["sigs_per_book"]
                sigs_input = input(f"   New signatures [{expected_sigs}]: ").strip()
                sigs = int(sigs_input) if sigs_input else expected_sigs

                conn = get_connection("petitions")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE entries SET books = %s, signatures = %s WHERE id = %s",
                    (books, sigs, existing["id"]),
                )
                conn.commit()
                conn.close()

                existing["books"] = books
                existing["signatures"] = sigs
                print("   ✓ Updated\n")
            except ValueError:
                print("   ❌ Invalid input\n")

        elif choice == "2":
            new_status = not existing["is_draft"]
            conn = get_connection("petitions")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE entries SET is_draft = %s WHERE id = %s",
                (new_status, existing["id"]),
            )
            conn.commit()
            conn.close()

            existing["is_draft"] = new_status
            status = "DRAFT" if new_status else "REAL"
            print(f"   ✓ Converted to {status}\n")

        elif choice == "3":
            confirm = input("   Delete? [n]: ").strip().lower()
            if confirm == "y":
                conn = get_connection("petitions")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM entries WHERE id = %s", (existing["id"],))
                conn.commit()
                conn.close()
                print("   ✓ Deleted\n")
                break
            else:
                print("   ❌ Cancelled\n")


def add_entry():
    """Main loop"""
    conn = get_connection("petitions")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price_per_sig, sigs_per_book FROM items ORDER BY price_per_sig DESC"
    )
    items = cursor.fetchall()
    conn.close()

    while True:
        display_petitions()
        today_entries = get_todays_entries()

        choice = input("\nSelect petition (1-15): ").strip()

        if not choice:
            continue

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(items):
                print("❌ Invalid selection")
                continue

            item = items[idx]
            item_id = item["id"]

            if item_id in today_entries:
                edit_entry(item, today_entries[item_id])
                continue

            print(f"\n📋 {item['name']}")

            books = int(input("Books: "))
            expected_sigs = books * item["sigs_per_book"]
            sigs_input = input(f"Signatures [{expected_sigs}]: ").strip()
            sigs = int(sigs_input) if sigs_input else expected_sigs

            draft_input = input("Draft? [n]: ").strip().lower()
            draft = draft_input == "y"

            conn = get_connection("petitions")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO entries (date, item_id, books, signatures, is_draft)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (date.today(), item["id"], books, sigs, draft),
            )
            conn.commit()
            conn.close()

            status = " (DRAFT)" if draft else ""
            print(f"✓ Added: {item['name']} - {books} books, {sigs} sigs{status}\n")

        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    add_entry()
