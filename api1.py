import sqlite3
from fastapi import FastAPI,HTTPException

app=FastAPI()



def get_db_connection():
    conn=sqlite3.connect("owner.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    



    cursor.execute("""
               CREATE TABLE IF NOT EXISTS Owners(
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               Name TEXT,
               Email TEXT UNIQUE,
               Password TEXT,
               Role TEXT,
               Pet_Name TEXT,
               Pet_Type TEXT
                )
                """)
    
    conn.commit()
    conn.close()

@app.get("/")
def root():
   return{"message":"Welcome to PetHubzzz API"}

@app.post("/owners")
def post_owner(Name:str,Email:str,Password:str,Role:str,Pet_Name:str,Pet_Type:str):
    conn=sqlite3.connect("owner.db")
    cursor=conn.cursor()
    cursor.execute("INSERT INTO Owners (Name,Email,Password,Role,Pet_Name,Pet_Type) VALUES(?,?,?,?,?,?)",(Name,Email,Password,Role,Pet_Name,Pet_Type))
    conn.commit()
    conn.close()
    return {"Message":"Owner Added Successfully."}

@app.get("/owner")
def get_owners():
    conn=sqlite3.connect("owner.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM Owners")
    owners=cursor.fetchall()
    conn.close()
    return[dict(o) for o in owners]

@app.put("/owner/{owner_id}")
def update_owner(owner_id: int,Name: str=None,Email: str=None,Password: str=None,Role: str=None,Pet_Name: str=None,Pet_Type: str=None):
    conn=sqlite3.connect("owner.db")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM Owners WHERE Id=?",(owner_id,))
    owner=cursor.fetchone()
    if not owner:
        conn.close()
        raise HTTPException(status_code=404,detail="Owner not found")
    updates=[]
    values=[]
    if Name:
        updates.append("Name=?")
        values.append(Name)

    if Email:
        updates.append("Email=?")
        values.append(Email)

    if Password:
        updates.append("Password=?")
        values.append(Password)
    
    if Role:
        updates.append("Role=?")
        values.append(Role)

    if Pet_Name:
        updates.append("Pet_Name=?")
        values.append(Pet_Name)

    if Pet_Type:
        updates.append("Pet_Type=?")
        values.append(Pet_Type)

    if updates:
        query=f"UPDATE Owners SET {','.join(updates)} WHERE Id=?"
        values.append(owner_id)
        cursor.execute(query,tuple(values))
        conn.commit()
    conn.close()
    return{"message":f"Updates Successfully"}

@app.delete("/owner{owner_id}")
def delete_owner(owner_id:int):
    conn=sqlite3.connect("owner.db")
    cursor=conn.cursor()
    cursor.execute("DELETE FROM Owners WHERE Id=?",(owner_id,))
    conn.commit()
    rows_deleted=cursor.rowcount
    conn.close()
    if rows_deleted==0:
        raise HTTPException(status_code=404,detail="Owner Not Found")
    return{"message":f"Owner with Id {owner_id} deleted successfully"}






    




    