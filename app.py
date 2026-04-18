from flask import Flask, render_template, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Spotify setup
sp = None
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET")
    ))
except Exception as e:
    print(f"⚠️  Spotify init failed: {e}. Will use fallback songs.")

# Gemini setup
gemini_model = None
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print(f"⚠️  Gemini init failed: {e}. Will use fallback activities.")


# ─────────────────────────────────────────────
# MOOD → SPOTIFY SEARCH QUERIES
# These are tuned to return supportive, therapeutic music
# ─────────────────────────────────────────────
MOOD_SPOTIFY_QUERIES = {
    'depression': [
        'uplifting hopeful healing songs',
        'you are not alone emotional support music',
        'songs about getting through hard times',
    ],
    'anxiety': [
        'calm anxiety relief peaceful music',
        'relaxing stress relief instrumental',
        'soothing music for overthinking',
    ],
    'numbness': [
        'emotional reconnect feeling music',
        'songs to feel something again',
        'moving emotional music',
    ],
    'calm': [
        'peaceful ambient gentle calm music',
        'cozy relaxing feel good songs',
        'soft acoustic feel good music',
    ],
    'happy': [
        'joyful upbeat happy songs',
        'feel good energetic fun music',
        'positive vibes happy playlist',
    ]
}

# ─────────────────────────────────────────────
# FALLBACK SONGS (used if Spotify API is unavailable)
# ─────────────────────────────────────────────
FALLBACK_SONGS = {
    'depression': [
        {'title': "It's OK by Nightbird", 'spotify_id': '2UD9HQpP5Jtawn6zraPl6f'},
        {'title': 'Fight Song by Rachel Platten', 'spotify_id': '37f4ITSlgPX81ad2EvmVQr'},
        {'title': 'Breathe Me by Sia', 'spotify_id': '7jqzZyJJLrpkRFYGpkqSK6'},
    ],
    'anxiety': [
        {'title': 'Control by Halsey', 'spotify_id': '3SKzTIl9mW0DadTys9SFo3'},
        {'title': 'Out of the Woods by Taylor Swift', 'spotify_id': '1OcSfkeCg9hRC2sFKB4IMJ'},
        {'title': 'Pick Up The Phone by Henry', 'spotify_id': '6Z1IBgysq1FfSzhQWUdvAc'},
    ],
    'numbness': [
        {'title': 'Numb by Linkin Park', 'spotify_id': '2nLtzopw4rPReszdYBJU6h'},
        {'title': 'The Sound of Silence by Simon & Garfunkel', 'spotify_id': '3YfS47QufnLDFA71FUsgCM'},
        {'title': 'Hurt by Nine Inch Nails', 'spotify_id': '27tX58NOpv1YKQ0abW7EPy'},
    ],
    'calm': [
        {'title': 'Runaway by Aurora', 'spotify_id': '1v1oIWf2Xgh54kIWuKsDf6'},
        {'title': 'To Build a Home by The Cinematic Orchestra', 'spotify_id': '54KFQB6N4pn926IUUYZGzK'},
        {'title': 'Banana Pancakes by Jack Johnson', 'spotify_id': '0BgbobvykXxEvxo2HhCuvM'},
    ],
    'happy': [
        {'title': 'Live While We Are Young by One Direction', 'spotify_id': '6Vh03bkEfXqekWp7Y1UBRb'},
        {'title': 'I Like Me Better by Lauv', 'spotify_id': '1wjzFQodRWrPcQ0AnYnvQ9'},
        {'title': 'Night Changes by One Direction', 'spotify_id': '5O2P9iiztwhomNh8xkR9lJ'},
    ],
}

# ─────────────────────────────────────────────
# FALLBACK ACTIVITIES (used if Gemini is unavailable)
# ─────────────────────────────────────────────
FALLBACK_ACTIVITIES = {
    'depression': [
        "Take a 5-minute walk outside and notice three things you can see, hear, and feel.",
        "Write down one small thing you accomplished today, no matter how minor.",
        "Call or text someone you trust and share how you're feeling.",
    ],
    'anxiety': [
        "Try the 4-7-8 breathing technique: breathe in for 4 counts, hold for 7, exhale for 8. Repeat 4 times.",
        "Ground yourself: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
        "Write down your worries on paper, then fold it up and set it aside for now.",
    ],
    'numbness': [
        "Hold an ice cube in your hand for 30 seconds to reconnect with physical sensations.",
        "Do 10 jumping jacks or dance to one song to activate your body and mind.",
        "Smell something strong like coffee, mint, or citrus to awaken your senses.",
    ],
    'calm': [
        "Take 5 minutes to practice gratitude: list three things you're thankful for today.",
        "Enjoy a cup of herbal tea mindfully, focusing on the warmth and taste.",
        "Journal about what's going well in your life right now.",
    ],
    'happy': [
        "Share your positive energy! Send an encouraging message to someone who might need it.",
        "Capture this moment: write in a journal about what's making you happy right now.",
        "Make a list of things that brought you joy this week.",
    ],
}

MOOD_QUOTES = {
    'depression': '"You are not your thoughts. You are the observer of your thoughts." - Anonymous',
    'anxiety': '"Anxiety is like a rocking chair. It gives you something to do but gets you nowhere." - Jodi Picoult',
    'numbness': '"Feeling nothing is still feeling something. You are still here, and that matters." - Anonymous',
    'calm': '"Peace comes from within. Do not seek it without." - Buddha',
    'happy': '"Happiness is not by chance, but by choice." - Jim Rohn',
}


# ─────────────────────────────────────────────
# SPOTIFY: Live track search
# Returns list of dicts: {title, artist, spotify_id, album_art}
# ─────────────────────────────────────────────
def get_spotify_tracks(mood, limit=3):
    if sp is None:
        return _format_fallback_songs(mood)

    try:
        query = random.choice(MOOD_SPOTIFY_QUERIES[mood])
        results = sp.search(q=query, type='track', limit=10)
        tracks = results['tracks']['items']

        if not tracks:
            return _format_fallback_songs(mood)

        # Shuffle and pick `limit` tracks for variety on each visit
        random.shuffle(tracks)
        selected = tracks[:limit]

        return [
            {
                'title': t['name'],
                'artist': t['artists'][0]['name'],
                'spotify_id': t['id'],
                'album_art': t['album']['images'][1]['url'] if len(t['album']['images']) > 1 else t['album']['images'][0]['url'],
                'preview_url': t.get('preview_url'),  # 30-sec preview, may be None
            }
            for t in selected
        ]
    except Exception as e:
        print(f"⚠️  Spotify search error: {e}")
        return _format_fallback_songs(mood)


def _format_fallback_songs(mood):
    songs = FALLBACK_SONGS.get(mood, FALLBACK_SONGS['calm'])
    return [
        {
            'title': s['title'],
            'artist': '',
            'spotify_id': s['spotify_id'],
            'album_art': None,
            'preview_url': None,
        }
        for s in songs
    ]


# ─────────────────────────────────────────────
# GEMINI: Personalized activity suggestion
# ─────────────────────────────────────────────
def get_personalized_activity(user_text, mood):
    if gemini_model is None:
        return random.choice(FALLBACK_ACTIVITIES[mood])

    try:
        prompt = f"""
A person is feeling {mood} and wrote the following:
"{user_text}"

Write ONE short, warm, and specific coping activity suggestion for them.
- Keep it under 3 sentences
- Make it feel personal to what they wrote, not generic
- Be compassionate and direct
- Do not start with "I" or mention that you're an AI
"""
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️  Gemini error: {e}")
        return random.choice(FALLBACK_ACTIVITIES[mood])


# ─────────────────────────────────────────────
# SENTIMENT ANALYSIS (VADER + keywords, unchanged from original)
# ─────────────────────────────────────────────
def analyze_sentiment(text):
    text_lower = text.lower()

    critical_keywords = {
        'depression': ['suicidal', 'suicide', 'kill myself', 'want to die', 'end it all',
                       'no reason to live', 'better off dead', 'cant go on', "can't go on"]
    }
    for mood, keywords in critical_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return mood

    scores = analyzer.polarity_scores(text)
    compound = scores['compound']

    anxiety_keywords = [
        'anxious', 'anxiety', 'panic', 'panicking', 'worried', 'worrying', 'worry',
        'stress', 'stressed', 'stressing', 'stressful', 'nervous', 'nervousness',
        'overwhelmed', 'overwhelming', 'scared', 'afraid', 'fear', 'fearful',
        'tense', 'tension', 'restless', 'on edge', 'uneasy', 'apprehensive',
        'cant sleep', "can't sleep", 'insomnia', 'racing thoughts', 'heart racing',
        'cant breathe', "can't breathe", 'hyperventilating', 'shaking', 'trembling'
    ]
    depression_keywords = [
        'depressed', 'depression', 'hopeless', 'hopelessness', 'worthless',
        'empty', 'emptiness', 'meaningless', 'pointless', 'numb', 'numbness',
        'sad', 'sadness', 'miserable', 'down', 'low', 'blue', 'unhappy',
        'crying', 'tears', 'devastated', 'heartbroken', 'lonely', 'alone',
        'isolated', 'cant feel', "can't feel", 'dont care', "don't care"
    ]
    anger_keywords = [
        'angry', 'anger', 'mad', 'furious', 'rage', 'enraged', 'livid',
        'irritated', 'irritation', 'frustrated', 'frustration', 'annoyed',
        'annoying', 'pissed', 'pissed off', 'hate', 'hating', 'fed up',
        'sick of', 'cant stand', "can't stand", 'infuriated', 'outraged'
    ]
    happy_keywords = [
        'happy', 'happiness', 'joy', 'joyful', 'excited', 'excitement',
        'great', 'amazing', 'awesome', 'wonderful', 'fantastic', 'excellent',
        'love', 'loving', 'blessed', 'grateful', 'thankful', 'appreciate',
        'delighted', 'thrilled', 'ecstatic', 'elated', 'cheerful', 'glad'
    ]
    calm_keywords = [
        'calm', 'calming', 'peaceful', 'peace', 'relaxed', 'relaxing',
        'content', 'contentment', 'serene', 'serenity', 'tranquil', 'tranquility',
        'at ease', 'comfortable', 'fine', 'okay', 'alright', 'good', 'better',
        'relieved', 'relief', 'stable', 'balanced', 'centered', 'grounded'
    ]

    anxiety_count = sum(1 for k in anxiety_keywords if k in text_lower)
    depression_count = sum(1 for k in depression_keywords if k in text_lower)
    anger_count = sum(1 for k in anger_keywords if k in text_lower)
    happy_count = sum(1 for k in happy_keywords if k in text_lower)
    calm_count = sum(1 for k in calm_keywords if k in text_lower)

    if anxiety_count > 0:
        return 'anxiety'
    if anger_count > 0:
        return 'anxiety'
    if depression_count > 0 and compound <= 0.1:
        return 'depression'
    if happy_count > 0 and compound >= 0.0:
        return 'happy'
    if calm_count > 0 and compound >= -0.1:
        return 'calm'

    if compound <= -0.6:
        return 'depression'
    elif compound <= -0.2:
        return 'anxiety'
    elif -0.2 < compound < 0.2:
        return 'numbness'
    elif 0.2 <= compound < 0.6:
        return 'calm'
    else:
        return 'happy'


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/mood-test')
def mood_test():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    user_input = request.form.get('mood_text', '')

    if not user_input.strip():
        return render_template('index.html', error="Please share how you're feeling.")

    if len(user_input.strip()) < 10:
        return render_template('index.html',
                               error="Please write at least 10 characters to help us understand your feelings better.")

    # Detect mood
    mood = analyze_sentiment(user_input)

    # Get live Spotify tracks for this mood
    songs = get_spotify_tracks(mood, limit=3)

    # Get Gemini-personalized activity
    activity = get_personalized_activity(user_input, mood)

    # Quote (static, per mood)
    quote = MOOD_QUOTES[mood]

    return render_template('result.html',
                           mood=mood.capitalize(),
                           songs=songs,                  # NEW: list of songs
                           song=songs[0] if songs else None,  # kept for backward compat
                           activity=activity,
                           quote=quote,
                           user_text=user_input)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('home.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('home.html'), 500

if __name__ == '__main__':
    print("🌸 BreatheEase is starting...")
    print("🎵 Spotify live search:", "✅ enabled" if sp else "⚠️  disabled (check env vars)")
    print("🤖 Gemini activities:", "✅ enabled" if gemini_model else "⚠️  disabled (check env vars)")
    print("✅ Server running at: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop the server")