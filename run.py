import webbrowser
from DUTGrievancePortal import create_app

app = create_app()

if __name__ == '__main__':
    url = "http://127.0.0.1:5000/"
    print(f"Starting Flask app... Open {url} in your browser.")
    
    # Open the browser automatically
    webbrowser.open(url)

    app.run(debug=True, host='0.0.0.0', port=5000)
