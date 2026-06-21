import sys
import threading
import urllib.request
import urllib.error
import time
import json
from datetime import date

API_URL_CHECKIN = "http://127.0.0.1:5000/api/checkin"
HEADERS = {"X-Admin-Token": "vem-admin-2026", "Content-Type": "application/json"}

# Vehicle distribution logic to avoid exceeding capacity
# ONIBUS-01: 44, ONIBUS-02: 44, MICRO-01: 28, VAN-01: 15
VEHICLES = [
    ("ONIBUS-01", 44),
    ("ONIBUS-02", 44),
    ("MICRO-01", 28),
    ("VAN-01", 15)
]

def do_checkin(cpf, veiculo_id, data_str):
    payload = {
        "cpf": cpf,
        "veiculo_id": veiculo_id,
        "data": data_str,
        "tipo": "IDA"
    }
    
    start_time = time.time()
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(API_URL_CHECKIN, data=data, headers=HEADERS, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed = time.time() - start_time
            if resp.status == 200:
                body = json.loads(resp.read().decode('utf-8'))
                return (True, elapsed, None, body.get("vagas_restantes"))
            else:
                body = resp.read().decode('utf-8')
                return (False, elapsed, f"HTTP {resp.status}: {body}", None)
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        body = e.read().decode('utf-8')
        return (False, elapsed, f"HTTP {e.code}: {body}", None)
    except Exception as e:
        elapsed = time.time() - start_time
        return (False, elapsed, str(e), None)

class CheckinThread(threading.Thread):
    def __init__(self, cpf, veiculo_id, data_str):
        super().__init__()
        self.cpf = cpf
        self.veiculo_id = veiculo_id
        self.data_str = data_str
        self.result = None
        
    def run(self):
        self.result = do_checkin(self.cpf, self.veiculo_id, self.data_str)

today = date.today().isoformat()
threads = []
results = []
print(f"Starting stress test for CHECKIN on {today}...")

student_index = 1
for v_id, capacity in VEHICLES:
    for _ in range(capacity):
        if student_index > 100:
            break
        cpf = f"{10000000000 + student_index}"
        t = CheckinThread(cpf, v_id, today)
        threads.append(t)
        student_index += 1
    if student_index > 100:
        break

start_total = time.time()

for t in threads:
    t.start()

for t in threads:
    t.join()
    results.append(t.result)

end_total = time.time()

success_count = sum(1 for r in results if r[0])
failure_count = len(results) - success_count
times = [r[1] for r in results]
avg_time = sum(times) / len(times) if times else 0
max_time = max(times) if times else 0
min_time = min(times) if times else 0

output = {
    "Test_Type": "Embarque (Checkin)",
    "Total_Time_Seconds": round(end_total - start_total, 2),
    "Successful_Requests": success_count,
    "Failed_Requests": failure_count,
    "Average_Time_Per_Request": round(avg_time, 4),
    "Max_Time": round(max_time, 4),
    "Min_Time": round(min_time, 4),
    "Errors": []
}

errors = [r[2] for r in results if not r[0]]
if errors:
    for e in set(errors):
        output["Errors"].append({"Error": e, "Count": errors.count(e)})

with open("stress_test_embarque_report.json", "w") as f:
    json.dump(output, f, indent=4)

print(f"Stress test complete. Success: {success_count}, Failed: {failure_count}. Results saved to stress_test_embarque_report.json")
