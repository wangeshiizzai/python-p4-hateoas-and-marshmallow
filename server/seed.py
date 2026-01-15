#!/usr/bin/env python3

from faker import Faker
from app import app, db
from models import Newsletter

with app.app_context():

    fake = Faker()

    # Delete all existing records
    Newsletter.query.delete()

    # Create 50 fake newsletters
    newsletters = [
        Newsletter(
            title=fake.text(max_nb_chars=20),
            body=fake.paragraph(nb_sentences=5)
        )
        for _ in range(50)
    ]

    # Add to database
    db.session.add_all(newsletters)
    db.session.commit()

    print(f"Seeded {len(newsletters)} newsletters successfully!")
