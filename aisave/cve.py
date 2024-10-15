import requests, zipfile, io, os, sqlite3, logging, shutil, json, re
from aisave import base

url = "https://github.com/CVEProject/cvelistV5/archive/refs/heads/main.zip"

def regexp(pattern, text):
    return re.search(pattern, text, re.IGNORECASE) is not None

def search_cves(string):
    conn = sqlite3.connect(os.path.join(base, "data", 'cves.db'))
    conn.create_function("REGEXP", 2, regexp)
    cursor = conn.cursor()
    searches = {}
    if string[:4].lower() == "cve-":
        cursor.execute("SELECT * FROM cve_data WHERE cve_name LIKE ?", (f'%{string}%',))
        rows = cursor.fetchall()
        for row in rows:
            searches[row] = 1
    else:
        for term in string.split():
            cursor.execute("SELECT * FROM cve_data WHERE description LIKE ?", (f'%{term}%',))
            rows = cursor.fetchall()
            for row in rows:
                if row not in searches:
                    searches[row] = 1
                else:
                    searches[row] += 1
    return searches

def update_cves():
    if download_cves():
        process_cves()
        shutil.rmtree(os.path.join(base, "data", "cvelistV5-main"))

def download_cves():
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to download cve zip file from {url}, response code {response.status_code}")
        return False
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    out_dir = os.path.join(base, "data")
    zip_file.extractall(out_dir)
    return True

def process_cves():
    os.remove(os.path.join(base, "data", "cves.db"))
    conn = sqlite3.connect(os.path.join(base, "data", "cves.db"))
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cve_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cve_name TEXT NOT NULL,
        description TEXT NOT NULL,
        score REAL
    )
    ''')
    for year in os.listdir(os.path.join(base, "data", "cvelistV5-main", "cves")):
        if year.isdigit():
            for folder in os.listdir(os.path.join(base, "data", "cvelistV5-main", "cves", year)):
                for cve in os.listdir(os.path.join(base, "data", "cvelistV5-main", "cves", year, folder)):
                    with open(os.path.join(base, "data", "cvelistV5-main", "cves", year, folder, cve), 'r') as file:
                        cve_dict = json.load(file)
                        if cve_dict["cveMetadata"]["state"] == "PUBLISHED":
                            cve_name = cve_dict["cveMetadata"]["cveId"]
                            cna = cve_dict["containers"]["cna"]
                            description = "n/a"
                            for desc in cna["descriptions"]:
                                if desc["lang"] == "en":
                                    description = desc["value"]
                            if description == "n/a":
                                continue
                            score = 0.0
                            score_count = 0
                            if "metrics" in cna.keys():
                                for metrics in cna["metrics"]:
                                    for metric in metrics.keys():
                                        if "baseScore" in metrics[metric]:
                                            score += metrics[metric]["baseScore"]
                                            score_count += 1
                            affect_list = []
                            for affected in cna["affected"]:
                                if "product" not in affected.keys():
                                    continue
                                if affected["product"] != "n/a":
                                    version_list = []
                                    if "versions" not in affected.keys():
                                        continue
                                    for version in affected["versions"]:
                                        if version["status"] != "affected":
                                            continue
                                        if "lessThanOrEqual" in version.keys():
                                            version_list.append(f"less than or equal to {version['lessThanOrEqual']}")
                                        elif "lessThan" in version.keys():
                                            version_list.append(f"less than {version['lessThan']}")
                                        elif version["version"] != "n/a" and version["version"] != "unspecified":
                                            version_list.append(version['version'])
                                    if len(version_list) > 0:
                                        affect_list.append(f"{affected['product']} version(s), {', '.join(version_list)}")
                            if len(affect_list) > 0:
                                description += f"\nAffected: {'; '.join(affect_list)}"
                            if score_count > 0:
                                score /= score_count
                            cursor.execute('''INSERT INTO cve_data (cve_name, description, score) VALUES (?, ?, ?)''', (cve_name, description, score))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    process_cves()
