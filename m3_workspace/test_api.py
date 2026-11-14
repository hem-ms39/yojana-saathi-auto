import urllib.request, json

payload = json.dumps({
    "scheme_id": "pm-mudra-shishu",
    "user_profile": {
        "name": "Priya Sharma", "age": 22, "gender": "F",
        "state": "Karnataka", "district": "Bangalore Urban",
        "aadhaar": "XXXX-XXXX-7842", "address": "42 MG Road",
        "pincode": "560001", "business_intent": "Tailoring business"
    }
}).encode("utf-8")

req = urllib.request.Request(
    "http://localhost:8001/forms/prefill",
    data=payload, method="POST",
    headers={"Content-Type": "application/json"}
)

r = urllib.request.urlopen(req)
resp = json.loads(r.read())

print("Form:", resp["form_title"])
print("Fill: {}% ({}/{} fields)".format(
    resp["fill_percentage"], resp["auto_filled_count"], resp["total_fields"]
))
print()
for f in resp["fields"]:
    status = "[AUTO]" if f.get("auto_filled") else "[    ]"
    print("  {} {}: {}".format(status, f["label"], f.get("value", "")))
