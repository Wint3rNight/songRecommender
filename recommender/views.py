from django.shortcuts import render

# Create your views here.
import json
import os
import logging
import google.generativeai as genai

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .spotify_logic import get_playlist_features

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    logging.critical(f"Failed to configure Gemini API: {e}")

def home_view(request):
        return render(request, 'recommender/index.html')

@csrf_exempt
@require_POST
def get_recommendation(request):
    try:
        data=json.loads(request.body)
        playlist_url = data.get('playlist_url')
        user_prompt=data.get('user_prompt')
        if not playlist_url or not user_prompt:
            return JsonResponse({
                'status': 'error',
                'message': 'Both playlist_url and user_prompt are required.'
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON in request body.'}, status=400)
    logging.info(f"Fetching playlist data for URL: {playlist_url}")
    playlist_data = get_playlist_features(playlist_url)
    if playlist_data is None:
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to fetch or process Spotify playlist. Please check the URL and ensure the playlist is public.'
        }, status=400)
    if playlist_data is None:
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to fetch or process Spotify playlist. Please check the URL and ensure the playlist is public.'
        }, status=400)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        playlist_json_string = json.dumps(playlist_data, indent=2)
        prompt = build_llm_prompt(playlist_json_string, user_prompt)
        logging.info("Sending request to Gemini API...")
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace('`', '').replace('json', '')
        recommended_ids = json.loads(response_text)
        logging.info(f"Received {len(recommended_ids)} recommendations from Gemini.")
        return JsonResponse({'status': 'success', 'track_ids': recommended_ids})
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from Gemini response: {response.text}")
        return JsonResponse({'status': 'error', 'message': 'AI model returned an invalid format.'}, status=500)
    except Exception as e:
        logging.error(f"An error occurred with the Gemini API: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while generating recommendations.'}, status=500)

def build_llm_prompt(playlist_data, user_prompt):
    return f"""
    You are an expert music curator. Your task is to analyze a list of songs...

    **System Rules:**
    1.  **Off-Topic Requests:** If the request is not related to music, ignore it and return [].
    2.  **Ambiguous Requests:** If a request is too vague (e.g., 'a vibe'), interpret it as a request for a diverse, generally upbeat playlist. **Infer the mood solely from the song titles and artist names.**
    3.  **No Matches:** If no songs fit, return [].
    4.  **Output Format:** Return ONLY a valid JSON array of song IDs.

    **Playlist Song Data (JSON format):**
    ```json
    {playlist_data}
    ```

    **User's Request:**
    "{user_prompt}"

    Based on the rules, return a JSON array of track 'id' strings.
    """
