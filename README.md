# BidMaster

BidMaster is a Django-based online auction platform with separate experiences for administrators, sellers, and bidders. Sellers can create auction listings, admins can review and approve products, and bidders can browse live auctions, place bids, and receive auction outcome notifications.

## Hosted Project

Live demo: [https://mybidmaster.pythonanywhere.com/](https://mybidmaster.pythonanywhere.com/)

## Overview

The platform is built around a custom `Members` model instead of relying only on Django auth groups. Users sign up with a role, log in with email and password, and are routed to a dashboard based on their access level. The application also includes email notifications, product lifecycle automation, and an AI-powered auction assistant.

## Key Features

- Role-based dashboards for admin, seller, and bidder users.
- Seller auction creation with image uploads, reserve price, buy-now price, and approval workflow.
- Admin moderation for pending, live, sold, and inactive auctions.
- Bidder browsing by category, auction detail pages, bidding, and winner notifications.
- Automatic auction closure handling for expired listings.
- Email alerts for registration, winning bids, and auction updates.
- In-app chatbot for auction and platform guidance.

## User Roles

### Admin

- Reviews pending auctions.
- Approves or rejects seller listings.
- Views platform-wide summaries for users, products, live auctions, sold items, and inactive items.
- Lists all sellers and bidders.

### Seller

- Creates a new auction listing with product details and an uploaded image.
- Views live, pending, sold, and inactive listings.
- Withdraws pending listings or deletes listings when needed.
- Receives notifications when bids arrive or when a product is sold.

### Bidder

- Browses live auctions by category.
- Views product details and places bids.
- Sees winning auctions and received platform messages.
- Uses the chatbot for help with auction-related questions.

## How the Auction Flow Works

1. A seller submits a new product listing.
2. An admin approves the listing and it becomes live.
3. Bidders browse live auctions and place bids.
4. The current price, bid count, and winner data are updated as bids arrive.
5. If a bid reaches the buy-now price, the auction ends immediately as sold.
6. If the auction expires, the management command closes it based on bid activity and reserve logic.
7. Winner and seller notifications are stored in the message system and sent by email.

## Tech Stack

- Python
- Django 5.2.x
- SQLite for local development
- HTML templates
- CSS and JavaScript for the frontend
- Pillow for image uploads
- Requests for chatbot API calls
- python-dotenv for environment variable loading

## Main Data Models

- `Members`: stores user profile data, contact number, password, and role.
- `Products`: stores auction details such as category, description, prices, timestamps, images, status, bidders, winner, and bid count.
- `Messages`: stores seller and bidder notifications, including bid alerts, sold notifications, and winner messages.

## Important Project Pages

- Landing page and authentication pages.
- Admin dashboard and moderation pages.
- Seller dashboard, auction submission form, live auctions, pending approvals, inactive items, and sold items.
- Bidder dashboard, category browser, auction detail page, winner history, and bid messages.
- Chatbot page and API endpoint.

## Project Structure

```text
BidMaster/
├── manage.py
├── db.sqlite3
├── bidding/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── management/commands/handle_expired_bids.py
│   ├── migrations/
│   ├── templates/accounts/
│   └── static/accounts/
└── media/auctions/images/
```

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Run migrations.
4. Start the development server.

Example commands:

```bash
python -m venv venv
venv\Scripts\activate
pip install Django requests python-dotenv Pillow
python manage.py migrate
python manage.py runserver
```

## Environment Configuration

The project uses email delivery and a Groq-backed chatbot. Make sure the following are configured before running the app:

- `GROQ_API_KEY` for the chatbot endpoint.
- Gmail SMTP credentials for outbound email notifications.
- A valid app password if you keep Gmail SMTP enabled.

If you plan to deploy the project, move secrets out of source code and into environment variables.

## Useful Commands

```bash
python manage.py createsuperuser
python manage.py handle_expired_bids
python manage.py runserver
```

## Notes

- Uploaded auction images are stored under `media/auctions/images/`.
- Static assets for the app live in `accounts/static/accounts/`.
- Templates for the app live in `accounts/templates/accounts/`.
- The application uses role checks in views to keep admin, seller, and bidder areas separated.