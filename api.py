from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union
import requests
import main
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse


app = FastAPI()

app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"]
      )

class Payload(BaseModel):
    question: str
    image: Union[str, List[str], None] = None

@app.post("/api")
async def save_payload(data: Payload):

      #return {"Greeting": "Hello world!"}
      print("Starting")
      input = ""

      if not data.image:
            entry = {"text": data.question}
            input = [{"text": entry["text"]}]
      elif type(data.image) == str:
            entry = {"text": data.question, "image": data.image}
            input = [{"text": entry["text"]}] + [{"image": entry["image"]}]
      else:
           input = [{"text": entry["text"]}] + [{"image": entry} for entry in data.image]

      print("Query recieved")
      output = {
            "model": "jina-clip-v2",
            "input": input
      }

      print("Query packaged")

      JINA_API_KEY = "jina_450417f62c9248bbaef5b564ced12ccdeUV-ddpFzWUqcB-YcZnSYU7GQqTd"

      headers = {
            "Authorization": f"Bearer {JINA_API_KEY}",
            "Content-Type": "application/json"
      }

      try:
            response = requests.post("https://api.jina.ai/v1/embeddings", headers=headers, json=output)

            if response.status_code != 200:
                  raise Exception("Error from Jina API: " + response.text + ", status code: " + str(response.status_code))

      except Exception as e:
            return {"error": "Unable to reach Jina API to process your request.", "details": str(e)}

      print("JINA API accessed")

      li = [em["embedding"] for em in response.json()["data"]]

      print(li)

      ret = main.fresh_prompt(entry["text"], li) #returns the final response

      return ret


@app.get("/", response_class=HTMLResponse)
async def get_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    html_content = f"""
    <html>
        <head>
            <title>Current Time</title>
        </head>
        <body style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <div style="font-size: 10em; font-family: Arial, sans-serif;">{current_time}</div>
        </body>
    </html>
    """
    return html_content


@app.options("/api1")
async def options_handler():
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }
    return Response(status_code=204, headers=headers)
