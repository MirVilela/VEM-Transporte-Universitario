import sys
import threading
import urllib.request
import urllib.error
import time
import json

API_URL = "http://127.0.0.1:5000/api/passageiros"
HEADERS = {"X-Admin-Token": "vem-admin-2026", "Content-Type": "application/json"}

def register_student(i):
    cpf = f"{10000000000 + i}" # valid 11 digit mock
    payload = {
        "cpf": cpf,
        "nome": f"Stress Test Student {i}",
        "rota": "ROTA-TESTE",
        "pin": f"{i:04d}"[-4:],
        "tipo_vaga": "NORMAL"
    }
    
    start_time = time.time()
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(API_URL, data=data, headers=HEADERS, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed = time.time() - start_time
            if resp.status == 201:
                return (True, elapsed, None)
            else:
                body = resp.read().decode('utf-8')
                return (False, elapsed, f"HTTP {resp.status}: {body}")
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        body = e.read().decode('utf-8')
        return (False, elapsed, f"HTTP {e.code}: {body}")
    except Exception as e:
        elapsed = time.time() - start_time
        return (False, elapsed, str(e))

results = []
start_total = time.time()
threads = []

class ReturnThread(threading.Thread):
    def __init__(self, target, args):
        super().__init__()
        self.target = target
        self.args = args
        self.result = None
    def run(self):
        self.result = self.target(*self.args)

print("Starting stress test with 100 concurrent requests...")

for i in range(1, 101):
    t = ReturnThread(target=register_student, args=(i,))
    threads.append(t)
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

with open("stress_test_report.json", "w") as f:
    json.dump(output, f, indent=4)

print("Stress test complete. Results saved to stress_test_report.json")
