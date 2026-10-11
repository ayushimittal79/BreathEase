from flask import Flask, render_template, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from google import genai
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import os

load_dotenv()

# ─────────────────────────────────────────────
# FLASK + VADER INIT
# ─────────────────────────────────────────────
app = Flask(__name__)
vader_analyzer = SentimentIntensityAnalyzer()

# ─────────────────────────────────────────────
# HUGGINGFACE EMOTION MODEL INIT
# Model: j-hartmann/emotion-english-distilroberta-base
# A transformer neural network fine-tuned on emotional text.
# Outputs probabilities for 7 emotions: anger, disgust, fear,
# joy, neutral, sadness, surprise.
# Downloads ~300MB on first run, then cached locally.
# ─────────────────────────────────────────────
hf_classifier = None
try:
    hf_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=None  # return all emotion scores, not just top 1
    )
    print("🤗 HuggingFace emotion model: ✅ loaded")
except Exception as e:
    print(f"⚠️  HuggingFace model failed to load: {e}. Will use VADER only.")

# ─────────────────────────────────────────────
# SPOTIFY INIT
# ─────────────────────────────────────────────
sp = None
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET")
    ))
    print("🎵 Spotify: ✅ connected")
except Exception as e:
    print(f"⚠️  Spotify init failed: {e}. Will use fallback songs.")

# ─────────────────────────────────────────────
# GEMINI INIT
# ─────────────────────────────────────────────
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
gemini_model = None
try:
    gemini_model = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    print("🤖 Gemini: ✅ connected")
except Exception as e:
    print(f"⚠️  Gemini init failed: {e}. Will use fallback activities.")


# ─────────────────────────────────────────────
# MOOD → SPOTIFY SEARCH QUERIES
# Tuned to return emotionally supportive, therapeutic music
# ─────────────────────────────────────────────
MOOD_SPOTIFY_QUERIES = {
    'depression': [
        'hopeful uplifting songs for sadness healing',
        'gentle comforting music for when you feel empty',
        'songs about finding light in dark times',
    ],
    'anxiety': [
        'calm instrumental music for anxiety relief',
        'soft peaceful songs to slow racing thoughts',
        'gentle acoustic music to reduce stress and worry',
    ],
    'numbness': [
        'emotional piano music to feel something again',
        'moving orchestral songs that bring out deep feelings',
        'deeply emotional music for dissociation and numbness',
    ],
    'calm': [
        'soft cozy acoustic songs for peaceful evenings',
        'gentle indie folk music for relaxing moments',
        'warm ambient music for contentment and peace',
    ],
    'happy': [
        'upbeat joyful feel good indie pop',
        'fun energetic songs for good mood dancing',
        'happy positive vibes feel good playlist',
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
# FALLBACK ACTIVITIES
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


# ═════════════════════════════════════════════
# ENSEMBLE MOOD DETECTION SYSTEM
# Three models, each votes on the mood.
# Final result = weighted majority vote.
#
# Weights (how much we trust each model):
#   Gemini       → 0.5  (best contextual understanding)
#   HuggingFace  → 0.3  (trained on real emotion data)
#   VADER        → 0.2  (rule-based, fast, least nuanced)
# ═════════════════════════════════════════════

# ─── Model 1: VADER ───────────────────────────
def vader_predict(text):
    """
    Rule-based lexicon model. Fast but limited — works on keyword
    matching and punctuation/capitalization heuristics.
    Returns (mood, confidence) where confidence is 0.0-1.0
    """
    text_lower = text.lower()
    scores = vader_analyzer.polarity_scores(text)
    compound = scores['compound']

    anxiety_keywords = [
        'anxious', 'anxiety', 'panic', 'panicking', 'worried', 'worrying',
        'stress', 'stressed', 'nervous', 'overwhelmed', 'scared', 'afraid',
        'fear', 'tense', 'restless', 'on edge', 'cant sleep', "can't sleep",
        'insomnia', 'racing thoughts', 'shaking', 'trembling', 'uneasy'
    ]
    depression_keywords = [
        'depressed', 'depression', 'hopeless', 'worthless', 'empty',
        'meaningless', 'pointless', 'sad', 'miserable', 'crying', 'tears',
        'devastated', 'heartbroken', 'lonely', 'isolated', 'dont care', "don't care"
    ]
    numbness_keywords = [
        'numb', 'numbness', 'dissociat', 'detached', 'detachment', 'unreal',
        'disconnected', 'zoned out', 'foggy', 'empty inside', 'feel nothing',
        'cant feel', "can't feel", 'going through the motions', 'like a robot',
        'out of body', 'derealization', 'depersonalization', 'spacing out'
    ]
    happy_keywords = [
        'happy', 'joy', 'joyful', 'excited', 'great', 'amazing', 'awesome',
        'wonderful', 'fantastic', 'love', 'blessed', 'grateful', 'thankful',
        'delighted', 'thrilled', 'ecstatic', 'cheerful', 'glad'
    ]
    calm_keywords = [
        'calm', 'peaceful', 'relaxed', 'content', 'serene', 'tranquil',
        'at ease', 'comfortable', 'okay', 'alright', 'good', 'better',
        'relieved', 'stable', 'balanced', 'centered', 'grounded'
    ]

    anxiety_count = sum(1 for k in anxiety_keywords if k in text_lower)
    depression_count = sum(1 for k in depression_keywords if k in text_lower)
    numbness_count = sum(1 for k in numbness_keywords if k in text_lower)
    happy_count = sum(1 for k in happy_keywords if k in text_lower)
    calm_count = sum(1 for k in calm_keywords if k in text_lower)

    # Keyword matches take priority
    counts = {
        'anxiety': anxiety_count,
        'depression': depression_count,
        'numbness': numbness_count,
        'happy': happy_count,
        'calm': calm_count,
    }
    max_count = max(counts.values())
    if max_count > 0:
        mood = max(counts, key=counts.get)
        confidence = min(0.4 + (max_count * 0.1), 0.9)
        return mood, confidence

    # Fall back to compound score
    if compound <= -0.6:
        return 'depression', 0.7
    elif compound <= -0.2:
        return 'anxiety', 0.6
    elif -0.2 < compound < 0.2:
        return 'numbness', 0.5
    elif 0.2 <= compound < 0.6:
        return 'calm', 0.6
    else:
        return 'happy', 0.7


# ─── Model 2: HuggingFace Transformer ────────
def huggingface_predict(text):
    """
    Neural network model (distilRoBERTa) fine-tuned on emotional text.
    Maps HuggingFace's 7 emotions → our 5 moods.
    Returns (mood, confidence) where confidence is the model's probability score.
    """
    if hf_classifier is None:
        return None, 0.0

    try:
        results = hf_classifier(text[:512])  # model max input length
        # results is a list of lists: [[{label, score}, ...]]
        scores = {r['label']: r['score'] for r in results[0]}

        # Map HuggingFace emotions → our app's 5 moods
        # HF labels: anger, disgust, fear, joy, neutral, sadness, surprise
        mood_mapping = {
            'sadness':  'depression',
            'disgust':  'depression',
            'fear':     'anxiety',
            'anger':    'anxiety',
            'neutral':  'numbness',
            'surprise': 'calm',
            'joy':      'happy',
        }

        # Find the highest scoring HF emotion
        top_hf_emotion = max(scores, key=scores.get)
        top_score = scores[top_hf_emotion]
        mapped_mood = mood_mapping[top_hf_emotion]

        # If neutral with low confidence, lean toward numbness
        if top_hf_emotion == 'neutral' and top_score < 0.4:
            return 'numbness', top_score

        return mapped_mood, top_score

    except Exception as e:
        print(f"⚠️  HuggingFace prediction error: {e}")
        return None, 0.0


# ─── Model 3: Gemini LLM ─────────────────────
def gemini_predict(text):
    """
    Large Language Model with deep contextual understanding.
    Best at nuanced states like dissociation, burnout, masked depression.
    Returns (mood, confidence) — confidence is fixed high since LLM is most trusted.
    """
    if gemini_model is None:
        return None, 0.0

    try:
        prompt = f"""You are a mental health mood classifier. Analyze the emotional state described and classify it into exactly ONE of these five moods:

- depression: sadness, hopelessness, emptiness, grief, worthlessness, crying, feeling broken
- anxiety: worry, stress, panic, fear, overthinking, nervousness, racing thoughts, restlessness  
- numbness: dissociation, feeling detached, zoned out, emotionally flat, unreal, can't feel anything, going through the motions, out of body
- calm: peaceful, relaxed, content, okay, stable, at ease, comfortable
- happy: joyful, excited, grateful, positive, energetic, cheerful, enthusiastic

Text to analyze: "{text}"

Reply with ONLY one word from this list: depression, anxiety, numbness, calm, happy
No explanation, no punctuation, just the single word."""

        response = gemini_model.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        mood = response.text.strip().lower().rstrip('.')
        if mood in ['depression', 'anxiety', 'numbness', 'calm', 'happy']:
            return mood, 0.9  # high confidence — Gemini is our most trusted model
        return None, 0.0

    except Exception as e:
        print(f"⚠️  Gemini mood prediction error: {e}")
        return None, 0.0


# ─── Ensemble Voting ─────────────────────────
def analyze_sentiment(text):
    """
    ENSEMBLE MOOD DETECTION — Three NLP models vote on the mood:

    1. VADER (weight: 0.2)
       Rule-based lexicon model. Fast, classical NLP approach.

    2. HuggingFace distilRoBERTa (weight: 0.3)
       Neural network transformer fine-tuned on emotional text.
       Understands semantic meaning, not just keywords.

    3. Gemini 2.5 Flash (weight: 0.5)
       Large Language Model with deep contextual understanding.
       Best at nuance — dissociation, burnout, masked emotions.

    Final mood = highest weighted vote score.
    Confidence % shown to user = winning score / total score.
    """

    # Safety check — always highest priority regardless of models
    text_lower = text.lower()
    critical_keywords = ['suicidal', 'suicide', 'kill myself', 'want to die',
                         'end it all', 'no reason to live', 'better off dead',
                         'cant go on', "can't go on"]
    if any(keyword in text_lower for keyword in critical_keywords):
        return 'depression', 100, {
            'vader': 'depression', 'huggingface': 'depression', 'gemini': 'depression'
        }

    # Model weights — higher = more trusted
    WEIGHTS = {
        'vader': 0.2,
        'huggingface': 0.3,
        'gemini': 0.5,
    }

    # Get each model's prediction
    vader_mood, vader_conf = vader_predict(text)
    hf_mood, hf_conf = huggingface_predict(text)
    gemini_mood, gemini_conf = gemini_predict(text)

    # Log what each model said (visible in terminal, useful for debugging)
    print(f"  🔵 VADER predicted:       {vader_mood} (conf: {vader_conf:.2f})")
    print(f"  🟠 HuggingFace predicted: {hf_mood} (conf: {hf_conf:.2f})")
    print(f"  🟢 Gemini predicted:      {gemini_mood} (conf: {gemini_conf:.2f})")

    # Weighted vote: accumulate scores per mood
    mood_scores = {'depression': 0.0, 'anxiety': 0.0, 'numbness': 0.0, 'calm': 0.0, 'happy': 0.0}

    if vader_mood:
        mood_scores[vader_mood] += WEIGHTS['vader'] * vader_conf
    if hf_mood:
        mood_scores[hf_mood] += WEIGHTS['huggingface'] * hf_conf
    if gemini_mood:
        mood_scores[gemini_mood] += WEIGHTS['gemini'] * gemini_conf

    # Pick the mood with the highest weighted score
    final_mood = max(mood_scores, key=mood_scores.get)
    total_score = sum(mood_scores.values())
    confidence_pct = round((mood_scores[final_mood] / total_score) * 100) if total_score > 0 else 0

    print(f"  ✅ Ensemble result: {final_mood} ({confidence_pct}% confidence)")

    model_votes = {
        'vader': vader_mood or 'unavailable',
        'huggingface': hf_mood or 'unavailable',
        'gemini': gemini_mood or 'unavailable',
    }

    return final_mood, confidence_pct, model_votes


# ─────────────────────────────────────────────
# SPOTIFY: Live track search
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
        random.shuffle(tracks)
        selected = tracks[:limit]
        return [
            {
                'title': t['name'],
                'artist': t['artists'][0]['name'],
                'spotify_id': t['id'],
                'album_art': t['album']['images'][1]['url'] if len(t['album']['images']) > 1 else t['album']['images'][0]['url'],
                'preview_url': t.get('preview_url'),
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
        prompt = f"""A person is feeling {mood} and wrote the following:
"{user_text}"

Write ONE short, warm, and specific coping activity suggestion for them.
- Keep it under 3 sentences
- Make it feel personal to what they wrote, not generic
- Be compassionate and direct
- Do not start with "I" or mention that you're an AI
"""
        response = gemini_model.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"⚠️  Gemini activity error: {e}")
        return random.choice(FALLBACK_ACTIVITIES[mood])


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

    print(f"\n📝 Analyzing: \"{user_input[:60]}...\"")

    # Ensemble mood detection
    mood, confidence, model_votes = analyze_sentiment(user_input)

    # Live Spotify tracks
    songs = get_spotify_tracks(mood, limit=3)

    # Gemini personalized activity
    activity = get_personalized_activity(user_input, mood)

    quote = MOOD_QUOTES[mood]

    return render_template('result.html',
                           mood=mood.capitalize(),
                           confidence=confidence,
                           model_votes=model_votes,
                           songs=songs,
                           song=songs[0] if songs else None,
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
    print("\n🌸 BreatheEase is starting...")
    print("─────────────────────────────────────")
    print("🔵 VADER:        ✅ ready (rule-based NLP)")
    print("🟠 HuggingFace: ", "✅ ready (neural network)" if hf_classifier else "⚠️  unavailable")
    print("🟢 Gemini:      ", "✅ ready (LLM)" if gemini_model else "⚠️  unavailable")
    print("🎵 Spotify:     ", "✅ ready (live search)" if sp else "⚠️  unavailable (fallback songs)")
    print("─────────────────────────────────────")
    print("✅ Server running at: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop\n")
    app.run(debug=False, host='0.0.0.0', port=5000)