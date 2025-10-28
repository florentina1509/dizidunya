# DiziDünya

<img width="604" height="497" alt="dizidunya-logo copy" src="https://github.com/user-attachments/assets/0a1b0413-f746-4348-9941-49388b3c893f" />

A full-stack social platform built for Turkish series fans — where users can explore, discuss, and connect over their favourite dizis.  
Created by **Florentina Ramadani**, this project brings together community features, personal watchlists, and real-time chat.

---

## Overview

**DiziDünya** is a community-based web app where users can:
- Browse Turkish series
- Add shows to their **Wishlist**, **Watchlist**, or **Currently Watching**
- Join and chat in **Communities** dedicated to each series
- Receive **real-time notifications** for new series or activity
- Manage their **Profile**, including notes and ratings for series

The app is built using a **Django REST Framework backend** and a **React frontend**, connected via REST APIs and WebSockets for live updates.

---

## Features

- **User Authentication** — Secure register/login/logout using Django Tokens  
- **Series CRUD** — Admins can add or remove Turkish series  
- **Wishlist & Watchlist** — Track what you plan to watch or are currently watching  
- **Community System** — Join, leave, and chat in group discussions  
- **Real-Time Notifications** — Bell icon updates instantly using Django Channels  
- **Responsive UI** — Modern interface built with React and styled for both desktop and mobile  

---

## Tech Stack

**Frontend:**
- React (Vite)
- Axios
- React Router
- Lucide Icons

**Backend:**
- Django & Django REST Framework
- Django Channels (WebSockets)
- SQLite (Development) / PostgreSQL (Production)

**Other Tools:**
- CORS Headers
- Daphne Server
- REST API Token Authentication

---

## Project Structure

```

dizidunya/
│
├── backend/
│   ├── core/                  # Django project setup
│   ├── main/                  # App (models, serializers, views, urls)
│   ├── db.sqlite3
│   ├── manage.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api.js
│   │   └── App.js
│   ├── package.json
│
├── media/                     # Uploaded images (series & profile)
├── dizidunya-logo.png
└── README.md

````

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/dizidunya.git
cd dizidunya
````

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Access the app at [http://localhost:3000](http://localhost:3000).

---

## Screenshots

### Landing Page

<img width="1584" height="965" alt="landingpage" src="https://github.com/user-attachments/assets/ff3741c4-111e-4fad-93b5-3acaed60744d" />

### Home Page

<img width="1648" height="992" alt="homepage" src="https://github.com/user-attachments/assets/f9361335-da14-450b-93b1-43983bc71177" />


### Communities Page

<img width="1640" height="954" alt="communitiespage" src="https://github.com/user-attachments/assets/ab81d3e6-bbfc-4188-ae66-3ccb2c5a823c" />


### Profile Page

<img width="1639" height="986" alt="profilepage" src="https://github.com/user-attachments/assets/29f456cd-6801-4842-830a-b5d2eafe2f93" />


---

##  Status

 MVP completed: Full CRUD, Auth, Communities, and Real-Time Chat
 
 Future improvements: Follow system, get series uploaded automatically and have a section where users can directly watch latest episodes

---

##  Created by

Florentina Ramadani

```
