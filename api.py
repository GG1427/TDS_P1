from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
from main import *


app = FastAPI()

app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
      )

class Payload(BaseModel):
      question: str
      image: Optional[List[str]] = None

@app.post("/api")
async def save_payload(data: Payload):

      entry = {"text": data.question, "image": data.image or []}

      output = {
            "model": "jina-clip-v2",
            "input": [{"text": entry["text"]}] + [{"image": url} for url in entry["image"]]
      }

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

      li = [em["embedding"] for em in response["data"]]

      ret = fresh_prompt(entry["text"], li) #returns the final response

      return ret