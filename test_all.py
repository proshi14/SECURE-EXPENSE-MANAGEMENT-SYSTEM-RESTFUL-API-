import urllib.request, urllib.error, json

print('=== COMPREHENSIVE EXPENSE TRACKER TEST ===')
print()

# 1. Register new user
print('1. REGISTER')
reg_req = urllib.request.Request('http://127.0.0.1:8000/users/register', data=json.dumps({'username':'testuser','email':'testuser@test.com','password':'Test1234'}).encode('utf-8'), headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(reg_req) as res:
        print('✓ Registration OK')
except urllib.error.HTTPError as e:
    if e.code == 400:
        print('✓ User already exists (OK)')
    else:
        print('✗ Register failed:', e.code)

# 2. Login
print()
print('2. LOGIN')
login_req = urllib.request.Request('http://127.0.0.1:8000/users/login', data=json.dumps({'email':'testuser@test.com','password':'Test1234'}).encode('utf-8'), headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(login_req) as res:
        login_data = json.loads(res.read().decode())
        token = login_data.get('access_token')
        print('✓ Login OK')
except urllib.error.HTTPError as e:
    print('✗ Login failed:', e.code)
    token = None

if token:
    # 3. Create expenses
    print()
    print('3. CREATE EXPENSES')
    expenses = [
        {'title':'Breakfast','amount':150,'category':'Food','date':'2026-06-10'},
        {'title':'Gas','amount':500,'category':'Travel','date':'2026-06-12'},
        {'title':'Books','amount':800,'category':'Shopping','date':'2026-06-14'},
    ]
    expense_ids = []
    for exp in expenses:
        exp_req = urllib.request.Request('http://127.0.0.1:8000/expenses/', data=json.dumps(exp).encode('utf-8'), headers={'Content-Type':'application/json','Authorization':'Bearer ' + token})
        try:
            with urllib.request.urlopen(exp_req) as res:
                exp_data = json.loads(res.read().decode())
                expense_ids.append(exp_data.get('id'))
                print('✓ Created: ' + exp['title'] + ' (' + str(exp_data.get('id'))[:8] + '...)')
        except Exception as e:
            print('✗ Failed to create ' + exp['title'] + ': ' + str(e)[:40])
    
    # 4. Get all expenses
    print()
    print('4. LIST EXPENSES')
    list_req = urllib.request.Request('http://127.0.0.1:8000/expenses/?page=1&limit=10', headers={'Authorization':'Bearer ' + token})
    try:
        with urllib.request.urlopen(list_req) as res:
            expenses_list = json.loads(res.read().decode())
            print('✓ Retrieved ' + str(len(expenses_list)) + ' expenses')
    except Exception as e:
        print('✗ Failed to list: ' + str(e)[:40])
    
    # 5. Get single expense
    if expense_ids:
        print()
        print('5. GET SINGLE EXPENSE')
        single_req = urllib.request.Request('http://127.0.0.1:8000/expenses/' + expense_ids[0], headers={'Authorization':'Bearer ' + token})
        try:
            with urllib.request.urlopen(single_req) as res:
                exp_data = json.loads(res.read().decode())
                print('✓ Retrieved expense: ' + exp_data.get('title'))
        except Exception as e:
            print('✗ Failed to get single: ' + str(e)[:40])
        
        # 6. Update expense
        print()
        print('6. UPDATE EXPENSE')
        update_req = urllib.request.Request('http://127.0.0.1:8000/expenses/' + expense_ids[0], data=json.dumps({'amount':200}).encode('utf-8'), headers={'Content-Type':'application/json','Authorization':'Bearer ' + token}, method='PUT')
        try:
            with urllib.request.urlopen(update_req) as res:
                exp_data = json.loads(res.read().decode())
                print('✓ Updated: ' + exp_data.get('title') + ' - new amount: ' + str(exp_data.get('amount')))
        except Exception as e:
            print('✗ Failed to update: ' + str(e)[:40])
    
    # 7. Get reports
    print()
    print('7. GET REPORTS')
    reports = ['/summary/dashboard', '/summary/category', '/summary/monthly']
    for report in reports:
        report_req = urllib.request.Request('http://127.0.0.1:8000' + report, headers={'Authorization':'Bearer ' + token})
        try:
            with urllib.request.urlopen(report_req) as res:
                report_data = json.loads(res.read().decode())
                print('✓ ' + report + ': OK')
        except Exception as e:
            print('✗ ' + report + ' failed: ' + str(e)[:40])
    
    # 8. Filter expenses
    print()
    print('8. FILTER EXPENSES')
    filter_req = urllib.request.Request('http://127.0.0.1:8000/expenses/?category=Food&keyword=Breakfast', headers={'Authorization':'Bearer ' + token})
    try:
        with urllib.request.urlopen(filter_req) as res:
            filtered = json.loads(res.read().decode())
            print('✓ Filtered: ' + str(len(filtered)) + ' results')
    except Exception as e:
        print('✗ Filter failed: ' + str(e)[:40])
    
    # 9. Delete expense
    if len(expense_ids) > 1:
        print()
        print('9. DELETE EXPENSE')
        del_req = urllib.request.Request('http://127.0.0.1:8000/expenses/' + expense_ids[1], headers={'Authorization':'Bearer ' + token}, method='DELETE')
        try:
            with urllib.request.urlopen(del_req) as res:
                print('✓ Deleted expense')
        except Exception as e:
            print('✗ Delete failed: ' + str(e)[:40])

print()
print('=== TEST COMPLETE ===')
