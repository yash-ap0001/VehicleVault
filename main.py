from app import app

# For Vercel deployment
app = app

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
