import sqlite3
conn=sqlite3.connect("pethub.db")
cursor=conn.cursor()
try:
    cursor.execute("ALTER TABLE Users ADD COLUMN Status TEXT DEFAULT 'Pending'")
    print("Added Status column to Users Table")
except sqlite3.OperationalError:
    print("Status Column already exists in Users Table")

try:
    cursor.execute("ALTER TABLE Vets ADD COLUMN Certificate TEXT")
    print("Added certificate column to Vets table.")
except sqlite3.OperationalError:
    print("Certificate column is already exist in Vets table.")


try:
    cursor.execute("ALTER TABLE ServiceProviders ADD COLUMN Certificate TEXT")
    print("Added certificate column to ServiceProviders table.")
except sqlite3.OperationalError:
    print("Certificate column is already exist in ServiceProviders table.")

conn.commit()
conn.close()
print("Migration Complete")


