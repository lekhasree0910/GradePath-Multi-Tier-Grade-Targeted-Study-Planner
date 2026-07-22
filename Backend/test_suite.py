import urllib.request
import urllib.error
import json
import random

BASE = 'http://127.0.0.1:8000'
results = []

def request(url, method='GET', payload=None, headers=None):
    if headers is None:
        headers = {}
    data_bytes = None
    if payload is not None:
        data_bytes = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            body = response.read().decode('utf-8', errors='ignore')
            try:
                json_data = json.loads(body)
            except:
                json_data = body
            return response.status, json_data
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='ignore')
        try:
            json_data = json.loads(body)
        except:
            json_data = body
        return e.code, json_data
    except Exception as ex:
        return 'ERR', str(ex)

def log_test(name, success, info):
    status_str = "PASS" if success else "FAIL"
    results.append((name, status_str, str(info)[:70]))

print("=" * 80)
print("              GRADEPATH END-TO-END COMPREHENSIVE TEST SUITE              ")
print("=" * 80)

# 1. Page Availability Checks
pages = [
    ('/', 'Landing Page'),
    ('/index.html', 'Index Page'),
    ('/register.html', 'Registration Page'),
    ('/login_student.html', 'Student Login Page'),
    ('/login_admin.html', 'Admin Login Page'),
    ('/courses.html', 'Courses Page'),
    ('/customize.html', 'Customize Page'),
    ('/vault.html', 'Vault Page'),
    ('/plan_output.html', 'Plan Output Page'),
    ('/student_dashboard.html', 'Student Dashboard'),
    ('/admin_dashboard.html', 'Admin Dashboard'),
    ('/style.css', 'Stylesheet CSS'),
    ('/script.js', 'Frontend JS Script')
]

for path, title in pages:
    code, _ = request(BASE + path)
    log_test(f"Page: {title}", code == 200, f"HTTP {code}")

# 2. Student Authentication Flow
rand_id = random.randint(10000, 99999)
student_email = f"auto_test_student_{rand_id}@gradepath.com"
student_pass = "TestPass123!"

# 2a. Register
code, res = request(BASE + '/api/auth/register/', 'POST', {
    'full_name': 'Automated Tester',
    'email': student_email,
    'password': student_pass,
    'role': 'Student'
})
user_id = res.get('user_id') if isinstance(res, dict) else None
log_test("API: Register Student", code == 201 and res.get('success') == True, f"Code {code}: {res}")

# 2b. Login
code, res = request(BASE + '/api/auth/login/', 'POST', {
    'email': student_email,
    'password': student_pass,
    'role': 'Student'
})
student_token = res.get('token') if isinstance(res, dict) else None
user_id = res.get('user_id') if isinstance(res, dict) and 'user_id' in res else user_id
log_test("API: Login Student", code == 200 and student_token is not None, f"Code {code}: Token received: {bool(student_token)}")

# 2c. Invalid Login Test
code, res = request(BASE + '/api/auth/login/', 'POST', {
    'email': student_email,
    'password': 'WrongPassword123',
    'role': 'Student'
})
log_test("API: Reject Invalid Credentials", code in (400, 401), f"Code {code}: {res}")

# 3. Admin Authentication Flow
code, res = request(BASE + '/api/auth/login/', 'POST', {
    'email': 'admin@gradepath.com',
    'password': 'adminpassword',
    'role': 'Admin'
})
admin_token = res.get('token') if isinstance(res, dict) else None
log_test("API: Login Admin", code == 200 and admin_token is not None, f"Code {code}: Token received: {bool(admin_token)}")

# 4. Courses API
code, courses = request(BASE + '/api/courses/')
log_test("API: Get Courses List", code == 200 and isinstance(courses, list), f"Found {len(courses) if isinstance(courses, list) else 0} courses")

if isinstance(courses, list) and len(courses) > 0:
    course_id = courses[0].get('id') or courses[0].get('course_id') or 1
    code, detail = request(BASE + f'/api/courses/{course_id}/')
    log_test("API: Get Course Detail", code == 200, f"Course ID {course_id}: {detail.get('title', '') if isinstance(detail, dict) else detail}")

# 5. Syllabus Bank API
code, bank = request(BASE + '/api/syllabus-bank/')
log_test("API: Get Syllabus Bank", code == 200, f"Found items: {len(bank) if isinstance(bank, list) else 'N/A'}")

# 6. Study Plan Customization Engine API
if student_token:
    headers = {'Authorization': f'Bearer {student_token}'}
    custom_payload = {
        "subject_name": "Computer Science Core",
        "exam_category": "Academic",
        "answer_format": "Descriptive",
        "exam_date": "2026-10-15",
        "target_grade_percent": 85,
        "available_hours_per_day": 3,
        "selected_days": ["Mon", "Wed", "Fri", "Sat"],
        "learner_level": "Intermediate",
        "syllabus_text": "Data Structures, Algorithms, Operating Systems, Database Management Systems, Computer Networks"
    }
    code, plan_res = request(BASE + '/api/plans/customize/', 'POST', custom_payload, headers)
    log_test("API: Create Custom Study Plan", code in (200, 201), f"Code {code}: {plan_res}")

    # 7. Student Vault (Saved Plans) API
    if user_id:
        code, vault_plans = request(BASE + f'/api/vault/{user_id}/', 'GET', None, headers)
        log_test("API: Fetch Saved Vault Plans", code == 200 and isinstance(vault_plans, list), f"Found {len(vault_plans) if isinstance(vault_plans, list) else 0} saved plans")

# 8. Admin Requests API
rand_admin_id = random.randint(10000, 99999)
code, admin_req_res = request(BASE + '/api/auth/admin-request/', 'POST', {
    'full_name': 'Pending Admin Test',
    'email': f'pending_admin_{rand_admin_id}@gradepath.com',
    'reason': 'Automated testing access request'
})
log_test("API: Submit Admin Access Request", code == 201, f"Code {code}: {admin_req_res}")

print("-" * 80)
print(f"{'TEST NAME':<40} | {'RESULT':<8} | DETAILS")
print("-" * 80)
passed_count = 0
for name, status, info in results:
    if status == "PASS":
        passed_count += 1
    print(f"{name:<40} | {status:<8} | {info}")
print("-" * 80)
print(f"SUMMARY: {passed_count} / {len(results)} tests passed successfully.")
print("=" * 80)
