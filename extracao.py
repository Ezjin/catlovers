import requests
from datetime import datetime
import pandas as pd
import json

def main():
    response = requests.get("https://cat-fact.herokuapp.com/facts/random?animal_type=cat&amount=2")
    date_today = datetime.today().strftime("%Y-%m-%d")

    if response.ok:
        data = response.json()

        with open(f"data/raw/{date_today}_facts.json"):
            json.dump(data, f, indent=2, ensure_ascii = False)

        df = pd.DataFrame(data)
        df_filtrada = df[["_id", "text", "updatedAt", "sentCount"]]
        df_filtrada.columns = ["id", "text", "updated", "sent_count"]
        df_filtrada.to_csv(f"data/processed/{date_today}_processed_facts.csv", index = False)
        
    else:
        print(f"Error: Status code - {response.status_code}")

if __name__ == "__main__":
    main()
