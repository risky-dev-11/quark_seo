from app import create_app

flask_app = create_app()

if __name__ == "__main__":
    from waitress import serve
    serve(flask_app, host="0.0.0.0", port=5000) # for prod
    #flask_app.run(debug=True) #for development