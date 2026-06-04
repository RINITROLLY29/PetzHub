# 🐾 PetHub – Pet Care & Appointment Management System

PetHub is a console-based Python application designed to manage pet care services, including vet appointments, service providers, and community interaction.

---

##  Features

- Multi-role system:
  - Pet Owners
  - Vets
  - Service Providers

- User authentication system
- Vet & Service Provider registration with certificate verification
- Appointment booking with time-slot validation
- Admin approval system for users
- Community posts (pet care tips, discussions)
- Notification system for updates
- Profile management (update/delete)

---

##  Tech Stack

- Python
- SQLite3 (Database)
- FastAPI (Basic API layer)
- Regex (validation)
- CLI-based interface

---

##  Project Structure

- `PetzHub.py` → Main application (CLI system)
- `petzhubApi.py` → FastAPI CRUD operations
- `migrate_db.py` → Database migration script
- `requirement.txt` → Dependencies list

---

## ▶️ How to Run

```bash
python PetzHub.py
