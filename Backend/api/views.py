import os
import uuid
import json
from datetime import datetime, date
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import (
    db_users, db_courses, db_customization_requests,
    db_plans, db_progress, db_vault, db_admin_requests, get_next_sequence_value
)
from .ocr_util import extract_text_from_file
from .ai_engine import analyze_syllabus, get_syllabus_hash, get_chat_response
from .scheduler import generate_plans, recompress_schedule, apply_feedback_patch

# Temporary directory for uploads inside workspace
UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# MongoDB session helper
db_sessions = settings.MONGO_DB["sessions"]

def generate_session(user_doc):
    token = str(uuid.uuid4())
    db_sessions.insert_one({
        "token": token,
        "user_id": user_doc["user_id"],
        "email": user_doc["email"],
        "role": user_doc["role"],
        "full_name": user_doc["full_name"],
        "created_at": datetime.now().isoformat()
    })
    return token

def get_session_user(request):
    # Try to get token from Authorization header
    token = None
    if hasattr(request, 'headers'):
        # DRF Request
        token = request.headers.get("Authorization")
    else:
        # Django HttpRequest
        token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        # Fallback to query param or form data
        # For DRF, request.query_params and request.data
        # For Django, request.GET and request.POST
        if hasattr(request, 'query_params'):
            token = request.query_params.get("token")
        else:
            token = request.GET.get("token")
        if not token:
            if hasattr(request, 'data'):
                token = request.data.get("token")
            else:
                token = request.POST.get("token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:]
    
    session = db_sessions.find_one({"token": token})
    return session

def calculate_pace(daily_schedule, completed_topic_ids):
    """
    Computes learner's progress pace: OnTrack, Behind, or Ahead.
    """
    today = date.today()
    expected_topics = set()
    all_topics = set()

    for day in daily_schedule:
        day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        for t in day.get("topics", []):
            all_topics.add(t["topic_id"])
            if day_date <= today and not day.get("is_revision", False):
                expected_topics.add(t["topic_id"])

    # If no study days expected yet
    if not expected_topics:
        return "OnTrack"

    completed_expected = expected_topics.intersection(completed_topic_ids)
    
    # Pace classification
    if len(completed_expected) < len(expected_topics):
        return "Behind"
    elif len(completed_topic_ids) > len(expected_topics):
        return "Ahead"
    else:
        return "OnTrack"

# ----------------- Ready-Made Roadmap Seeds -----------------
def seed_courses_if_empty():
    if db_courses.count_documents({}) == 0:
        default_courses = [
            {
                "course_id": 11,
                "course_name": "Python Core",
                "category": "Software Development",
                "description": "Master Python variables, control flow, functions, OOP, and data structures.",
                "stage_count": 5,
                "stages": [
                    {"stage_number": 1, "title": "Syntax & Basics", "topics": ["Variables", "Data Types", "Conditionals"]},
                    {"stage_number": 2, "title": "Loops & Collections", "topics": ["For/While Loops", "Lists", "Tuples"]},
                    {"stage_number": 3, "title": "Data Management", "topics": ["Dictionaries", "Sets", "File Read/Write"]},
                    {"stage_number": 4, "title": "Advanced Logic", "topics": ["Functions", "Modules", "Exception Handling"]},
                    {"stage_number": 5, "title": "Object-Oriented Coding", "topics": ["Classes", "Inheritance", "Methods"]}
                ],
                "created_by": 999,
                "created_at": datetime.now().isoformat()
            },
            {
                "course_id": 12,
                "course_name": "Java Developer",
                "category": "Software Development",
                "description": "A comprehensive pathway through JVM architecture, compilation, OOP, and exceptions.",
                "stage_count": 5,
                "stages": [
                    {"stage_number": 1, "title": "Compilation & Basics", "topics": ["JVM vs JRE", "Data Types", "Operators"]},
                    {"stage_number": 2, "title": "OOP in Java", "topics": ["Classes", "Inheritance", "Polymorphism"]},
                    {"stage_number": 3, "title": "Abstractions & Packages", "topics": ["Abstract classes", "Interfaces", "Packages"]},
                    {"stage_number": 4, "title": "Data structures", "topics": ["ArrayList", "HashMap", "Generics"]},
                    {"stage_number": 5, "title": "Memory & I/O", "topics": ["Garbage Collection", "Files", "Exceptions"]}
                ],
                "created_by": 999,
                "created_at": datetime.now().isoformat()
            },
            {
                "course_id": 13,
                "course_name": "Data Analytics",
                "category": "Data Science",
                "description": "Learn SQL data management, Python Pandas, clean workflows, and visualization principles.",
                "stage_count": 5,
                "stages": [
                    {"stage_number": 1, "title": "Structured Queries (SQL)", "topics": ["Select", "Joins", "Group By", "Filters"]},
                    {"stage_number": 2, "title": "Python Processing", "topics": ["Pandas DataFrames", "Series", "Missing values"]},
                    {"stage_number": 3, "title": "Numerical Operations", "topics": ["NumPy Arrays", "Indexing", "Math functions"]},
                    {"stage_number": 4, "title": "Data Visualization", "topics": ["Matplotlib", "Seaborn", "Line/Bar Charts"]},
                    {"stage_number": 5, "title": "Descriptive Stats", "topics": ["Mean", "Median", "Standard Deviation", "Correlation"]}
                ],
                "created_by": 999,
                "created_at": datetime.now().isoformat()
            },
            {
                "course_id": 14,
                "course_name": "Machine Learning",
                "category": "Artificial Intelligence",
                "description": "Study regression algorithms, classification boundaries, cluster modeling, and validation.",
                "stage_count": 5,
                "stages": [
                    {"stage_number": 1, "title": "Supervised Regression", "topics": ["Linear Regression", "Cost function", "Gradient Descent"]},
                    {"stage_number": 2, "title": "Classification", "topics": ["Logistic Regression", "Decision Trees", "SVM"]},
                    {"stage_number": 3, "title": "Evaluation Metrics", "topics": ["Precision/Recall", "F1 Score", "ROC Curves"]},
                    {"stage_number": 4, "title": "Clustering & Analytics", "topics": ["K-Means", "PCA Dimensions", "Distance metrics"]},
                    {"stage_number": 5, "title": "Generalization", "topics": ["Overfitting", "Cross Validation", "Regularization"]}
                ],
                "created_by": 999,
                "created_at": datetime.now().isoformat()
            },
            {
                "course_id": 15,
                "course_name": "Artificial Intelligence",
                "category": "Artificial Intelligence",
                "description": "Understand basic heuristics search, logical propositions, NLP basics, and Neural Nets.",
                "stage_count": 5,
                "stages": [
                    {"stage_number": 1, "title": "Search Heuristics", "topics": ["A* search", "BFS/DFS", "State graphs"]},
                    {"stage_number": 2, "title": "Logic Frameworks", "topics": ["Propositional Logic", "First-Order Rules", "Inference"]},
                    {"stage_number": 3, "title": "Natural Language", "topics": ["Tokenization", "TF-IDF vectors", "Embeddings"]},
                    {"stage_number": 4, "title": "Artificial Neural Nets", "topics": ["Perceptrons", "Backpropagation", "Activations"]},
                    {"stage_number": 5, "title": "Ethics & Safety", "topics": ["Bias testing", "Safety margins", "Alignment principles"]}
                ],
                "created_by": 999,
                "created_at": datetime.now().isoformat()
            },
            {
                "course_id": 16,
                "course_name": "Cybersecurity",
                "category": "Systems & Network",
                "description": "Deep dive into network packet analyses, cipher algorithms, threat models, and vulnerability scanning.",
                "stage_count": 5,
                "stages": [
                    {"stage_number": 1, "title": "CIA Triad & Threats", "topics": ["Confidentiality", "Integrity", "Vulnerabilities"]},
                    {"stage_number": 2, "title": "Cryptography", "topics": ["Symmetric vs Asymmetric", "AES/RSA", "Hash validation"]},
                    {"stage_number": 3, "title": "Network Defense", "topics": ["Firewalls", "IDS/IPS", "VPN tunnels"]},
                    {"stage_number": 4, "title": "Defensive Scanning", "topics": ["Nmap", "Wireshark packet filters", "Metasploit intro"]},
                    {"stage_number": 5, "title": "Governance & Audits", "topics": ["ISO 27001", "Compliance checks", "Incident plans"]}
                ],
                "created_by": 999,
                "created_at": datetime.now().isoformat()
            },
            {
                "course_id": 17,
                "course_name": "Operating Systems",
                "category": "Systems & Network",
                "description": "Study CPU scheduler calculations, synchronization locks, memory paging, and file nodes.",
                "stage_count": 5,
                "stages": [
                    {"stage_number": 1, "title": "Processes & Threads", "topics": ["PCB structure", "Context switching", "Thread execution"]},
                    {"stage_number": 2, "title": "CPU Schedulers", "topics": ["Round Robin", "SJF", "Priority Queues"]},
                    {"stage_number": 3, "title": "Synchronization", "topics": ["Race condition", "Mutex", "Deadlock detection"]},
                    {"stage_number": 4, "title": "Virtual Memory", "topics": ["Paging", "Segmentation", "Page replacement"]},
                    {"stage_number": 5, "title": "Disk & File Nodes", "topics": ["Inodes", "SCAN/LOOK algorithms", "File structures"]}
                ],
                "created_by": 999,
                "created_at": datetime.now().isoformat()
            }
        ]
        db_courses.insert_many(default_courses)

seed_courses_if_empty()

# Static Syllabus Bank
SYLLABUS_BANK = [
    {
        "id": "bank_jee_physics",
        "name": "JEE Mains - Physics Syllabus",
        "subject": "Physics",
        "text": "1. Classical Mechanics (Newton's Laws, Gravitation, Work-Energy)\n2. Thermodynamics & Kinetic Theory of Gases\n3. Electrostatics & Magnetism\n4. Wave Optics and Wave Mechanics\n5. Modern Physics (Atomic Nucleus, Dual Nature of Matter)"
    },
    {
        "id": "bank_java_core",
        "name": "Java Programming Fundamentals",
        "subject": "Java",
        "text": "1. Java Syntax and Basic Constructs\n2. Object Oriented Programming (Inheritance, Polymorphism, Interfaces)\n3. Exception Handling and Logging\n4. Collections Framework (List, Map, Set)\n5. Concurrency & Thread Coordination"
    },
    {
        "id": "bank_data_science",
        "name": "Data Analytics & Statistics Essentials",
        "subject": "Data Analytics",
        "text": "1. Basic SQL (Queries, Joins, Aggregations)\n2. Pandas DataFrames & NumPy Arrays\n3. Data Cleaning and Imputation\n4. Exploratory Data Visualization (Matplotlib, Seaborn)\n5. Statistical Inference (Probability, Hypothesis testing)"
    }
]

# Admin access code (in production, load from env variable)
ADMIN_ACCESS_CODE = "GRADEPATH_ADMIN_2024"

# ----------------- MODULE 1: AUTHENTICATION -----------------
@api_view(['POST'])
def auth_register(request):
    data = request.data
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "Student")  # Student / Admin
    admin_secret = data.get("admin_secret", "")

    # --- Validation ---
    if not full_name or not email or not password:
        return Response({"error": "Missing required fields: full_name, email, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 6:
        return Response({"error": "Password must be at least 6 characters."}, status=status.HTTP_400_BAD_REQUEST)

    if role not in ("Student", "Admin"):
        return Response({"error": "Invalid role. Must be 'Student' or 'Admin'."}, status=status.HTTP_400_BAD_REQUEST)

    # Admin registration requires a valid access code
    if role == "Admin":
        if not admin_secret:
            return Response({"error": "Administrator registration requires an admin access code."}, status=status.HTTP_403_FORBIDDEN)
        if admin_secret != ADMIN_ACCESS_CODE:
            return Response({"error": "Invalid admin access code. Contact your platform administrator."}, status=status.HTTP_403_FORBIDDEN)

    if db_users.find_one({"email": email}):
        return Response({"error": "An account with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user_id = get_next_sequence_value("user_id")
    password_hash = make_password(password)

    user_doc = {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    db_users.insert_one(user_doc)

    return Response({
        "success": True,
        "message": f"Successfully registered as {role}.",
        "user_id": user_id
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def auth_login(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")
    requested_role = data.get("role")  # Optional check for portal validation

    if not email or not password:
        return Response({"error": "Missing credentials."}, status=status.HTTP_400_BAD_REQUEST)
        
    user = db_users.find_one({"email": email})
    if not user:
        return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        
    if not check_password(password, user["password_hash"]):
        return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

    if requested_role and user["role"] != requested_role:
        return Response({"error": f"Unauthorized access. You are registered as a {user['role']}."}, status=status.HTTP_403_FORBIDDEN)

    token = generate_session(user)

    return Response({
        "token": token,
        "user_id": user["user_id"],
        "full_name": user["full_name"],
        "role": user["role"],
        "email": user["email"]
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def auth_logout(request):
    session = get_session_user(request)
    if session:
        db_sessions.delete_one({"token": session["token"]})
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
    return Response({"message": "No active session to invalidate."}, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT'])
def user_profile(request, user_id):
    session = get_session_user(request)
    if not session or session["user_id"] != int(user_id):
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        
    if request.method == 'GET':
        user = db_users.find_one({"user_id": int(user_id)}, {"_id": 0, "password_hash": 0})
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(user, status=status.HTTP_200_OK)
        
    elif request.method == 'PUT':
        data = request.data
        updates = {}
        if "full_name" in data:
            updates["full_name"] = data["full_name"]
            
        if not updates:
            return Response({"message": "No fields to update."}, status=status.HTTP_400_BAD_REQUEST)
            
        db_users.update_one({"user_id": int(user_id)}, {"$set": updates})
        return Response({"success": True, "message": "Profile updated."}, status=status.HTTP_200_OK)

# ----------------- MODULE 2: COURSE ROADMAPS -----------------
@api_view(['GET', 'POST'])
def courses_list(request):
    if request.method == 'GET':
        courses = list(db_courses.find({}, {"_id": 0}))
        return Response(courses, status=status.HTTP_200_OK)
        
    elif request.method == 'POST':
        # Admin only
        session = get_session_user(request)
        if not session or session["role"] != 'Admin':
            return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
            
        data = request.data
        course_name = data.get("course_name")
        category = data.get("category")
        description = data.get("description")
        stages = data.get("stages", []) # list of stages
        
        if not course_name or not category:
            return Response({"error": "Missing course details."}, status=status.HTTP_400_BAD_REQUEST)
            
        course_id = get_next_sequence_value("course_id")
        course_doc = {
            "course_id": course_id,
            "course_name": course_name,
            "category": category,
            "description": description,
            "stage_count": len(stages),
            "stages": stages,
            "created_by": session["user_id"],
            "created_at": datetime.now().isoformat()
        }
        db_courses.insert_one(course_doc)
        
        return Response({"success": True, "course_id": course_id}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def course_detail(request, course_id):
    if request.method == 'GET':
        course = db_courses.find_one({"course_id": int(course_id)}, {"_id": 0})
        if not course:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(course, status=status.HTTP_200_OK)
        
    # Edit/Delete require admin
    session = get_session_user(request)
    if not session or session["role"] != 'Admin':
        return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
        
    if request.method == 'PUT':
        data = request.data
        updates = {}
        for key in ["course_name", "category", "description", "stages"]:
            if key in data:
                updates[key] = data[key]
        if "stages" in updates:
            updates["stage_count"] = len(updates["stages"])
            
        db_courses.update_one({"course_id": int(course_id)}, {"$set": updates})
        return Response({"success": True}, status=status.HTTP_200_OK)
        
    elif request.method == 'DELETE':
        db_courses.delete_one({"course_id": int(course_id)})
        return Response({"success": True, "message": "Course removed."}, status=status.HTTP_200_OK)

# ----------------- MODULE 3 & 4: CUSTOMIZATION & PLAN GENERATION -----------------
@api_view(['GET'])
def syllabus_bank_list(request):
    return Response(SYLLABUS_BANK, status=status.HTTP_200_OK)

@api_view(['POST'])
def syllabus_upload(request):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Authentication session required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    if 'syllabus_file' not in request.FILES:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
    uploaded_file = request.FILES['syllabus_file']
    # Save file to upload directory
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{uploaded_file.name}")
    try:
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
                
        # Perform OCR
        extracted_text = extract_text_from_file(file_path)
        
        # Cleanup file after reading to avoid leak
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return Response({
            "success": True,
            "filename": uploaded_file.name,
            "extracted_text": extracted_text
        }, status=status.HTTP_200_OK)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return Response({"error": f"File parsing failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def customize_plan_submit(request):
    session = get_session_user(request)
    if not session or session["role"] != 'Student':
        return Response({"error": "Student account required."}, status=status.HTTP_403_FORBIDDEN)
        
    data = request.data
    exam_category = data.get("exam_category")
    answer_format = data.get("answer_format")
    exam_name = data.get("exam_name")
    category_other = data.get("category_other")
    subject_name = data.get("subject_name")
    syllabus_source = data.get("syllabus_source")
    syllabus_text = data.get("syllabus_text")
    exam_date_str = data.get("exam_date")
    target_grade_percent = data.get("target_grade_percent") # Cap at 90 baseline

    if not exam_category or not answer_format or not subject_name or not syllabus_text or not exam_date_str or target_grade_percent is None:
        return Response({"error": "Missing required fields for planner."}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        target_grade_percent = float(target_grade_percent)
        # Cap baseline target grade at 90 so Target+10% does not exceed 100%
        if target_grade_percent > 90:
            target_grade_percent = 90
        elif target_grade_percent < 0:
            target_grade_percent = 0
    except ValueError:
        return Response({"error": "Invalid grade percent format."}, status=status.HTTP_400_BAD_REQUEST)

    # 1. AI pass - Complexity Analysis
    # Get hash to cache or reuse analysis
    syllabus_hash = get_syllabus_hash(syllabus_text)
    
    # Check cache
    db_analysis = settings.MONGO_DB["analysis_cache"]
    cached = db_analysis.find_one({"syllabus_hash": syllabus_hash, "exam_category": exam_category, "answer_format": answer_format})
    if cached:
        topics = cached["topics"]
    else:
        # Run AI analysis
        topics = analyze_syllabus(syllabus_text, exam_category, answer_format)
        # Cache results
        db_analysis.insert_one({
            "syllabus_hash": syllabus_hash,
            "exam_category": exam_category,
            "answer_format": answer_format,
            "topics": topics,
            "created_at": datetime.now().isoformat()
        })
        
    # Store Customization request
    request_id = get_next_sequence_value("request_id")
    req_doc = {
        "request_id": request_id,
        "student_id": session["user_id"],
        "exam_category": exam_category,
        "answer_format": answer_format,
        "exam_name": exam_name,
        "category_other": category_other,
        "subject_name": subject_name,
        "syllabus_source": syllabus_source,
        "syllabus_text": syllabus_text,
        "exam_date": exam_date_str,
        "target_grade_percent": target_grade_percent,
        "submitted_at": datetime.now().isoformat()
    }
    db_customization_requests.insert_one(req_doc)

    # 2. Deterministic schedule calculation
    # Generates three plans: Baseline, Plus5, Plus10
    plans_data = generate_plans(
        request_id=request_id,
        student_id=session["user_id"],
        exam_category=exam_category,
        answer_format=answer_format,
        subject_name=subject_name,
        exam_date_str=exam_date_str,
        target_grade_percent=target_grade_percent,
        topics=topics
    )
    
    # Store generated plans and set the active status
    generated_plan_ids = []
    baseline_plan_id = None
    
    # Set all student's existing plans to inactive
    db_plans.update_many({"student_id": session["user_id"]}, {"$set":{"is_active": False}})
    db_vault.update_many({"student_id": session["user_id"]}, {"$set":{"is_active": False}})
    
    for plan in plans_data:
        plan_id = get_next_sequence_value("plan_id")
        plan["plan_id"] = plan_id
        plan["request_id"] = request_id
        plan["student_id"] = session["user_id"]
        # Default active tier is Plus5 (recommended) or Baseline. We'll set the tier generated to is_active = False by default,
        # and explicitly active standard is Baseline, but the user selects. We can mark the whole request set active in vault
        # and make the Baseline plan_id active in the schedule.
        plan["is_active"] = (plan["tier"] == "Plus5") # We default to active tier: Plus5
        plan["feedback_patches"] = []
        
        db_plans.insert_one(plan)
        generated_plan_ids.append(plan_id)
        if plan["tier"] == "Plus5":
            baseline_plan_id = plan_id

    # Create Vault entry
    vault_id = get_next_sequence_value("vault_id")
    vault_doc = {
        "vault_id": vault_id,
        "student_id": session["user_id"],
        "plan_id": baseline_plan_id, # Link active plan
        "associated_plan_ids": generated_plan_ids, # Store references to the full tier set
        "session_summary": f"{subject_name} ({exam_name if exam_name else exam_category}) Study Plan — Tiers: Baseline, +5%, +10%",
        "is_active": True,
        "timestamp": datetime.now().isoformat()
    }
    db_vault.insert_one(vault_doc)

    return Response({
        "success": True,
        "request_id": request_id,
        "vault_id": vault_id,
        "active_plan_id": baseline_plan_id,
        "plans": [
            {
                "plan_id": p["plan_id"],
                "tier": p["tier"],
                "target_grade_effective": p["target_grade_effective"],
                "revision_start_date": p["revision_start_date"],
                "daily_schedule": p["daily_schedule_json"]
            } for p in plans_data
        ]
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_plans_by_request(request, request_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    plans = list(db_plans.find({"request_id": int(request_id)}, {"_id": 0}))
    return Response(plans, status=status.HTTP_200_OK)

@api_view(['GET'])
def plan_detail(request, plan_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    plan = db_plans.find_one({"plan_id": int(plan_id)}, {"_id": 0})
    if not plan:
        return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)
        
    return Response(plan, status=status.HTTP_200_OK)

# ----------------- MODULE 5: PROGRESS & PACE ADAPTATION -----------------
@api_view(['GET', 'POST'])
def plan_progress(request, plan_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    plan = db_plans.find_one({"plan_id": int(plan_id)})
    if not plan:
        return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        # Retrieve all progress entries checked off for this plan
        progress_entries = list(db_progress.find({"plan_id": int(plan_id)}, {"_id": 0}))
        completed_ids = [p["topic_id"] for p in progress_entries if p["status"] == "Completed"]
        
        # Calculate pace
        schedule = plan["daily_schedule_json"]
        pace = calculate_pace(schedule, completed_ids)
        
        return Response({
            "pace_status": pace,
            "progress": progress_entries
        }, status=status.HTTP_200_OK)
        
    elif request.method == 'POST':
        data = request.data
        topic_id = data.get("topic_id")
        status_val = data.get("status") # Completed / Skipped / Pending
        
        if not topic_id or not status_val:
            return Response({"error": "Missing topic_id or status values."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Update progress entry
        db_progress.update_one(
            {"plan_id": int(plan_id), "topic_id": topic_id},
            {
                "$set": {
                    "status": status_val,
                    "completed_on": date.today().strftime("%Y-%m-%d") if status_val == "Completed" else None,
                },
                "$setOnInsert": {
                    "progress_id": get_next_sequence_value("progress_id")
                }
            },
            upsert=True
        )
        
        # Recalculate pace status
        progress_entries = list(db_progress.find({"plan_id": int(plan_id)}))
        completed_ids = [p["topic_id"] for p in progress_entries if p["status"] == "Completed"]
        pace = calculate_pace(plan["daily_schedule_json"], completed_ids)
        
        return Response({
            "success": True,
            "pace_status": pace
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
def plan_recompress(request, plan_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    plan = db_plans.find_one({"plan_id": int(plan_id)})
    if not plan:
        return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)
        
    # Get completed topics
    progress_entries = list(db_progress.find({"plan_id": int(plan_id)}, {"_id": 0}))
    completed_ids = [p["topic_id"] for p in progress_entries if p["status"] == "Completed"]
    
    # Run recompression
    current_schedule = plan["daily_schedule_json"]
    revision_start_date = plan["revision_start_date"]
    today_str = date.today().strftime("%Y-%m-%d")
    
    new_schedule, applied = recompress_schedule(
        daily_schedule=current_schedule,
        completed_topic_ids=completed_ids,
        revision_start_date_str=revision_start_date,
        current_date_str=today_str
    )
    
    if applied:
        db_plans.update_one(
            {"plan_id": int(plan_id)},
            {"$set": {
                "daily_schedule_json": new_schedule
            }}
        )
        
    return Response({
        "success": True,
        "recompression_applied": applied,
        "daily_schedule": new_schedule
    }, status=status.HTTP_200_OK)

# ----------------- MODULE 6: FEEDBACK & PATCH REFINEMENT -----------------
@api_view(['POST'])
def plan_feedback_submit(request, plan_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    plan = db_plans.find_one({"plan_id": int(plan_id)})
    if not plan:
        return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)
        
    data = request.data
    feedback_text = data.get("feedback_text")
    adjustment_type = data.get("adjustment_type") # Workload / Pace / Other
    
    if not feedback_text or not adjustment_type:
        return Response({"error": "Missing feedback parameters."}, status=status.HTTP_400_BAD_REQUEST)
        
    # Apply patch to schedule
    current_schedule = plan["daily_schedule_json"]
    today_str = date.today().strftime("%Y-%m-%d")
    
    new_schedule, modified, details = apply_feedback_patch(
        daily_schedule=current_schedule,
        feedback_text=feedback_text,
        adjustment_type=adjustment_type,
        current_date_str=today_str
    )
    
    feedback_id = get_next_sequence_value("feedback_id")
    patch_doc = {
        "feedback_id": feedback_id,
        "plan_id": int(plan_id),
        "feedback_text": feedback_text,
        "adjustment_type": adjustment_type,
        "patch_details": details,
        "submitted_at": datetime.now().isoformat()
    }
    
    db_plans.update_one(
        {"plan_id": int(plan_id)},
        {
            "$push": {"feedback_patches": patch_doc},
            "$set": {"daily_schedule_json": new_schedule}
        }
    )
    
    return Response({
        "success": True,
        "feedback_id": feedback_id,
        "patch_details": details,
        "daily_schedule": new_schedule
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def plan_version_history(request, plan_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    plan = db_plans.find_one({"plan_id": int(plan_id)}, {"feedback_patches": 1, "_id": 0})
    if not plan:
        return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)
        
    return Response(plan.get("feedback_patches", []), status=status.HTTP_200_OK)

# ----------------- MODULE 7: UNIFIED PLAN VAULT -----------------
@api_view(['GET'])
def vault_list(request, student_id):
    session = get_session_user(request)
    if not session or session["user_id"] != int(student_id):
        return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        
    vault_entries = list(db_vault.find({"student_id": int(student_id)}, {"_id": 0}))
    
    # Attach plan details to make frontend rendering richer
    for entry in vault_entries:
        active_plan_id = entry.get("plan_id")
        plan_doc = db_plans.find_one({"plan_id": active_plan_id}, {"daily_schedule_json": 0, "_id": 0})
        if plan_doc:
            entry["plan_details"] = plan_doc
            
    # Sort with active plan first, then chronologically descending
    vault_entries.sort(key=lambda x: (not x.get("is_active", False), x.get("timestamp", "")), reverse=True)
    return Response(vault_entries, status=status.HTTP_200_OK)

@api_view(['GET'])
def vault_detail(request, vault_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    entry = db_vault.find_one({"vault_id": int(vault_id)}, {"_id": 0})
    if not entry:
        return Response({"error": "Vault entry not found."}, status=status.HTTP_404_NOT_FOUND)
        
    return Response(entry, status=status.HTTP_200_OK)

@api_view(['POST'])
def vault_reopen(request, vault_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    vault_entry = db_vault.find_one({"vault_id": int(vault_id)})
    if not vault_entry:
        return Response({"error": "Vault entry not found."}, status=status.HTTP_404_NOT_FOUND)
        
    student_id = vault_entry["student_id"]
    active_plan_id = vault_entry["plan_id"]
    associated_plan_ids = vault_entry.get("associated_plan_ids", [active_plan_id])

    # Deactivate all plans for this student
    db_plans.update_many({"student_id": student_id}, {"$set": {"is_active": False}})
    db_vault.update_many({"student_id": student_id}, {"$set": {"is_active": False}})
    
    # Activate the reopening vault session
    db_vault.update_one({"vault_id": int(vault_id)}, {"$set": {"is_active": True}})
    
    # Also activate the active plan in the set (defaulting to the saved active tier)
    db_plans.update_one({"plan_id": active_plan_id}, {"$set": {"is_active": True}})

    return Response({
        "success": True,
        "message": "Vault session reopened as active plan.",
        "active_plan_id": active_plan_id
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def vault_delete(request, vault_id):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Auth token required."}, status=status.HTTP_401_UNAUTHORIZED)
        
    db_vault.delete_one({"vault_id": int(vault_id)})
    return Response({"success": True, "message": "Vault entry removed from history."}, status=status.HTTP_200_OK)

# ----------------- MODULE 8: ADMIN DASHBOARD -----------------
@api_view(['GET'])
def admin_usage_metrics(request):
    session = get_session_user(request)
    if not session or session["role"] != 'Admin':
        return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
        
    total_students = db_users.count_documents({"role": "Student"})
    total_plans = db_plans.count_documents({})
    
    # Find pace status distributions of active plans
    active_plans = list(db_plans.find({"is_active": True}))
    on_track_count = 0
    behind_count = 0
    ahead_count = 0
    
    for plan in active_plans:
        progress_entries = list(db_progress.find({"plan_id": plan["plan_id"]}))
        completed_ids = [p["topic_id"] for p in progress_entries if p["status"] == "Completed"]
        pace = calculate_pace(plan["daily_schedule_json"], completed_ids)
        if pace == 'OnTrack':
            on_track_count += 1
        elif pace == 'Behind':
            behind_count += 1
        elif pace == 'Ahead':
            ahead_count += 1

    return Response({
        "total_students": total_students,
        "total_plans_generated": total_plans,
        "active_plans_count": len(active_plans),
        "pace_distribution": {
            "on_track": on_track_count,
            "behind": behind_count,
            "ahead": ahead_count
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_difficulty_trends(request):
    """
    Exposes aggregate, anonymized difficulty trends compiled from syllabus topic complexity scores.
    """
    session = get_session_user(request)
    if not session or session["role"] != 'Admin':
        return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
        
    # Aggregate average complexity by subject name from customization requests
    requests_list = list(db_customization_requests.find({}))
    
    subject_complexity = {}
    
    for req in requests_list:
        sub_name = req["subject_name"].capitalize()
        # Find plans of this request to extract complexity
        plan = db_plans.find_one({"request_id": req["request_id"]})
        if not plan:
            continue
            
        schedule = plan["daily_schedule_json"]
        complexities = []
        for day in schedule:
            if not day.get("is_revision", False):
                for t in day.get("topics", []):
                    complexities.append(t.get("complexity", 3))
                    
        if complexities:
            avg_comp = sum(complexities) / len(complexities)
            if sub_name not in subject_complexity:
                subject_complexity[sub_name] = []
            subject_complexity[sub_name].append(avg_comp)

    # Format averages
    report = []
    for sub, scores in subject_complexity.items():
        report.append({
            "subject": sub,
            "avg_complexity": round(sum(scores) / len(scores), 2),
            "samples_count": len(scores)
        })
        
    # Sort by complexity descending
    report.sort(key=lambda x: x["avg_complexity"], reverse=True)
    return Response(report, status=status.HTTP_200_OK)

@api_view(['GET'])
def admin_students_list(request):
    session = get_session_user(request)
    if not session or session["role"] != 'Admin':
        return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
        
    students = list(db_users.find({"role": "Student"}, {"_id": 0, "password_hash": 0}))
    
    # Annotate with active plan summary
    for student in students:
        active_vault = db_vault.find_one({"student_id": student["user_id"], "is_active": True})
        if active_vault:
            student["active_plan_summary"] = active_vault["session_summary"]
            # Find pace
            plan = db_plans.find_one({"plan_id": active_vault["plan_id"]})
            if plan:
                progress_entries = list(db_progress.find({"plan_id": plan["plan_id"]}))
                completed_ids = [p["topic_id"] for p in progress_entries if p["status"] == "Completed"]
                student["pace_status"] = calculate_pace(plan["daily_schedule_json"], completed_ids)
            else:
                student["pace_status"] = "No Active Plan"
        else:
            student["active_plan_summary"] = "No active schedules"
            student["pace_status"] = "No Active Plan"
            
    return Response(students, status=status.HTTP_200_OK)

# ----------------- ADMIN ACCESS CODE REQUEST SYSTEM -----------------
@api_view(['POST'])
def admin_request_create(request):
    data = request.data
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    reason = data.get("reason", "").strip()

    if not full_name or not email or not reason:
        return Response({"error": "All fields (full_name, email, reason) are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if a pending request already exists
    existing = db_admin_requests.find_one({"email": email, "status": "Pending"})
    if existing:
        return Response({"error": "You already have a pending admin access request."}, status=status.HTTP_400_BAD_REQUEST)

    request_id = get_next_sequence_value("admin_request_id")
    request_doc = {
        "request_id": request_id,
        "full_name": full_name,
        "email": email,
        "reason": reason,
        "status": "Pending",
        "access_code": "",
        "created_at": datetime.now().isoformat()
    }
    db_admin_requests.insert_one(request_doc)

    return Response({
        "success": True,
        "message": "Admin access request submitted successfully.",
        "request_id": request_id
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def admin_requests_list(request):
    session = get_session_user(request)
    if not session or session["role"] != 'Admin':
        return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)

    requests = list(db_admin_requests.find({}, {"_id": 0}))
    return Response(requests, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_request_action(request, request_id):
    session = get_session_user(request)
    if not session or session["role"] != 'Admin':
        return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    action = data.get("action")  # Approve / Reject

    if action not in ("Approve", "Reject"):
        return Response({"error": "Invalid action. Must be 'Approve' or 'Reject'."}, status=status.HTTP_400_BAD_REQUEST)

    req = db_admin_requests.find_one({"request_id": int(request_id)})
    if not req:
        return Response({"error": "Admin request not found."}, status=status.HTTP_404_NOT_FOUND)

    if req["status"] != "Pending":
        return Response({"error": f"Request has already been {req['status'].lower()}."}, status=status.HTTP_400_BAD_REQUEST)

    updates = {"status": action + "d"}
    if action == "Approve":
        updates["access_code"] = "GRADEPATH_ADMIN_2024"

    db_admin_requests.update_one({"request_id": int(request_id)}, {"$set": updates})

    return Response({
        "success": True,
        "message": f"Request successfully {action.lower()}d.",
        "access_code": updates.get("access_code", "")
    }, status=status.HTTP_200_OK)
@csrf_exempt
@api_view(['POST'])
def chat_view(request):
    session = get_session_user(request)
    if not session:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    user_message = str(data.get('message', ''))
    if not user_message:
        return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)
    active_vault = None
    plan = None
    progress_entries = []
    # Build context about the user's progress (optional)
    context_parts = [f"User ID: {session['user_id']}", f"Role: {session['role']}"]
    try:
        # Get user's active plan from vault
        active_vault = db_vault.find_one({"student_id": session["user_id"], "is_active": True})
        if active_vault:
            plan = db_plans.find_one({"plan_id": active_vault["plan_id"]})
            if plan:
                context_parts.append(f"Active plan ID: {active_vault['plan_id']}")
                # Get progress for this plan
                progress_entries = list(db_progress.find({"plan_id": plan["plan_id"]}))
                if progress_entries:
                    completed = sum(1 for p in progress_entries if p.get('status') == 'Completed')
                    total = len(progress_entries)
                    context_parts.append(f"Progress: {completed}/{total} topics completed")
                else:
                    context_parts.append("No progress recorded yet.")
            else:
                context_parts.append("Active plan not found.")
        else:
            context_parts.append("No active plan found.")
    except Exception as e:
        # If we can't get context, just continue without it
        print(f"Error building context for chatbot: {e}")
        pass
    context = "\n".join(context_parts)
    try:
        # Generate response based on user message and context
        msg = user_message.strip()
        msg_lower = msg.lower()

        # Greeting
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(g in msg_lower for g in greetings):
            return Response({"response": "Hello! I'm your study buddy. How can I assist you with your studies today?"}, status=status.HTTP_200_OK)

        # Who are you
        if 'who are you' in msg_lower or 'what are you' in msg_lower:
            return Response({"response": "I'm your study buddy, here to help you with your study plan and progress."}, status=status.HTTP_200_OK)

        # Progress queries
        if 'progress' in msg_lower or 'how am i' in msg_lower or 'how am i doing' in msg_lower:
            if plan:
                total = len(progress_entries)
                completed = sum(1 for p in progress_entries if p.get('status') == 'Completed')
                if total == 0:
                    return Response({"response": "You haven't started tracking progress yet. Start checking off topics as you complete them!"}, status=status.HTTP_200_OK)
                else:
                    percent = int((completed / total) * 100) if total > 0 else 0
                    return Response({"response": f"You've completed {completed} out of {total} topics ({percent}%). Keep going!"}, status=status.HTTP_200_OK)
            else:
                return Response({"response": "I don't have your plan info yet. Make sure you have an active study plan."}, status=status.HTTP_200_OK)

        # Today's tasks
        if ('what should i study' in msg_lower or 'today\'s task' in msg_lower or 'what to study' in msg_lower or 'today\'s tasks' in msg_lower):
            if plan and 'daily_schedule' in plan:
                from datetime import datetime
                today_str = datetime.now().strftime('%Y-%m-%d')
                for day in plan['daily_schedule']:
                    if day.get('date') == today_str:
                        topics = [t.get('topic_name', 'Unnamed topic') for t in day.get('topics', []) if t.get('topic_name')]
                        if topics:
                            if len(topics) == 1:
                                return Response({"response": f"Today you should study: {topics[0]}"}, status=status.HTTP_200_OK)
                            else:
                                return Response({"response": f"Today you should study: {', '.join(todos)}"}, status=status.HTTP_200_OK)
                        else:
                            return Response({"response": "No topics scheduled for today."}, status=status.HTTP_200_OK)
                return Response({"response": f"No schedule found for today ({today_str}). Check your plan dates."}, status=status.HTTP_200_OK)
            else:
                return Response({"response": "I don't have your schedule info. Please ensure you have an active study plan."}, status=status.HTTP_200_OK)

        # Plan summary
        if ('plan' in msg_lower and ('summary' in msg_lower or 'detail' in msg_lower or 'what is my plan' in msg_lower or 'my plan' in msg_lower)):
            if plan:
                tier = plan.get('tier', 'N/A')
                target = plan.get('target_grade_effective', 'N/A')
                return Response({"response": f"Your current plan is {tier} tier aiming for {target}% grade."}, status=status.HTTP_200_OK)
            else:
                return Response({"response": "No active plan found."}, status=status.HTTP_200_OK)

        # Days left
        if ('how many days left' in msg_lower or 'days left' in msg_lower or 'days remaining' in msg_lower):
            if plan and 'daily_schedule' in plan:
                from datetime import datetime
                dates = [d.get('date') for d in plan['daily_schedule'] if d.get('date')]
                if dates:
                    last_str = max(dates)
                    today = datetime.now().date()
                    last_date = datetime.strptime(last_str, '%Y-%m-%d').date()
                    delta = (last_date - today).days
                    if delta < 0:
                        return Response({"response": "Your plan has already ended."}, status=status.HTTP_200_OK)
                    elif delta == 0:
                        return Response({"response": "Today is the last day of your plan!"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"response": f"You have {delta} days left until your plan ends on {last_str}."}, status=status.HTTP_200_OK)
                else:
                    return Response({"response": "Could not determine end date from schedule."}, status=status.HTTP_200_OK)
            else:
                return Response({"response": "No schedule data available."}, status=status.HTTP_200_OK)

        # Study tip
        if 'study tip' in msg_lower or 'tip' in msg_lower:
            import random
            tips = [
                "Break your study sessions into 25-minute chunks with 5-minute breaks (Pomodoro technique).",
                "Explain the concept aloud as if teaching someone else to reinforce learning.",
                "Use spaced repetition: review material after 1 day, 3 days, 1 week, and 1 month.",
                "Stay hydrated and take short walks to keep your mind fresh.",
                "Test yourself with practice questions to identify gaps.",
                "Organize your study materials before you start to reduce distractions.",
                "Set specific goals for each study session (e.g., 'finish chapter 3 exercises')."
            ]
            return Response({"response": random.choice(tips)}, status=status.HTTP_200_OK)

        # Default fallback
        return Response({"response": "I'm here to help with your study plan. You can ask about your progress, today's tasks, or general study tips."}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Chatbot error: {e}")
        return Response({"response": "I'm having trouble processing your request. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(f"Chatbot error: {e}")
        return Response({"response": "I'm having trouble processing your request. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
