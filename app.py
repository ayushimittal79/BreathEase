
from flask import Flask, render_template, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random

# Initialize Flask application
app = Flask(__name__)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Recommendations dictionary - stores songs and activities for each mood
RECOMMENDATIONS = {
    'depression': {
        'songs': [
            {
                'title': 'Its OK by Nightbird', 
                'spotify': 'https://open.spotify.com/track/2UD9HQpP5Jtawn6zraPl6f?si=d5770969d5354696',
                'type': 'spotify'
            },
            {
                'title': 'Reasons To Stay by Kate Vogel', 
                'spotify': 'https://open.spotify.com/embed/track/0Em410NMTZ6CPDOtHMK46Z?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'Fight Song by Rachel Platten', 
                'spotify': 'https://open.spotify.com/embed/track/37f4ITSlgPX81ad2EvmVQr?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'A Little Too Much by Shawn Mendes',
                'spotify': 'https://open.spotify.com/embed/track/1T7AiFL9ruKKwlONN35Vh0?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'Breathe Me by Sia',
                'spotify': 'https://open.spotify.com/embed/track/7jqzZyJJLrpkRFYGpkqSK6?utm_source=generator',
                'type': 'spotify'
            }
        ],
        'activities': [
            "Take a 5-minute walk outside and notice three things you can see, hear, and feel.",
            "Write down one small thing you accomplished today, no matter how minor.",
            "Call or text someone you trust and share how you're feeling.",
            "Practice gentle stretching for 5 minutes while focusing on your breath.",
            "Listen to this calming music and allow yourself to just be present."
        ],
        'quote': '"You are not your thoughts. You are the observer of your thoughts." - Anonymous'
    },
    'anxiety': {
        'songs': [
            {
                'title': 'Pick Up The Phone by Henry', 
                'spotify': 'https://open.spotify.com/embed/track/6Z1IBgysq1FfSzhQWUdvAc?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'Control by Halsey', 
                'spotify': 'https://open.spotify.com/embed/track/3SKzTIl9mW0DadTys9SFo3?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'Out of the woods by Taylor Swift', 
                'spotify': 'https://open.spotify.com/embed/track/1OcSfkeCg9hRC2sFKB4IMJ?utm_source=generator',
                'type': 'spotify'
            }
        ],
        'activities': [
            "Try the 4-7-8 breathing technique: Breathe in for 4 counts, hold for 7, exhale for 8. Repeat 4 times.",
            "Ground yourself using the 5-4-3-2-1 method: Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.",
            "Stretch your body gently for 2 minutes, focusing on releasing tension in your shoulders and neck.",
            "Write down your worries on paper, then fold it up and put it away for now.",
            "Progressive muscle relaxation: Tense and release each muscle group from toes to head."
        ],
        'quote': '"Anxiety is like a rocking chair. It gives you something to do but gets you nowhere." - Jodi Picoult'
    },
    'numbness': {
        'songs': [
            {
                'title': 'Numb by Linkin Park', 
                'spotify': 'https://open.spotify.com/embed/track/2nLtzopw4rPReszdYBJU6h?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'Hurt by Nine Inch Nails', 
                'spotify': 'https://open.spotify.com/embed/track/27tX58NOpv1YKQ0abW7EPy?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'The Sound of Silence by Simon & Garfunkel', 
                'spotify': 'https://open.spotify.com/embed/track/3YfS47QufnLDFA71FUsgCM?utm_source=generator',
                'type': 'spotify'
            }
        ],
        'activities': [
            "Hold an ice cube in your hand for 30 seconds to reconnect with physical sensations.",
            "Engage in a creative activity: doodle, color, or write whatever comes to mind without judgment.",
            "Do 10 jumping jacks or dance to one song to activate your body and mind.",
            "Smell something strong like coffee, mint, or citrus to awaken your senses.",
            "Take a warm or cold shower and focus on how the water feels on your skin."
        ],
        'quote': '"Feeling nothing is still feeling something. You are still here, and that matters." - Anonymous'
    },
    'calm': {
        'songs': [
            {
                'title': 'Runaway by Aurora', 
                'spotify': 'https://open.spotify.com/embed/track/1v1oIWf2Xgh54kIWuKsDf6?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'To Build a Home by The Cinematic Orchestra ', 
                'spotify': 'https://open.spotify.com/embed/track/54KFQB6N4pn926IUUYZGzK?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'Banana Pancakes by Jack Johnson', 
                'spotify': 'https://open.spotify.com/embed/track/0BgbobvykXxEvxo2HhCuvM?utm_source=generator',
                'type': 'spotify'
            }
        ],
        'activities': [
            "Take 5 minutes to practice gratitude: list three things you're thankful for today.",
            "Enjoy a cup of herbal tea mindfully, focusing on the warmth and taste.",
            "Spend 10 minutes reading something that inspires you or brings you joy.",
            "Journal about what's going well in your life right now.",
            "Do a short meditation or simply sit in silence for 5 minutes."
        ],
        'quote': '"Peace comes from within. Do not seek it without." - Buddha'
    },
    'happy': {
        'songs': [
            {
                'title': 'Live While We Are Young by One Direction', 
                'spotify': 'https://open.spotify.com/embed/track/6Vh03bkEfXqekWp7Y1UBRb?utm_source=generator',
                'type': 'spotify'
            },
            {
                'title': 'I Like My Better by Lauv', 
                'spotify': 'https://open.spotify.com/embed/track/1wjzFQodRWrPcQ0AnYnvQ9',
                'type': 'spotify'
            },
            {
                'title': 'Night Changes by One Direction', 
                'spotify': 'https://open.spotify.com/embed/track/5O2P9iiztwhomNh8xkR9lJ?utm_source=generator',
                'type': 'spotify'            }
        ],
        'activities': [
            "Share your positive energy! Send an encouraging message to someone who might need it.",
            "Capture this moment: write in a journal about what's making you happy right now.",
            "Move your body joyfully - dance, go for a run, or do your favorite physical activity.",
            "Make a list of things that brought you joy this week.",
            "Take a moment to appreciate this feeling and remember it for tougher days."
        ],
        'quote': '"Happiness is not by chance, but by choice." - Jim Rohn'
    }
}

def analyze_sentiment(text):
    """
    Advanced sentiment analysis using VADER + keyword detection
    
    VADER (Valence Aware Dictionary and sEntiment Reasoner) is specifically
    designed for social media and emotional text. It understands:
    - Intensifiers: "very stressed" vs "stressed"
    - Capitalization: "ANGRY" vs "angry"
    - Punctuation: "sad!!!" vs "sad"
    - Negations: "not happy" is negative
    
    Returns one of five moods: depression, anxiety, numbness, calm, happy
    """
    
    # Convert text to lowercase for case-insensitive keyword matching
    text_lower = text.lower()
    
    # STEP 1: Priority keyword detection for critical mental health terms
    # These take absolute priority for safety reasons
    critical_keywords = {
        'depression': ['suicidal', 'suicide', 'kill myself', 'want to die', 'end it all', 
                      'no reason to live', 'better off dead', 'cant go on', "can't go on"]
    }
    
    for mood, keywords in critical_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return mood
    
    # STEP 2: Get VADER sentiment scores
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']  # Range: -1 (most negative) to +1 (most positive)
    neg = scores['neg']           # Negative score (0 to 1)
    neu = scores['neu']           # Neutral score (0 to 1)
    pos = scores['pos']           # Positive score (0 to 1)
    
    # STEP 3: Enhanced keyword detection for specific emotions
    # This provides better accuracy than VADER alone
    
    # ANXIETY keywords (stress, worry, fear, panic)
    anxiety_keywords = [
        'anxious', 'anxiety', 'panic', 'panicking', 'worried', 'worrying', 'worry',
        'stress', 'stressed', 'stressing', 'stressful', 'nervous', 'nervousness',
        'overwhelmed', 'overwhelming', 'scared', 'afraid', 'fear', 'fearful',
        'tense', 'tension', 'restless', 'on edge', 'uneasy', 'apprehensive',
        'cant sleep', "can't sleep", 'insomnia', 'racing thoughts', 'heart racing',
        'cant breathe', "can't breathe", 'hyperventilating', 'shaking', 'trembling'
    ]
    
    # DEPRESSION keywords (sadness, hopelessness, emptiness)
    depression_keywords = [
        'depressed', 'depression', 'hopeless', 'hopelessness', 'worthless',
        'empty', 'emptiness', 'meaningless', 'pointless', 'numb', 'numbness',
        'sad', 'sadness', 'miserable', 'down', 'low', 'blue', 'unhappy',
        'crying', 'tears', 'devastated', 'heartbroken', 'lonely', 'alone',
        'isolated', 'cant feel', "can't feel", 'dont care', "don't care"
    ]
    
    # ANGER keywords (frustration, rage, irritation)
    anger_keywords = [
        'angry', 'anger', 'mad', 'furious', 'rage', 'enraged', 'livid',
        'irritated', 'irritation', 'frustrated', 'frustration', 'annoyed',
        'annoying', 'pissed', 'pissed off', 'hate', 'hating', 'fed up',
        'sick of', 'cant stand', "can't stand", 'infuriated', 'outraged'
    ]
    
    # HAPPY keywords (joy, excitement, contentment)
    happy_keywords = [
        'happy', 'happiness', 'joy', 'joyful', 'excited', 'excitement',
        'great', 'amazing', 'awesome', 'wonderful', 'fantastic', 'excellent',
        'love', 'loving', 'blessed', 'grateful', 'thankful', 'appreciate',
        'delighted', 'thrilled', 'ecstatic', 'elated', 'cheerful', 'glad'
    ]
    
    # CALM keywords (peace, relaxation, contentment)
    calm_keywords = [
        'calm', 'calming', 'peaceful', 'peace', 'relaxed', 'relaxing',
        'content', 'contentment', 'serene', 'serenity', 'tranquil', 'tranquility',
        'at ease', 'comfortable', 'fine', 'okay', 'alright', 'good', 'better',
        'relieved', 'relief', 'stable', 'balanced', 'centered', 'grounded'
    ]
    
    # STEP 4: Count keyword matches for each emotion
    anxiety_count = sum(1 for keyword in anxiety_keywords if keyword in text_lower)
    depression_count = sum(1 for keyword in depression_keywords if keyword in text_lower)
    anger_count = sum(1 for keyword in anger_keywords if keyword in text_lower)
    happy_count = sum(1 for keyword in happy_keywords if keyword in text_lower)
    calm_count = sum(1 for keyword in calm_keywords if keyword in text_lower)
    
    # STEP 5: Make decision based on keyword matches + VADER scores
    
    # If anxiety keywords found
    if anxiety_count > 0:
        return 'anxiety'
    
    # If anger keywords found (anger maps to anxiety - similar physiological arousal)
    if anger_count > 0:
        return 'anxiety'
    
    # If depression keywords found AND text is negative/neutral
    if depression_count > 0 and compound <= 0.1:
        return 'depression'
    
    # If happy keywords found AND text is positive
    if happy_count > 0 and compound >= 0.0:
        return 'happy'
    
    # If calm keywords found AND text is positive/neutral
    if calm_count > 0 and compound >= -0.1:
        return 'calm'
    
    # STEP 6: Fall back to VADER compound score if no clear keywords
    # These thresholds are based on VADER documentation and testing
    
    if compound <= -0.6:
        # Very negative → depression
        return 'depression'
    elif compound <= -0.2:
        # Moderately negative → anxiety
        return 'anxiety'
    elif -0.2 < compound < 0.2:
        # Neutral → numbness
        return 'numbness'
    elif 0.2 <= compound < 0.6:
        # Moderately positive → calm
        return 'calm'
    else:
        # Very positive → happy
        return 'happy'

# Route: Homepage
@app.route('/')
def home():
    """Render the homepage with navigation"""
    return render_template('home.html')

# Route: Mood Test Page (where user inputs their feelings)
@app.route('/mood-test')
def mood_test():
    """Render the mood test input page"""
    return render_template('index.html')

# Route: Process mood input and show results
@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze user's mood from the form submission
    Return personalized recommendations based on detected emotion
    """
    # Get user input from form
    user_input = request.form.get('mood_text', '')
    
    # Validate input - check if empty
    if not user_input.strip():
        return render_template('index.html', error="Please share how you're feeling.")
    
    # Validate input - check minimum length for accurate analysis
    if len(user_input.strip()) < 10:
        return render_template('index.html', 
                             error="Please write at least 10 characters to help us understand your feelings better.")
    
    # Analyze sentiment using our enhanced VADER function
    mood = analyze_sentiment(user_input)
    
    # Get recommendations for the detected mood
    recs = RECOMMENDATIONS[mood]
    
    # Randomly select one song and one activity for variety
    # Users can refresh to get different recommendations
    selected_song = random.choice(recs['songs'])
    selected_activity = random.choice(recs['activities'])
    selected_quote = recs['quote']
    
    # Render results page with all the personalized recommendations
    return render_template('result.html', 
                         mood=mood.capitalize(),
                         song=selected_song,
                         activity=selected_activity,
                         quote=selected_quote,
                         user_text=user_input)

# Route: About Page
@app.route('/about')
def about():
    """Render the about page with app information"""
    return render_template('about.html')

# Route: Help Page
@app.route('/help')
def help_page():
    """Render the help page with FAQs and resources"""
    return render_template('help.html')

# Error handlers for better user experience
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors - page not found"""
    return render_template('home.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors - internal server error"""
    return render_template('home.html'), 500

# Run the Flask application
if __name__ == '__main__':
    # Debug mode provides helpful error messages during development
    # Set debug=False when deploying to production
    print("🌸 BreatheEase is starting...")
    print("📊 Using VADER sentiment analysis for accurate emotion detection")
    print("✅ Server running at: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
