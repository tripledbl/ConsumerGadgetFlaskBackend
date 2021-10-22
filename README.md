Set up (after cd into project directory):
    - install dependencies (cmd/powershell)
        - pip install -r requirements.txt
    - initialize env vars
        - $env:FLASK_APP = "app"
        - $env:FLASK_ENV = "development"
    - run on local server (http://127.0.0.1:5000/)
        - flask run
