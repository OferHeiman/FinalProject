from app import app, db, models

if __name__ == '__main__':
    db.create_all()
    app.run()
