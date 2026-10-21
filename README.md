# Campus Estate & Facilities Management System

**Group E**
- Ramyashree Priyadarshani
- Lopamudra Swain
- Akankshya Priyadarsini Mallick

## Project overview
A Flask + SQLite web application prototype for automating college estate-office work: room allocation, maintenance requests, asset inventory, and summary reports.

## Features
- Dashboard with room, availability, open maintenance, and asset counts
- Add rooms and update allocation status / assignee
- Log maintenance requests and update their status
- Register assets with unique asset tags and condition
- Summary reports for rooms, maintenance and asset condition
- Local SQLite database created automatically with sample records on first run

## Run locally
1. Install Python 3.10 or newer.
2. Extract this folder and open a terminal in it.
3. Create and activate a virtual environment (recommended):
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the application: `python app.py`
6. Open `http://127.0.0.1:5000` in your browser.

The app uses demo/sample data. Replace it with your college's real data only after obtaining authorization. This is a classroom prototype, not a production-ready system. Before deployment, add authentication/roles, CSRF protection, input validation, backups, audit logs, and secure configuration.

## Screenshots
The UI is a working local application. To create authentic screenshots for your lab record, run the application and capture the Dashboard, Room Allocation, Maintenance, Asset Management and Reports pages. Mockup illustrations should be labelled as prototypes; do not present mockups as screenshots of a running app.
