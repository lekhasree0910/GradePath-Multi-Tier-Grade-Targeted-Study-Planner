import urllib.request, urllib.error, json

BASE = 'http://127.0.0.1:8000'
results = []

def check(label, url, method='GET', data=None, headers={}):
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=6) as r:
            status = r.status
            body = r.read(400).decode(errors='ignore')
            results.append((label, status, body[:60]))
    except urllib.error.HTTPError as e:
        body = e.read(200).decode(errors='ignore')
        results.append((label, e.code, body[:60]))
    except Exception as ex:
        results.append((label, 'ERR', str(ex)[:60]))

# ── HTML pages ──
check('Landing /',              BASE + '/')
check('index.html (Home fix)',  BASE + '/index.html')
check('register.html',         BASE + '/register.html')
check('login_student.html',    BASE + '/login_student.html')
check('login_admin.html',      BASE + '/login_admin.html')
check('courses.html',          BASE + '/courses.html')
check('customize.html',        BASE + '/customize.html')
check('vault.html',            BASE + '/vault.html')
check('plan_output.html',      BASE + '/plan_output.html')
check('student_dashboard.html',BASE + '/student_dashboard.html')
check('admin_dashboard.html',  BASE + '/admin_dashboard.html')

# ── Static assets ──
check('style.css',             BASE + '/style.css')
check('script.js',             BASE + '/script.js')
check('hero_dark.png',         BASE + '/assets/hero_dark.png')
check('hero_light.png',        BASE + '/assets/hero_light.png')

# ── API ──
payload_reg = json.dumps({
    'full_name': 'Test Student',
    'email':     'teststudent99@gradepath.com',
    'password':  'test1234',
    'role':      'Student'
}).encode()

check('API Register Student',
      BASE + '/api/auth/register/', 'POST', payload_reg,
      {'Content-Type': 'application/json'})

payload_login = json.dumps({
    'email':    'teststudent99@gradepath.com',
    'password': 'test1234',
    'role':     'Student'
}).encode()

check('API Login Student',
      BASE + '/api/auth/login/', 'POST', payload_login,
      {'Content-Type': 'application/json'})

payload_bad = json.dumps({
    'email':    'nobody@gradepath.com',
    'password': 'wrongpass',
    'role':     'Admin'
}).encode()

check('API Bad Login (expect 400/401)',
      BASE + '/api/auth/login/', 'POST', payload_bad,
      {'Content-Type': 'application/json'})

# ── Admin Requests ──
import random
rand_num = random.randint(1000, 9999)
payload_admin_req = json.dumps({
    'full_name': 'Pending Admin',
    'email':     f'pending_admin{rand_num}@gradepath.com',
    'reason':    'Need to review curriculum'
}).encode()

check('API Create Admin Request',
      BASE + '/api/auth/admin-request/', 'POST', payload_admin_req,
      {'Content-Type': 'application/json'})

# ── Print results ──
print()
print('-' * 70)
print('  {:<30} {:<8} PREVIEW'.format('TEST', 'STATUS'))
print('-' * 70)
for label, status, preview in results:
    ok = str(status) in ('200', '201')
    icon = 'PASS' if ok else 'FAIL'
    print('  [{:<4}] {:<30} {:<8} {}'.format(icon, label, str(status), preview[:30]))
print('-' * 70)
print()
