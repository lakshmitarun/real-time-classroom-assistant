from app import app

# Vercel requires a WSGI callable
if __name__ == "__main__":
    app.run()
