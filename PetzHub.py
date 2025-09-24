import sqlite3
import datetime
import re

#DataBase SetUp

conn=sqlite3.connect("pethub.db")
conn.row_factory=sqlite3.Row
cursor=conn.cursor()

#Tables

cursor.execute("""
               CREATE TABLE IF NOT EXISTS Users(
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               Name TEXT,
               Email TEXT UNIQUE,
               Password TEXT,
               Role TEXT,
               Pet_Name TEXT,
               Pet_Type TEXT,
               Status TEXT DEFAULT 'Pending'
               )
               """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS Vets(
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               Name TEXT,
               Speciality TEXT,
               Visiting_Time TEXT,
               Certificate TEXT
               )
               """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS ServiceProviders(
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               Name TEXT,
               Service_Type TEXT,
               Contact_Info INTEGER,
               Location TEXT,
               Certificate TEXT
               )
               """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS Appointments(
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               User_Id INTEGER,
               Vet_Id INTEGER,
               Slot TEXT,
               Status TEXT,FOREIGN KEY(User_Id) REFERENCES Users(Id),
               FOREIGN KEY(Vet_Id) REFERENCES Vets(Id)
               )
               """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS CommunityPosts(
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               User_Id INTEGER,
               Content TEXT,
               Timestamp TEXT,
               is_vet_tip INTEGER DEFAULT 0,
               FOREIGN KEY(User_Id) REFERENCES Users(id)
               )""")

cursor.execute("""
               CREATE TABLE IF NOT EXISTS Notifications(
               Id INTEGER PRIMARY KEY AUTOINCREMENT,
               User_Id INTEGER,
               Message TEXT,
               Timestamp Text,
               Status TEXT DEFAULT 'Unread',
               FOREIGN KEY(User_Id) REFERENCES Users(Id)
               )
               """)
conn.commit()

#Functions

def is_valid_email(email):
   pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
   return re.match(pattern,email) is not None

def register_user():
    print("\n---User Registration---")
    name=input("Enter Your Name: ").strip().title()

    while True:
      email=input("Enter Your Mail_Id: ").strip()
      if is_valid_email(email):
        break
      else:
       print("Invalid Email Format.\n Try Again!")
       
    password=input("Enter a Strong Password: ")
    role=input("Role (PetOwner/Vet/Service_Provider): ").strip().lower()
    pet_name=None
    pet_type=None

    if role.lower() == "petowner":
        pet_name=input("Enter Your Pet's Name: ").title()
        pet_type=input("Enter Your Pet's type (Dog/Cat/etc....): ").strip().capitalize()

    try:
        cursor.execute("INSERT INTO Users(Name,Email,Password,Role,Pet_Name,Pet_Type) VALUES (?,?,?,?,?,?)",
                       (name,email,password,role,pet_name,pet_type))
        conn.commit()
        print("Account Created")

        if role.lower() == "vet":
          speciality=input("Enter Your Specialized Area: ")
          slots=input("Enter Visiting Time (eg:- 9am-12pm,2pm-5pm): ")
          slots=slots.replace(" ","").replace(".","")
          certificate=input("Enter your Vet License/Certificate Number: ").strip()
          cursor.execute("INSERT INTO Vets(Name,Speciality,Visiting_Time,Certificate) VALUES (?,?,?,?)",
                       (name,speciality,slots,certificate))
        
          conn.commit()
          print("Profile Created Successfully!Awaiting Admin Approval.")

        elif role.lower() == "serviceprovider":
          service_type=input("Enter Service Type: ").capitalize()
          while True:
             contact_info=input("Enter Your Contact Number: ")
             if contact_info.isdigit() and len(contact_info)==10:
                break
             else:
                print("Please enter a valid 10-digit number")
          location=input("Enter Your Location: ").capitalize()
          certificate=input("Enter your Business License/Certificate Number: ").strip()
          cursor.execute("INSERT INTO ServiceProviders(Name,Service_Type,Contact_Info,Location,Certificate) VALUES (?,?,?,?,?)",
                       (name,service_type,contact_info,location,certificate))
        
          conn.commit()
          print("Service Provider profile created!Awaiting Admin Approval.")
    

    except sqlite3.IntegrityError:
      print("Email Already Exists! ")

#Login

def user_login():
   print("\n---Login---")
   email=input("Enter your email: ").strip().lower()
   password=input("Enter your password: ").strip()

   cursor.execute("SELECT * FROM Users WHERE lower(Email)=? AND password=?",(email,password))
   user=cursor.fetchone()

   if user:
      if user['Status']!="Approved":
         print(f"Your account is currently '{user['Status']}'. Please wait for Admin's approval.")
         return None
      print(f" Welcome {user['Name']}!")
      print("Logged in Successfuly.")
      return user
   else:
      print("Invalid login credentials.")
      return None

#Add Notification

def add_notification(user_id,message):
   Timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   cursor.execute("INSERT INTO Notifications (User_Id,Message,Timestamp) VALUES (?,?,?)",(user_id,message,Timestamp)) 
   conn.commit()

#View Notifications

def view_notifications(user):
   cursor.execute("""
                  SELECT Id,Message,Timestamp,Status FROM Notifications WHERE User_Id=? ORDER BY Timestamp DESC""",(user['Id'],))
   notes=cursor.fetchall()
   if notes:
      for note in notes:
         print(f"{note['Id']} - {note['Message']} ({note['Timestamp']}) Status: {note['Status']}")
         if note['Status'] =="Unread":
            cursor.execute("UPDATE Notifications SET Status='Read' WHERE Id=?",(note['Id'],))
            conn.commit()
   else:
      print("No Notifications.")

#convert to time
def convert_to_time(time_str):
   """Convert string like '9am' or '3pm' to datetime.time object.
   NOTE: requires am/pm."""
   time_str=time_str.strip().lower().replace(" ","").replace(".",":")#normalise . to :
   formats=["%I%p", "%I:%M%p"]
   for fmt in formats:
      try:
        return datetime.datetime.strptime(time_str,fmt).time()  #handles 9am, 12pm
      except ValueError:
         continue
   return None

def is_slot_in_range(slot_input,Visiting_Time):
   """Check if slot is inside any of the vet's visiting ranges."""
   slot_time=convert_to_time(slot_input)
   if not slot_time:
      return False
   
   Visiting_Time=Visiting_Time.replace(" ","").replace(".","").lower()
   ranges=Visiting_Time.split(",")
   for rng in ranges:
      try:
         start_str,end_str=rng.split("-")
         start_time=convert_to_time(start_str)
         end_time=convert_to_time(end_str)
         if start_time and end_time and start_time <= slot_time <= end_time:
            return True
      except Exception:
         continue
   return False

#Book Appointment

def book_appointment(user):
   print("\n---Book Appointment---")
   print("Book Vet")
   cursor.execute("SELECT * FROM Vets")
   vets=cursor.fetchall()

   if not vets:
      print("No vets available right now.")
      return 
   
   print("\n---Available Vets---")
   for vet in vets:
      print(f"ID: {vet['Id']}. {vet['Name']} - {vet['Speciality']} || (Visiting_Time: {vet['Visiting_Time']})")
   
   while True:
      try:
        vet_id=int(input("Enter Vet_Id to book: "))
        cursor.execute("SELECT * FROM Vets WHERE Id=?", (vet_id,))
        vet_record=cursor.fetchone()
        if vet_record:
           break
        else:
           print("Invalid Vet Id! Please select from the available list.")
      except ValueError:
         print("Please enter a valid vet_id.")
         
   while True:   
     slot=input("Enter slot (eg:-10am): ").strip().lower()

     if is_slot_in_range(slot,vet_record['Visiting_Time']):
      break
     print(f"Invalid slot! This vet is only available during {vet_record['Visiting_Time']}")


   cursor.execute("INSERT INTO Appointments (User_Id,Vet_Id,Slot,Status) VALUES (?,?,?,?)",(user['Id'],vet_id,slot,"Pending"))
   conn.commit()
   print("Successfully sent the Appointment request!")
   #send notification
   cursor.execute("SELECT Id FROM Users WHERE Name=(SELECT Name FROM Vets WHERE Id=?)",(vet_id,))
   vet_user=cursor.fetchone()

   if vet_user:
      add_notification(vet_user['Id'],f"New appointment booked by {user['Name']} for slot {slot}")

#View Appointment

def view_appointment(user):
   print("\n---Your Appointment---")
   role=user["Role"].lower()
   
   if user['Role'].lower()== "petowner":
       cursor.execute("""
            SELECT 
                Appointments.Id AS AppointmentId,
                Vets.Name AS VetName,
                Vets.Speciality,
                Appointments.Slot,
                Appointments.Status
            FROM Appointments
            JOIN Vets ON Appointments.Vet_Id = Vets.Id
            WHERE Appointments.User_Id = ?
        """, (user["Id"],))

       appointments=cursor.fetchall()


       if appointments:
         for appt in appointments:
            print(dict(appt))
       else:
            print("No Appointments")

   elif user['Role'].lower() == "vet":
      cursor.execute("SELECT Id FROM Vets WHERE Name=?",(user['Name'],))
      vet_record=cursor.fetchone()
      if vet_record:
         vet_id=vet_record['Id']
         cursor.execute("""
           SELECT Appointments.Id AS AppointmentId,
           Users.Name AS PetownerName,
           Users.Pet_Type,
           Appointments.Slot,
           Appointments.Status
           FROM Appointments JOIN Users ON Appointments.User_Id=Users.Id WHERE Appointments.Vet_Id=?""", (vet_id,))
         appointments=cursor.fetchall()
         if appointments:
            for appt in appointments:
               print(f"ID: {appt['AppointmentId']} || Owner: {appt['PetownerName']}" f"|| Pet:{appt['Pet_Type']} || Slot: {appt['Slot']} ||" f"Status: {appt['Status']}")
         else:
            print("No Appointments Found.")

      else:
        print("No Appointments Found.")

#Petowner_Manage_Appointment
def manage_appointments(user):
  while True:
   print("\n---Manage Your Appointments---")
   cursor.execute("""
                  SELECT Appointments.Id AS AppointmentId,
                  Vets.Name AS VetName,
                  Vets.Speciality,
                  Appointments.Slot,
                  Appointments.Status FROM Appointments JOIN Vets ON Appointments.Vet_Id=Vets.Id WHERE Appointments.User_Id=?""",(user["Id"],))
   appointments=cursor.fetchall()

   if not appointments:
      print("No Appointments to manage")
      return
   
   for appt in appointments:
      print(f"ID: {appt['AppointmentId']} || Vet: {appt['VetName']}" f"({appt['Speciality']}) || Slot: {appt['Slot']} || Status: {appt['Status']}")

   try:
      appt_id=int(input("Enter Appointment Id to update/cancel(or 0 to go back): "))
   except ValueError:
      print("Invalid input.Try Again!")
      continue
      

   if appt_id==0:
      break
   
   cursor.execute("SELECT * FROM Appointments WHERE Id=? AND User_Id=?",(appt_id,user['Id']))
   selected_appt=cursor.fetchone()

   if not selected_appt:
      print("Invalid Appointment Id")
      continue
   
   print("\n1. Update Slot")
   print("2. Cancel Appointment")
   choice=input("Choose option: ").strip()

   if choice=="1":
      while True:
        new_slot=input("Enter new slot (or type 'back'to cancel):").strip().lower()
        if new_slot=="back":
           print("Slot Update Cancelled.")
           return
        
        cursor.execute("SELECT Visiting_Time FROM Vets WHERE Id=?",(selected_appt['vet_id'],))
        vet=cursor.fetchone()
        if not vet:
          print("Vet not Found!")
          continue
        
        if "am" not in new_slot and "pm" not in new_slot:
           print("Please specify AM or PM (eg.,11.30am,12pm)")
           continue
        
        if is_slot_in_range(new_slot,vet['Visiting_Time']):
          cursor.execute("UPDATE Appointments SET Slot=?, Status='Pending' WHERE Id=?",(new_slot,appt_id))
          conn.commit()
          print("Appointment slot updated successfully(sent for approval again)")
          break
        else:
          print(f"Invalid slot! Vet is only available during {vet['Visiting_Time']}")

   elif choice=="2":
      confirm=input("Are you sure you want to cancel this appointment?(yes/no): ").strip().lower()
      if confirm=="yes":
        cursor.execute("DELETE FROM Appointments WHERE Id=?",(appt_id,))
        conn.commit()
        print("Appointment cancelled successfully.")
      else:
         print("Cancellation aborted.")

   elif choice=="3":
      continue
   else:
      print("Invalid Choice")
   

#Vet_Manage_Appointments

def vet_manage_appointments(user):
   cursor.execute("SELECT Id FROM Vets WHERE NAME=?",(user['Name'],))
   vet_record=cursor.fetchone()

   if not vet_record:
      print("No Vet Profile Found")
      return
   
   vet_id=vet_record['Id']
   cursor.execute("""
        SELECT Appointments.Id AS AppointmentId,Users.Id AS PetOwnerId,Users.Name AS petowner, Users.Pet_Type, Appointments.Slot
        FROM Appointments
        JOIN Users ON Appointments.User_Id = Users.Id
        WHERE Appointments.Vet_Id=? AND Appointments.Status='Pending'
    """, (vet_id,))
   
   appointments=cursor.fetchall()

   if not appointments:
      print("No Pending Appointments.")
      return
   
   for appt in appointments:
      print(f"ID: {appt['AppointmentId']} || PetOwner: {appt['petowner']} || Slot: {appt['Slot']}")
      choice=input("Approve (A) / Decline (D) /Skip (S): ").strip().upper()
      if choice == 'A':
         cursor.execute("UPDATE Appointments SET Status='Approved' WHERE Id=?",(appt['AppointmentId'],))
         add_notification(appt['PetOwnerId'], f"Your appointment for {appt['Pet_Type']} is Approved.")
         print("Appointment updated.")

      elif choice== 'D':
         cursor.execute("UPDATE Appointments SET Status='Declined' WHERE Id=?", (appt['AppointmentId'],))
         add_notification(appt['PetOwnerId'], f"Your appointment for {appt['Pet_Type']} is Declined.")
         print("Appointment updated.")
      elif choice=='S':
         print("Appointment is still Pending")
         break

      else:
         print("Invalid Choice")
         break

   conn.commit()


#Community

def post_community(user):
  while True:
   print("\n---Community---")
   print("1. Add Post ")
   print("2. View Posts in the Community")
   choice=input("Choose:- 1 / 2 : ").strip()
   if choice=='1':
      content=input("Write Your Post: \n")
      is_vet_tip=1 if user['Role'].lower()=="Vet" else 0
      Timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      cursor.execute("INSERT INTO CommunityPosts(User_Id,Content,Timestamp,is_vet_tip) VALUES (?,?,?,?)",(user['Id'],content,Timestamp,is_vet_tip))
      conn.commit()
      print("Post Added!")
      break
   elif choice=='2':
      view_community()
      break
   else:
      print("Invalid Choice,Try Again!")
      
#view community    
def view_community():
  cursor.execute("""
                  SELECT CommunityPosts.Id,Users.Name,CommunityPosts.Content,CommunityPosts.Timestamp,CommunityPosts.is_vet_tip FROM CommunityPosts JOIN Users ON CommunityPosts.user_id = Users.id ORDER BY CommunityPosts.Timestamp DESC""")  
  posts=cursor.fetchall()
  for post in posts:
     tag="[VET TIP]" if post['is_vet_tip'] else ""
     print(f"{post['Id']} - {post['Name']} {tag} ({post['Timestamp']})): {post['Content']}")

#view serviceproviders
def view_service_providers():
   print("\n---Available Service Providers---")
   cursor.execute("SELECT * FROM ServiceProviders")
   providers=cursor.fetchall()
   if providers:
      for sp in providers:
         print(f"{sp['Id']} || {sp['Name']} - {sp['Service_Type']} || phone: {sp['Contact_Info']} || Location: {sp['Location']}")
   else:
      print("No Service providers registered yet.")

#update profile
def update_profile(user):
   print("\n---Update Your Profile---")
   new_name=input(f"Enter new name (Leave blank to keep {user['Name']}): ").strip().title()
   new_password=input(f"Enter new password (Leave blank to keep current):").strip()

   if new_name:
      cursor.execute("UPDATE Users SET Name=? WHERE Id=?", (new_name,user["Id"]))
   if new_password:
      cursor.execute("UPDATE Users SET Password=? WHERE Id=?", (new_password,user["Id"]))

   #petowner extras
   if user['Role'].lower()=="petowner":
      new_pet_name=input(f"Enter new Pet's Name (Leave blank to keep {user['Pet_Name']}): ").strip().title()
      new_pet_type=input(f"Enter new Pet's Type (Leave blank to keep {user['Pet_Type']}): ").strip().capitalize()
      
      if new_pet_name:
         cursor.execute("UPDATE Users SET Pet_Name=? WHERE Id=?", (new_pet_name,user['Id']))
      if new_pet_type:
         cursor.execute("UPDATE Users SET Pet_Type=? WHERE Id=?", (new_pet_type,user['Id']))
   
   #vet extras
   elif user['Role'].lower()=="vet":
      cursor.execute("SELECT * FROM Vets WHERE Name=?",(user["Name"],))
      vet_record=cursor.fetchone()
      if not vet_record:
        print("No Vet Profile found!")
      new_speciality=input(f"Enter new Speciality (Leave blank to keep {vet_record['Speciality']}): ").strip().title()
      new_time=input(f"Enter new Visiting Time (Leave blank to keep {vet_record['Visiting_Time']}): ").strip()

      if new_speciality:
         cursor.execute("UPDATE Vets SET Speciality=? WHERE Name=?", (new_speciality,user['Name']))
      if new_time:
         cursor.execute("UPDATE Vets SET Visiting_Time=? WHERE Name=?", (new_time,user['Name']))

   #serviceprovider extras
   elif user['Role'].lower()=="serviceprovider":
      cursor.execute("SELECT * FROM ServiceProviders WHERE Name=?",(user["Name"],))
      sp=cursor.fetchone()
      if not sp:
        print("No Service Provider Profile found!")

      new_service=input(f"Enter new service type (Leave blank to keep {sp['Service_Type']}) ").strip().title()
      new_contact=input(f"Enter new contact number (Leave blank to keep {sp['Contact_Info']}):" ).strip()
      new_location=input(f"Enter new location (Leave blank to keep {sp['Location']}): ").strip().title()
      
      if new_service:
         cursor.execute("UPDATE ServiceProviders SET Service_Type=? WHERE Name=?", (new_service,user["Name"]))
      if new_contact:
         cursor.execute("UPDATE ServiceProviders SET Contact_Info=? WHERE Name=?", (new_contact,user["Name"]))
      if new_location:
         cursor.execute("UPDATE ServiceProviders SET Location=? WHERE Name=?", (new_location,user["Name"]))   

   conn.commit()
   print("Profile Updated Successfully!")


#delete profile
def delete_profile(user):
      print("\n---Delete Profile---")
      confirm=input("Are you sure you want to delete your account? (Yes/No): ").strip().lower()

      if confirm!="yes":
         print("Deletion Cancelled.")
         return
       
         
      cursor.execute("DELETE FROM Appointments WHERE User_Id=?",(user["Id"],))
      cursor.execute("DELETE FROM Notifications WHERE User_Id=?",(user["Id"],))
      cursor.execute("DELETE FROM Appointments WHERE User_Id=?",(user["Id"],))

      if user['Role'].lower()=="vet":
         cursor.execute("DELETE FROM Vets WHERE Name=?", (user["Name"],))
      elif user['Role'].lower()=="serviceprovider":
         cursor.execute("DELETE FROM ServiceProviders WHERE Name=?", (user["Name"],))

      cursor.execute("DELETE FROM Users WHERE Id=?", (user["Id"],))
      conn.commit()
      print("Your Account has been deleted.GoodBye")
      exit()

def admin_panel():
   while True:
      print("\n---Admin Panel---")
      print("1. View Pending Users")
      print("2. Approve User")
      print("3. Reject User")
      print("4. Back")
      choice=input("Enter choice: ").strip() 
      if choice=="1":
         cursor.execute("SELECT Id,Name,Email,Role,Status FROM Users WHERE Status='Pending'")
         pending=cursor.fetchall()
         if pending:
            for u in pending:
               print(dict(u))

               if u['Role'].lower()=="vet":
                  cursor.execute("SELECT Certificate FROM Vets WHERE Name=?",(u['Name'],))
                  vet_cert=cursor.fetchone()
                  print(f"Vet Certificate: {vet_cert['Certificate'] if vet_cert else 'N/A'}")
               elif u['Role'].lower()=="serviceprovider":
                  cursor.execute("SELECT Certificate FROM ServiceProviders WHERE Name=?",(u['Name'],))
                  sp_cert=cursor.fetchone()
                  print(f"Service Provider Certificate: {sp_cert['Certificate'] if sp_cert else 'N/A'}")
         else:
            print("No Pending Users.")
      
      elif choice=="2":
         uid=input("Enter User Id to Approve: ").strip()
         cursor.execute("UPDATE Users SET Status='Approved' WHERE Id=?",(uid,))
         conn.commit()
         print("User Approved")

      elif choice=="3":
         uid=input("Enter User Id to Reject: ").strip()
         cursor.execute("UPDATE Users SET Status='Rejected' WHERE Id=?",(uid,))
         conn.commit()
         print("User Rejected")

      elif choice=="4":
         break

      else:
         print("Invalid Choice! Select a valid Option.")
         
   

#Dashboard
def dashboard(user):
   role=user['Role'].lower()

   while True:
      print("\n===============DASHBOARD===============")
      print(f"Logged in as: {user['Name']} ({user['Role'].title()})")
      print("========================================")

      #petowner menu
      if role=="petowner":
        print("1. Book Appointment ")
        print("2. View Appointments ")
        print("3. Manage Appointments")
        print("4. View Service Providers ")
        print("5. Community ")
        print("6. Notifications ")
        print("7. Update Profile ")
        print("8. Delete Profile ")
        print("9. Logout ")


        choice=input("Enter Choice: ").strip()

        if choice=="1":
         book_appointment(user)

        elif choice=="2":
          view_appointment(user)

        elif choice=="3":
          manage_appointments(user)

        elif choice=="4":
          view_service_providers()

        elif choice=="5":
          post_community(user)
          view_community()

        elif choice=="6":
          view_notifications(user)

        elif choice=="7":
           update_profile(user)

        elif choice=="8":
            delete_profile(user)  

        elif choice=="9":
            break
        
        else:
          print("Invalid Choice!")

      #vet menu
      elif role=="vet":
         print("1. View Appointments ")
         print("2. Notification ")
         print("3. Manage Appointment ")
         print("4. Community ")
         print("5. Update Profile ")
         print("6. Delete Profile ")
         print("7. Logout ")
         choice=input("Enter Your Choice: ").strip()

         if choice=="1":
            view_appointment(user)

         elif choice=="2":
            view_notifications(user)

         elif choice=="3":
            vet_manage_appointments(user)

         elif choice=="4":
            post_community(user)
            view_community()

         elif choice=="5":
           update_profile(user)

         elif choice=="6":
            delete_profile(user)   

         elif choice=="7":
            break

         else:
            print("Invalid Choce!")

      #serviceprovider menu   
      elif role=="serviceprovider":
         print("1. Community ")
         print("2. Update Profile ")
         print("3. Delete Profile ")
         print("4. Logout ")

         choice=input("Enter Your Choice: ").strip()

         if choice=="1":
            post_community(user)
            view_community()

         elif choice=="2":
           update_profile(user)

         elif choice=="3":
            delete_profile(user)

         elif choice=="4":
            break

         else:
            print("Invalid Choice!")
#main
def main():
   while True:
      print("\n PetHub  ")
      print("1. Register ")
      print("2. Login ")
      print("3. Admin Login ")
      print("4. Exit " )
      choice=input("Enter your Choice: ")

      if choice=="1":
         register_user()
      elif choice=="2":
         user=user_login()
         if user:
            dashboard(user)
      elif choice=="3":
         admin_panel()
      elif choice=="4":
         print("Exiting PetHub......")
         break
      else:
         print("Invalid Choice")

if __name__=="__main__":
   main()

            

          



   




  



