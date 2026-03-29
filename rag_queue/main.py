from server import app

import uvicorn
from dotenv import load_dotenv

load_dotenv()


def main():
    uvicorn.run(app, host="localhost", port=8080)


if __name__ == "__main__":
    main()
