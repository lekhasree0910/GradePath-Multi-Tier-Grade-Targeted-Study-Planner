import re
import hashlib
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_syllabus(syllabus_text, exam_category, answer_format):
    """
    Analyzes syllabus complexity using Groq API.
    Falls back to keyword-based simulation if API fails.
    """
    if not syllabus_text:
        syllabus_text = "1. Introduction to subject\n2. Fundamentals and basic review\n3. Advanced topics and applications"

    # Try to use Groq API first
    try:
        topics = _analyze_with_groq(syllabus_text, exam_category, answer_format)
        if topics:  # If we got valid results from API
            return topics
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Groq API error: {e}. Falling back to simulation.")
    
    # Fallback to original simulation method
    return _analyze_syllabus_simulation(syllabus_text, exam_category, answer_format)

def _analyze_with_groq(syllabus_text, exam_category, answer_format):
    """
    Internal function to call Groq API for syllabus analysis.
    """
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_api_key_here':
        raise ValueError("Groq API key not configured")
    
    api_url = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    model = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
    
    # Construct prompt for the AI
    prompt = f"""
    Analyze the following syllabus text and break it down into distinct topics with complexity scores.
    
    Syllabus:
    {syllabus_text}
    
    Exam Category: {exam_category}
    Answer Format: {answer_format}
    
    For each topic, provide:
    1. Topic name
    2. Complexity score (1-5, where 5 is most complex)
    3. List of subtopics or key concepts
    
    Consider the exam category and answer format when assessing complexity.
    For example, competitive exams with MCQ format may emphasize different skills.
    
    Return the result as a JSON array of objects with this structure:
    [
      {{
        "topic_name": "Topic Name",
        "complexity": 3,
        "subtopics": ["subtopic1", "subtopic2"]
      }}
    ]
    
    Only return valid JSON, no additional text.
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert educational analyst specializing in curriculum breakdown and complexity assessment."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    response = requests.post(api_url, headers=headers, json=payload, timeout=5)
    response.raise_for_status()
    
    result = response.json()
    
    # Extract the content from the response
    content = None
    if 'choices' in result and len(result['choices']) > 0:
        message = result['choices'][0].get('message', {})
        content = message.get('content')
    
    if not content:
        raise ValueError("No content in API response")
    
    # Parse the JSON response
    try:
        topics_data = json.loads(content.strip())
    except json.JSONDecodeError:
        # Try to extract JSON from text if needed
        import re
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            topics_data = json.loads(json_match.group())
        else:
            raise ValueError("Could not parse JSON from API response")
    
    # Convert to expected format
    topics = []
    for i, topic_data in enumerate(topics_data):
        topic_id = f"topic_{i+1:02d}"
        topic_name = topic_data.get('topic_name', f'Topic {i+1}')
        complexity = max(1, min(5, int(topic_data.get('complexity', 3))))
        subtopics = topic_data.get('subtopics', [])
        
        # Ensure we have at least one subtopic
        if not subtopics:
            subtopics = ["Key concepts", "Fundamentals"]
            
        topics.append({
            "topic_id": topic_id,
            "topic_name": topic_name,
            "subtopics": subtopics,
            "complexity": complexity
        })
    
    # Calculate weights based on complexity
    total_complexity = sum(t["complexity"] for t in topics)
    for topic in topics:
        topic["weight"] = round(topic["complexity"] / total_complexity, 4)
    
    return topics

def _analyze_syllabus_simulation(syllabus_text, exam_category, answer_format):
    """
    Original simulation-based syllabus analysis (fallback method).
    """
    if not syllabus_text:
        syllabus_text = "1. Introduction to subject\n2. Fundamentals and basic review\n3. Advanced topics and applications"

    # Split syllabus text into logical lines/paragraphs
    lines = [line.strip() for line in syllabus_text.split('\n') if line.strip()]
    
    topics = []
    current_topic = None
    topic_counter = 1

    for line in lines:
        # Check if line matches a numbered section e.g. "1. Mechanics" or "Unit I: Calculus" or "- Topic"
        match = re.match(r'^(?:(?:Unit|Chapter|Module|Topic)?\s*(?:[0-9]+|[A-Za-z]+|\-|\*)\.?[:\-]?\s*)(.*)', line)
        if match:
            topic_name = match.group(1).strip()
            # If the header has text, create a topic
            if topic_name:
                if current_topic:
                    topics.append(current_topic)
                
                current_topic = {
                    "topic_id": f"topic_{topic_counter:02d}",
                    "topic_name": topic_name,
                    "subtopics": [],
                    "complexity": 3,  # default
                }
                topic_counter += 1
        else:
            # If it doesn't match a header, treat it as a subtopic under the current topic
            if current_topic:
                current_topic["subtopics"].append(line)
            else:
                # If no topic is active yet, create a default one
                current_topic = {
                    "topic_id": f"topic_{topic_counter:02d}",
                    "topic_name": line,
                    "subtopics": [],
                    "complexity": 3,
                }
                topic_counter += 1

    if current_topic:
        topics.append(current_topic)

    # Handle cases where parsing found no topics
    if not topics:
        topics = [
            {
                "topic_id": "topic_01",
                "topic_name": "Core Fundamentals",
                "subtopics": ["Key concepts", "Terminology", "Overview"],
                "complexity": 2
            },
            {
                "topic_id": "topic_02",
                "topic_name": "Intermediate Theories",
                "subtopics": ["Applications", "Calculations", "Problem sets"],
                "complexity": 3
            },
            {
                "topic_id": "topic_03",
                "topic_name": "Advanced Research & Practical Integration",
                "subtopics": ["Case studies", "Synthesis", "Exams review"],
                "complexity": 5
            }
        ]

    # Keyword lists for scoring complexity
    complex_keywords = [
        "quantum", "relativity", "calculus", "differential", "integration", "advanced", "complex",
        "cryptography", "neural", "deep learning", "machine learning", "database design",
        "architecture", "analysis", "algorithm", "synthesis", "proof", "optimization", "mechanics",
        "electromagnetism", "thermodynamics"
    ]
    simple_keywords = [
        "intro", "introduction", "basic", "basics", "fundamental", "fundamentals", "history",
        "overview", "elementary", "concept", "concepts", "definition", "definitions"
    ]

    # Score each topic based on keywords in its name or subtopics
    for topic in topics:
        score = 3  # Start at Medium (3)
        combined_text = (topic["topic_name"] + " " + " ".join(topic["subtopics"])).lower()
        
        # Increase complexity for hard topics
        for kw in complex_keywords:
            if kw in combined_text:
                score = max(score, 4)
                if "advanced" in combined_text or "quantum" in combined_text or "deep" in combined_text:
                    score = 5
        
        # Decrease complexity for easy topics
        for kw in simple_keywords:
            if kw in combined_text:
                score = min(score, 2)
                if "intro" in combined_text or "history" in combined_text:
                    score = 1

        # Adjust score slightly based on Exam Category and Answer Format
        # e.g., Competitive MCQ exams increase complexity slightly; practical oral exams adjust
        if exam_category == 'Competitive':
            score = min(score + 1, 5)
        elif exam_category == 'Vocational' or answer_format == 'Oral':
            score = max(score - 1, 1)

        topic["complexity"] = max(1, min(5, score))  # Ensure bounds

    # Compute weights based on complexity
    # Higher complexity = more weight/time allocation
    total_complexity = sum(t["complexity"] for t in topics)
    for topic in topics:
        topic["weight"] = round(topic["complexity"] / total_complexity, 4)

    return topics

def get_chat_response(message, context=""):
    """
    Get a response from the Groq API for a chat message.
    """
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_api_key_here':
        raise ValueError("Groq API key not configured")
    
    api_url = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    model = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
    
    # We'll use the same structure as before: system and user messages.
    system_message = "You are a helpful study assistant for the GradePath platform. You help students with their study plans, progress, and course-related questions."
    if context:
        system_message += "\n\nContext about the user: {}".format(context)

    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    
    # Extract the content from the response
    content = None
    if 'choices' in result and len(result['choices']) > 0:
        message = result['choices'][0].get('message', {})
        content = message.get('content')
    
    if not content:
        raise ValueError("No content in API response")
    
    return content.strip()


def get_syllabus_hash(syllabus_text):
    """
    Generate a SHA-256 hash of the syllabus text to check for cached analyses.
    """
    return hashlib.sha256(syllabus_text.encode('utf-8')).hexdigest()

def get_chat_response(message, context=""):
    """
    Get a response from the Groq API for a chat message.
    Falls back to rule-based responses if API is unavailable.
    """
    if not message:
        return "I didn't receive a message. How can I help you with your studies?"
    
    # Prepare prompt for the AI - we want it to act as a study assistant
    system_prompt = """You are a helpful study assistant for the GradePath application. 
    You help students with their study plans, progress tracking, and general academic questions.
    Keep your responses concise, encouraging, and focused on studying. 
    If you don't know something related to study planning, be honest about your limitations."""
    
    # Try to use Groq API
    try:
        api_key = os.getenv('GROK_API_KEY')
        if not api_key or api_key == 'your_grok_api_key_here':
            raise ValueError("Groq API key not configured")
        
        api_url = os.getenv('GROK_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
        model = os.getenv('GROK_MODEL', 'mixtral-8x7b-32768')
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # Extract the assistant's message
        if 'choices' in result and len(result['choices']) > 0:
            message_text = result['choices'][0].get('message', {}).get('content', '').strip()
            if message_text:
                return message_text
        
        # If we get here, the response format was unexpected
        raise ValueError("Unexpected response format from Groq API")
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Chatbot error: {e}")
        # Fallback to a simple rule-based response for common queries
        user_lower = message.lower()
        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your study buddy. How can I assist you with your studies today?"
        elif any(word in user_lower for word in ['progress', 'how am i', 'am i on track']):
            return "I'd love to check your progress, but I need you to have an active study plan first. Try creating a plan in the Customize section!"
        elif any(word in user_lower for word in ['study', 'what should i study', 'next']):
            return "Based on your current plan, focus on the topics scheduled for today. Check your Student Dashboard for your daily goals."
        elif any(word in user_lower for word in ['break', 'rest', 'timeout']):
            return "Remember to take regular breaks! The Pomodoro technique (25 minutes work, 5 minutes break) can help maintain focus."
        elif any(word in user_lower for word in ['thank', 'thanks']):
            return "You're welcome! Keep up the great work on your studies!"
        else:
            return "I'm here to help with your study planning and progress tracking. Try asking about your current study plan, what to study next, or general study tips!"
