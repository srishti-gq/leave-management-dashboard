import os

secrets_toml = os.environ.get("SECRETS_TOML_CONTENT", "")
service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON_CONTENT", "")

os.makedirs(".streamlit", exist_ok=True)
os.makedirs("secrets", exist_ok=True)

with open(".streamlit/secrets.toml", "w") as f:
    f.write(secrets_toml)

with open("secrets/service_account.json", "w") as f:
    f.write(service_account_json)

print("Secrets written successfully.")