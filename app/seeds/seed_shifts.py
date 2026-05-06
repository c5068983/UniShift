from app.db.connection import get_db_connection

def seed_shifts():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("🔥 seed_shifts() is running")

    try:
        cursor.executemany("""
            INSERT INTO shifts (
                userId,
                date,
                title,
                job_description,
                company_name,
                start_datetime,
                end_datetime,
                city,
                post_code,
                hourly_rate,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [

            (1, "2026-05-02", "Cafe Morning Shift",
             "Serve customers and manage orders",
             "Cafe Nero",
             "2026-05-10 09:00:00", "2026-05-10 13:00:00",
             "Sheffield", "S1 1AA", 12.5, "Open"),

            (2, "2026-05-02", "Library Assistant",
             "Help students with books",
             "University Library",
             "2026-05-19 10:00:00", "2026-05-19 16:00:00",
             "Sheffield", "S2 2BB", 11.0, "Accepted"),

            (3, "2026-05-03", "Delivery Rider",
             "Food delivery work",
             "Just Eat",
             "2026-05-03 14:00:00", "2026-05-03 20:00:00",
             "Sheffield", "S3 3CC", 14.0, "Accepted"),

            (1, "2026-05-03", "Retail Assistant",
             "Customer support in store",
             "Tesco",
             "2026-05-18 16:00:00", "2026-05-18 22:00:00",
             "Sheffield", "S4 4DD", 13.0, "Open"),

            (2, "2026-05-04", "Warehouse Picker",
             "Pick and pack items",
             "Amazon",
             "2026-05-15 08:00:00", "2026-05-15 16:00:00",
             "Manchester", "M1 1AE", 13.5, "Open"),

            (3, "2026-05-04", "Event Staff",
             "Assist live event operations",
             "NEC Events",
             "2026-05-04 12:00:00", "2026-05-04 20:00:00",
             "Birmingham", "B1 2AA", 14.0, "Accepted"),

            (1, "2026-05-05", "Cafe Barista",
             "Prepare coffee",
             "Costa",
             "2026-05-05 08:00:00", "2026-05-05 12:00:00",
             "Sheffield", "S1 4AA", 12.0, "Open"),

            (2, "2026-05-05", "Stock Assistant",
             "Manage store stock",
             "Sainsbury's",
             "2026-05-17 09:00:00", "2026-05-17 15:00:00",
             "Sheffield", "S6 1AA", 11.5, "Open"),

            (3, "2026-05-06", "Parcel Sorting",
             "Sort packages",
             "Royal Mail",
             "2026-05-14 06:00:00", "2026-05-14 14:00:00",
             "Leeds", "LS1 2AB", 13.0, "Accepted"),

            (1, "2026-05-06", "Customer Support",
             "Handle customer queries",
             "Teleperformance",
             "2026-05-06 10:00:00", "2026-05-06 18:00:00",
             "Sheffield", "S10 2TN", 12.5, "Cancelled"),

            (2, "2026-05-07", "Hotel Reception",
             "Front desk work",
             "Hilton",
             "2026-05-07 15:00:00", "2026-05-07 23:00:00",
             "Manchester", "M60 7HA", 14.5, "Cancelled")
        ])

        conn.commit()
        print("✅ seed_shifts() completed successfully")

    except Exception as e:
        print("❌ ERROR in seed_shifts:", e)

    finally:
        cursor.close()
        conn.close()