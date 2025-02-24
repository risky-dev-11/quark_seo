from app import create_app

flask_app = create_app()

if __name__ == "__main__":
    #from waitress import serve
    #serve(flask_app, host="0.0.0.0", port=5000) # for prod
    flask_app.run(debug=True) #for development

# Next Implementation steps: add screenshot, more and more specific improvement suggestions, wiki and links to it, fix comments & other stuff in html (picture on log in page), server routing with log in and registration system - false password redirect to error site instead of outputting a error, etc.  

# an bewertungsparameter wirtschaftlichkeit - wie kunden gewinnnen, etc. mit einbauen

# wissenschaftliche neutrale ausarbeitung der grundlagen von seo

# wirtschaftliche betrachtung

# wo habe ich fehler gemacvht und wo habe ich draus gelernt

