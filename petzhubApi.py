import sqlite3
from fastapi import FastAPI,HTTPException
app=FastAPI()


def get_db_connection():
    conn=sqlite3.connect("pethub.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    conn.commit()
    conn.close()

@app.get("/")
def root():
    return {"Message":"Welcome to PetzHub API"}

@app.post("/pet")
def post_user(Name:str,Email:str,Password:str,Role:str,Pet_Name:str,Pet_Type:str):
    conn=sqlite3.connect("pethub")
    cursor=conn.cursor()
    cursor.execute("INSERT INTO Users (Name,Email,Password,Role,Pet_Name,Pet_Type) VALUES(?,?,/,?,?,?)",(Name,Email,Password,Role,Pet_Name,Pet_Type))
    conn.commit()
    conn.close()
    return {"Message":"Users Added Successfully!"}

@app.get("/pet")
def get_users():
    conn=sqlite3.connect("pethub.db")
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM Users")
    users=cursor.fetchall()
    conn.close()
    return[dict(u) for u in users]

@app.put("/pet/{User_Id}")
def update_user(User_Id:int,Name:str=None,Email:str=None,Password:str=None,Role:str=None,Pet_Name:str=None,Pet_Type:str=None):
    conn=sqlite3.connect("pethub.db")
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Id=?",(User_Id,))
    u=cursor.fetchone()
    if not u:
        conn.close()
        raise HTTPException(status_code=404,detail="User Not Found")
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
        query=f"UPDATE Users SET {','.join(updates)} WHERE Id=?"
        values.append(User_Id)
        cursor.execute(query,tuple(values))
        conn.commit()
    conn.close()
    return {"Message":f"Updated Values of {User_Id} Successfully!"}   
 
@app.delete("/pet/{User_Id}")
def delete_user(User_Id:int):
    conn=sqlite3.connect("pethub.db")
    cursor=conn.cursor()
    cursor.execute("DELETE FROM Users WHERE Id=?",(User_Id,))
    conn.commit()
    rows_deleted=cursor.rowcount
    conn.close()
    if rows_deleted==0:
        raise HTTPException(status_code=404,detail="User Not Found!")
    return {"Message":f"User with Id {User_Id} had Deleted Successfully!"}

    

    

