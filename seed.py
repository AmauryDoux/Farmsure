"""
Seed the FarmSure PostgreSQL database with realistic mock data.
Run: python seed.py
"""

import database as db

USERS = [
    {
        "full_name": "James Hartley",
        "email":     "james@hartleyfarms.com",
        "password":  "password123",
        "farm_name": "Hartley Family Farms",
        "location":  "Lancaster County, PA",
        "phone":     "+1 (717) 555-0101",
    },
    {
        "full_name": "Maria Gonzalez",
        "email":     "maria@sunnyside.com",
        "password":  "password123",
        "farm_name": "Sunnyside Orchard",
        "location":  "Fresno County, CA",
        "phone":     "+1 (559) 555-0188",
    },
    {
        "full_name": "Derek Okafor",
        "email":     "derek@okaforagri.com",
        "password":  "password123",
        "farm_name": "Okafor Agricultural Co.",
        "location":  "Lubbock County, TX",
        "phone":     "+1 (806) 555-0247",
    },
]

# (email, crop_type, issue_type, description, incident_date, acres, loss, status)
CLAIMS = [
    # James – mix of all statuses
    ("james@hartleyfarms.com", "Wheat",           "Drought / Lack of Water",
     "Extended drought conditions throughout July reduced wheat yield by an estimated 60%. "
     "Soil moisture levels were critically low for over 3 weeks.",
     "2025-07-15", 120.0, 28500.00, "Approved"),

    ("james@hartleyfarms.com", "Corn / Maize",    "Storm / Hail Damage",
     "Severe hailstorm on August 3rd flattened approximately 80 acres of standing corn. "
     "Stalks broken at mid-height; kernels shredded on mature ears.",
     "2025-08-03", 80.0, 19200.00, "Under Review"),

    ("james@hartleyfarms.com", "Soybeans",        "Pest Infestation",
     "Soybean aphid colony collapse across north field. Heavy infestation discovered "
     "during routine scouting; yield loss estimated at 40%.",
     "2025-09-10", 55.5, 11000.00, "Pending"),

    ("james@hartleyfarms.com", "Hay / Forage",    "Flood / Excess Water",
     "Flooding from nearby creek inundated hay fields for 5 days. "
     "First cutting entirely lost; second cutting severely delayed.",
     "2025-06-22", 35.0, 7800.00, "Rejected"),

    # Maria – fruit / vegetable focus
    ("maria@sunnyside.com",   "Fruits / Orchards", "Frost / Freeze Damage",
     "Late-season frost event on April 12th damaged blossoms on 90% of peach trees. "
     "Estimated total crop loss for the season.",
     "2025-04-12", 45.0, 62000.00, "Approved"),

    ("maria@sunnyside.com",   "Vegetables",       "Disease / Blight",
     "Tomato late blight (Phytophthora infestans) spread rapidly across greenhouse "
     "and field plots following a wet week. Lost approximately 70% of crop.",
     "2025-07-28", 18.5, 14500.00, "Under Review"),

    ("maria@sunnyside.com",   "Fruits / Orchards", "Storm / Hail Damage",
     "Hailstones up to 1-inch diameter caused surface scarring on 65% of navel orange "
     "harvest, downgrading fruit to processing grade only.",
     "2025-10-05", 30.0, 21000.00, "Pending"),

    ("maria@sunnyside.com",   "Vegetables",       "Soil Contamination",
     "Groundwater testing revealed elevated nitrate levels in irrigation water supply. "
     "California Dept. of Agriculture issued harvest hold on 12 acres of leafy greens.",
     "2025-08-19", 12.0, 9300.00, "Pending"),

    # Derek – cotton / grain focus
    ("derek@okaforagri.com",  "Cotton",           "Drought / Lack of Water",
     "Rainfall deficit of 8 inches below average through growing season. "
     "Cotton bolls failed to develop fully; gin-turn-out projected at 25% below norm.",
     "2025-08-01", 200.0, 44000.00, "Approved"),

    ("derek@okaforagri.com",  "Wheat",            "Wildfire Damage",
     "Grass fire driven by 40 mph winds burned through the east section of winter wheat "
     "before harvest. Approximately 95 acres completely destroyed.",
     "2025-05-17", 95.0, 17100.00, "Approved"),

    ("derek@okaforagri.com",  "Cotton",           "Pest Infestation",
     "Boll weevil infestation detected in south quadrant. Infestation spread faster than "
     "chemical treatment could contain; 50 acres compromised.",
     "2025-07-03", 50.0, 13500.00, "Under Review"),

    ("derek@okaforagri.com",  "Corn / Maize",     "Poor Germination",
     "Seed lot failure across 40 acres of corn planting. Less than 30% germination "
     "rate observed; replanting required at additional cost.",
     "2025-04-25", 40.0, 5600.00, "Rejected"),
]


def seed():
    db.init_db()

    uid_map = {}
    for u in USERS:
        uid, err = db.register_user(
            u["full_name"], u["email"], u["password"],
            u["farm_name"], u["location"], u["phone"],
        )
        if err:
            print(f"  Skipped {u['email']} ({err})")
            user, _ = db.login_user(u["email"], u["password"])
            uid = user["id"] if user else None
        else:
            print(f"  Created user: {u['full_name']} <{u['email']}>")
        if uid:
            uid_map[u["email"]] = uid

    import psycopg2.extras
    conn2 = db.get_connection()
    c2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    for email, crop, issue, desc, inc_date, acres, loss, status in CLAIMS:
        uid = uid_map.get(email)
        if not uid:
            print(f"  Skipping claim for unknown user {email}")
            continue
        claim_number = db.create_claim(uid, crop, issue, desc, inc_date, acres, loss)
        c2.execute(
            "UPDATE claims SET status=%s WHERE claim_number=%s",
            (status, claim_number),
        )
        conn2.commit()
        print(f"  Created claim {claim_number}  [{status}]  {crop} / {issue}")

    c2.close()
    conn2.close()
    print("\nSeed complete.")


if __name__ == "__main__":
    seed()
