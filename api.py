from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
app = FastAPI()

class Review(BaseModel):
   text:str

class Analysis(BaseModel):
   label: str
   score: int
   theme: str

def analyze_review(text: str) -> Analysis:
   """Analyze review text with Gemini and return the structured result."""
   client = genai.Client()
   response = client.models.generate_content(
      model="gemini-3.8-flash",
      contents=(
        "Analyze this customer review. \n"
        "label must be 'positive', 'negative', or 'neutral'. \n"
        "score  must be a number from 1 (very bad) to 5 (very good). \n"
        "theme must be ONE lowercase word for the main topic "
        "(for example: delivery, taste, price, service, quality). \n" 
        f"Review: {text}"
      ),
      config=types.GenerateContentConfig(
         response_mime_type="application/json",
         response_schema=Analysis,
      ),
   )
   if response.parsed is None:
      raise ValueError("The model did not return a valid analysis.")
   return response.parsed

@app.post("/analyze", response_model=Analysis)
def analyze(review: Review):
   return analyze_review(review.text)
