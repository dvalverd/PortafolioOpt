
import logging
from config import app  
from main import create_layout

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app.layout = create_layout()

if __name__ == '__main__':
    app.run_server(debug=True)