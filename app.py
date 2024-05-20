"""
Install the Google AI Python SDK

pip install google-generativeai python-dotenv tweepy

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
import tweepy

load_dotenv()

# Configure Google Generative AI with the API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Configure Twitter API
TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
TWITTER_API_SECRET_KEY = os.environ["TWITTER_API_SECRET_KEY"]
TWITTER_BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]
TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
twitter_api = tweepy.API(auth)
client = tweepy.Client( TWITTER_BEARER_TOKEN,TWITTER_API_KEY, TWITTER_API_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, wait_on_rate_limit=True )

# Template from the GEMINI quickstart
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]

system_instruction = """
1. Use a friendly and conversational tone.
2. Structure each post with a headline, body, hashtags, call to action or fact, and sources.
3. Headline format: "How [Name] Rose to Fame: [Key Point]"
4. Body format: "Did you know [Name] got famous by [brief explanation]? [Additional detail]."
5. End an intriguing fact.
6. Example post:
   - Headline: "How Emma Stone Rose to Fame: Breakthrough Role in 'Easy A'"
   - Body: "\n\nDid you know Emma Stone got famous by starring in the hit comedy 'Easy A'? This role showcased her comedic talent and catapulted her to stardom, leading to major roles in films like 'La La Land' and 'The Amazing Spider-Man'."
   - Fun fact Fact: "\n\nFun fact: Emma Stone changed her name from Emily to Emma because of the Screen Actors Guild!" 
7. This is a twitter tweet, so markdown syntax does not work. Separate the headline, body, and fact with a single #
8. Make sure the body is NEVER over 280 characters.
"""


model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
  system_instruction=system_instruction,
)

current_dir = os.path.dirname(__file__)
celebrities_csv_path = os.path.join(current_dir, 'celebrities.csv')
tweet_log_path = os.path.join(current_dir, 'tweet_log.txt')

def get_random_celebrity():
    """Select a random celebrity from the CSV file, ensuring they haven't been tweeted about."""
    df = pd.read_csv(celebrities_csv_path)
    tweeted_celebrities = get_tweeted_celebrities()
    
    available_celebrities = df[~df['Name'].isin(tweeted_celebrities)]
    if available_celebrities.empty:
        print("No more celebrities left to tweet about.")
        return None
    
    random_celebrity = available_celebrities.sample(n=1).iloc[0]
    return random_celebrity['Name']

def get_tweeted_celebrities():
    """Get the list of celebrities that have already been tweeted about."""
    if not os.path.exists(tweet_log_path):
        return []
    
    with open(tweet_log_path, 'r') as file:
        tweeted_celebrities = file.read().splitlines()
    
    return tweeted_celebrities

def log_tweeted_celebrity(celebrity):
    """Log the name of the celebrity that has been tweeted about."""
    with open(tweet_log_path, 'a') as file:
        file.write(f"{celebrity}\n")


def generate_response(celebrity):
    """Generate a response using the generative AI model."""
    chat_session = model.start_chat(
        history=[{"role": "user", "parts": [f"How did {celebrity} become famous?"]}]
    )
    response = chat_session.send_message(f"How did {celebrity} become famous?")
    return response.text

def post_to_twitter_thread(text):
    """Post the given text to Twitter as a thread."""
    try:
        chunks = text.split('#')
        last_tweet_id = None

        for chunk in chunks:
            tweet = client.create_tweet(text=chunk, in_reply_to_tweet_id=last_tweet_id)
            last_tweet_id = tweet.data["id"]
            print("Successfully posted tweet part")

    except tweepy.errors.TweepyException as e:
        print(f"Error posting tweet: {e}")

def generate_and_post_tweet():
    """Generate and post a tweet about how a celebrity became famous."""
    try:
        celebrity = get_random_celebrity()
        if not celebrity:
            return
        
        response_text = generate_response(celebrity)
        post_to_twitter_thread(response_text)
        log_tweeted_celebrity(celebrity)
    except Exception as e:
        print(f"Error processing {celebrity}: {e}")

generate_and_post_tweet()