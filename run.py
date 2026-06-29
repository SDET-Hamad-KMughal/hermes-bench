from app import create_app

# Instantiate the application using our factory pattern
app = create_app()

if __name__ == '__main__':
    # Run the local development server on debug mode for rapid prototyping
    app.run(debug=True, host='127.0.0.1', port=5000)