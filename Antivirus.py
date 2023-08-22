import os
import subprocess
import hashlib
import sqlite3
import concurrent.futures
import tempfile
import shutil
import webbrowser
import glob
def is_file_infected_md5(md5):
    md5_connection = sqlite3.connect("MD5basedatabase.db")
    main_connection = sqlite3.connect("main.db")
    daily_connection = sqlite3.connect("daily.db")
    old_virus_base_connection = sqlite3.connect("oldvirusbase.db")
    virus_base_connection = sqlite3.connect("virusbase.db")
    full_md5_connection = sqlite3.connect("Hash.db")
    
    # Check in the MD5base table
    md5_command = md5_connection.execute("SELECT COUNT(*) FROM MD5base WHERE field1 = ?;", (md5,))
    md5_result = md5_command.fetchone()[0]
    if md5_result > 0:
        md5_connection.close()
        return True
    
    # Check in the main table
    main_command = main_connection.execute("SELECT COUNT(*) FROM main WHERE field2 = ?;", (md5,))
    main_result = main_command.fetchone()[0]
    if main_result > 0:
        main_connection.close()
        return True
    
    # Check in the daily table
    daily_command = daily_connection.execute("SELECT COUNT(*) FROM daily WHERE field2 = ?;", (md5,))
    daily_result = daily_command.fetchone()[0]
    if daily_result > 0:
        daily_connection.close()
        return True
    
    # Check in the oldvirusbase table
    old_virus_base_command = old_virus_base_connection.execute("SELECT COUNT(*) FROM oldvirusbase WHERE field2 = ?;", (md5,))
    old_virus_base_result = old_virus_base_command.fetchone()[0]
    if old_virus_base_result > 0:
        old_virus_base_connection.close()
        return True
    
    # Check in the oldvirusbase2 table
    old_virus_base2_command = old_virus_base_connection.execute("SELECT COUNT(*) FROM oldvirusbase2 WHERE field1 = ?;", (md5,))
    old_virus_base2_result = old_virus_base2_command.fetchone()[0]
    if old_virus_base2_result > 0:
        old_virus_base_connection.close()
        return True
    
    # Check in the oldvirusbase3 table
    old_virus_base3_command = old_virus_base_connection.execute("SELECT COUNT(*) FROM oldvirusbase3 WHERE field2 = ?;", (md5,))
    old_virus_base3_result = old_virus_base3_command.fetchone()[0]
    if old_virus_base3_result > 0:
        old_virus_base_connection.close()
        return True
    
    # Check in the virusbase table
    virus_base_command = virus_base_connection.execute("SELECT COUNT(*) FROM virusbase WHERE field1 = ?;", (md5,))
    virus_base_result = virus_base_command.fetchone()[0]
    if virus_base_result > 0:
        virus_base_connection.close()
        return True
    
    # Check in the virusbase2 table
    virus_base2_command = virus_base_connection.execute("SELECT COUNT(*) FROM virusbase2 WHERE field1 = ?;", (md5,))
    virus_base2_result = virus_base2_command.fetchone()[0]
    if virus_base2_result > 0:
        virus_base_connection.close()
        return True
    
    # Check in the HashDB table
    full_md5_command = full_md5_connection.execute("SELECT COUNT(*) FROM HashDB WHERE hash = ?;", (md5,))
    full_md5_result = full_md5_command.fetchone()[0]
    if full_md5_result > 0:
        full_md5_connection.close()
        return True
    
    md5_connection.close()
    main_connection.close()
    daily_connection.close()
    old_virus_base_connection.close()
    virus_base_connection.close()
    full_md5_connection.close()
    return False
def is_file_infected_sha1(sha1):
    # Check in the SHA256hashes database for SHA1 hashes
    database_path_sha256_hashes = "SHA256hashes.db"
    connection_sha256_hashes = sqlite3.connect(database_path_sha256_hashes)

    sha1_command_text = "SELECT EXISTS(SELECT 1 FROM malwarescomsha1 WHERE field1 = ? LIMIT 1);"
    sha1_result = connection_sha256_hashes.execute(sha1_command_text, (sha1,)).fetchone()

    if sha1_result and sha1_result[0]:
        connection_sha256_hashes.close()
        return True

    # If the SHA1 hash was not found in the SHA256hashes.db database,
    # Check in the abusech.db database for SHA1 hashes in SSLBL table with field2.
    database_path_abusech = "abusech.db"
    connection_abusech = sqlite3.connect(database_path_abusech)

    sslbl_command_text = "SELECT EXISTS(SELECT 1 FROM SSLBL WHERE field2 = ? LIMIT 1);"
    sslbl_result = connection_abusech.execute(sslbl_command_text, (sha1,)).fetchone()

    connection_abusech.close()

    if sslbl_result and sslbl_result[0]:
        return True
    # If the code reaches this point, it means the SHA1 hash was not found in both databases.
    return False

def is_file_infected_sha256(sha256):
    database_path_0 = "batchvirusbase.db"
    database_path_sha256 = "SHA256databasesqlite.db"
    database_path_fake_domain = "vxugfakedomain.db"
    database_path_sha256_hashes = "SHA256hashes.db"
    database_path_emotet_ioc = "IOC_Emotet.db"  # New database path
    database_path_full_sha256 = "full_sha256.db"  # New database path
    database_path_abusech = "abusech.db"  # New database path

    # Check in the SHA256 table
    connection = sqlite3.connect(database_path_0)

    sha256_command_text = "SELECT EXISTS(SELECT 1 FROM SHA256 WHERE field1 = ? LIMIT 1) FROM SHA256 WHERE field1 = ?;"
    sha256_result = connection.execute(sha256_command_text, (sha256, sha256)).fetchone()

    if sha256_result and sha256_result[0]:
        connection.close()
        return True, ""

    # Check in the abusech database
    connection_abusech = sqlite3.connect(database_path_abusech)

    abusech_command_text = "SELECT EXISTS(SELECT 1 FROM full_sha256 WHERE field3 = ? LIMIT 1) FROM full_sha256 WHERE field3 = ?;"
    abusech_result = connection_abusech.execute(abusech_command_text, (sha256, sha256)).fetchone()

    connection_abusech.close()

    if abusech_result and abusech_result[0]:
        return True

    # Check in the full_sha256 database
    connection_full_sha256 = sqlite3.connect(database_path_full_sha256)

    full_sha256_command_text = "SELECT EXISTS(SELECT 1 FROM full_sha256 WHERE field1 = ? LIMIT 1) FROM full_sha256 WHERE field1 = ?;"
    full_sha256_result = connection_full_sha256.execute(full_sha256_command_text, (sha256, sha256)).fetchone()

    connection_full_sha256.close()

    if full_sha256_result and full_sha256_result[0]:
        return True

    # Check in the SHA256 database
    connection_sha256 = sqlite3.connect(database_path_sha256)

    sha256_command_text = "SELECT EXISTS(SELECT 1 FROM SHA256 WHERE field1 = ? LIMIT 1) FROM SHA256 WHERE field1 = ?;"
    sha256_result = connection_sha256.execute(sha256_command_text, (sha256, sha256)).fetchone()

    connection_sha256.close()

    if sha256_result and sha256_result[0]:
        return True

    # Check in the vxugfakedomain database
    connection_fake_domain = sqlite3.connect(database_path_fake_domain)

    fake_domain_command_text = "SELECT EXISTS(SELECT 1 FROM vxugfakedomain WHERE field5 = ? LIMIT 1) FROM vxugfakedomain WHERE field5 = ?;"
    fake_domain_result = connection_fake_domain.execute(fake_domain_command_text, (sha256, sha256)).fetchone()

    connection_fake_domain.close()

    if fake_domain_result and fake_domain_result[0]:
        return True

    # Check in the SHA256hashes database
    connection_sha256_hashes = sqlite3.connect(database_path_sha256_hashes)

    sha256_hashes_command_text = "SELECT EXISTS(SELECT 1 FROM SHA256hashes WHERE field1 = ? LIMIT 1) FROM SHA256hashes WHERE field1 = ?;"
    sha256_hashes_result = connection_sha256_hashes.execute(sha256_hashes_command_text, (sha256, sha256)).fetchone()

    connection_sha256_hashes.close()

    if sha256_hashes_result and sha256_hashes_result[0]:
        return True

    # Check in the Emotet IOC database
    connection_emotet_ioc = sqlite3.connect(database_path_emotet_ioc)  # New database connection

    emotet_ioc_command_text = "SELECT EXISTS(SELECT 1 FROM IOC_Emotet WHERE field1 = ? LIMIT 1) FROM IOC_Emotet WHERE field1 = ?;"  # New table and field names
    emotet_ioc_result = connection_emotet_ioc.execute(emotet_ioc_command_text, (sha256, sha256)).fetchone()

    connection_emotet_ioc.close()

    if emotet_ioc_result and emotet_ioc_result[0]:
        return True

    # If the code reaches this point, it means the record with the specified field1 value was not found in any of the databases.
    return False

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def calculate_sha1(file_path):
    hash_sha1 = hashlib.sha1()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()
def calculate_sha256(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()
def scan_folder_with_clamscan(folder_path):
    try:
        current_folder = os.getcwd()
        clamscan_path = os.path.join(current_folder, "clamscan")
        subprocess.run([clamscan_path, "-r", "--heuristic-alerts=yes", "--remove=yes", "--detect-pua=yes", "--normalize=no", folder_path])
    except Exception as e:
        print(f"Error running ClamScan: {e}")
def delete_file(file_path):
    try:
        os.remove(file_path)
        return f"Infected file deleted: {file_path}"
    except Exception as e:
        return f"Error deleting {file_path}: {e}"

def scan_file(file_path):
    try:
        file_size = os.path.getsize(file_path)
        
        # Skip empty files
        if file_size == 0:
            return f"Clean file: {file_path}"
        
        # Calculate hash values
        md5 = calculate_md5(file_path)
        sha1 = calculate_sha1(file_path)
        sha256 = calculate_sha256(file_path)
        
        # Check if the file is infected using hash-based methods
        if is_file_infected_md5(md5) or is_file_infected_sha1(sha1) or is_file_infected_sha256(sha256):
            print(f"Infected file detected: {file_path}\nMD5 Hash: {md5}")
            print(delete_file(file_path))  # Automatically delete infected file
        else:
            return f"Clean file: {file_path}"
        
    except PermissionError:
        return f"Access denied: {file_path}"
    except Exception as e:
        return f"Error processing {file_path}: {e}"

def scan_folder_parallel(folder_path):
    infected_files = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        file_paths = [os.path.join(root, file) for root, _, files in os.walk(folder_path) for file in files]
        results = executor.map(scan_file, file_paths)
        
        for result in results:
            if result and result.startswith("Infected"):
                infected_files.append(result)
            elif result:
                print(result)
    
    if infected_files:
        print("\nInfected files:")
        for infected_file in infected_files:
            print(infected_file)
    else:
        print("\nNo infected files found.")

def scan_running_files_with_custom_method():
    temp_dir = tempfile.mkdtemp(prefix="running_file_scan_")

    try:
        running_files = []

        for pid in os.listdir("/proc"):
            if pid.isdigit():
                pid_dir = os.path.join("/proc", pid)
                exe_link = os.path.join(pid_dir, "exe")

                try:
                    exe_path = os.readlink(exe_link)
                    if os.path.exists(exe_path) and os.path.isfile(exe_path):
                        running_files.append(exe_path)
                except (OSError, FileNotFoundError):
                    pass

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(scan_and_check_file, running_files, [temp_dir] * len(running_files))

        print("Custom scan finished.")

    except Exception as e:
        print(f"Error scanning running files: {e}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def scan_and_check_file(file_path, temp_dir):
    try:
        md5 = calculate_md5(file_path)
        sha1 = calculate_sha1(file_path)
        sha256 = calculate_sha256(file_path)
        if is_file_infected_md5(md5) or is_file_infected_sha1(sha1) or is_file_infected_sha256(sha256):
            print(f"Infected file detected: {file_path}")
            print(delete_file(file_path))  # Automatically delete infected file 
        else:
            print(f"Clean file: {file_path}")
        
        shutil.copy2(file_path, temp_dir)
    except Exception as e:
        print(f"Error scanning file {file_path}: {e}")

def scan_running_files_with_custom_and_clamav_continuous():
    try:
        while True:
            # Create a ThreadPoolExecutor to run ClamAV and custom scans concurrently
            with concurrent.futures.ThreadPoolExecutor() as executor:
                clamav_scan = executor.submit(scan_running_files_with_clamav)
                custom_scan = executor.submit(scan_running_files_with_custom_method)
                clamonacc_scan = executor.submit(scan_running_files_with_clamav)
                # Wait for both scans to complete
                clamav_scan.result()
                custom_scan.result()
                clamonacc_scan.result()

            print("Waiting for the next combined scan...")

    except KeyboardInterrupt:
        print("\nContinuous combined scan stopped.")

def scan_running_files_with_clamav():
    # Create a temporary directory to store copies of running files
    temp_dir = tempfile.mkdtemp(prefix="running_file_scan_")

    try:
        # Iterate through the /proc directory to find running process IDs
        for pid in os.listdir("/proc"):
            if pid.isdigit():
                pid_dir = os.path.join("/proc", pid)
                exe_link = os.path.join(pid_dir, "exe")
                
                try:
                    # Resolve symbolic link to get the path of the running file
                    exe_path = os.readlink(exe_link)
                    if os.path.exists(exe_path) and os.path.isfile(exe_path):
                        # Copy the running file to the temporary directory for scanning
                        shutil.copy2(exe_path, temp_dir)
                except (OSError, FileNotFoundError):
                    # Some processes may have restricted permissions, skip them
                    pass

        # Perform a ClamAV scan on the copied running files
        clamscan_path = shutil.which("clamscan")
        if clamscan_path:
            print("Scanning running files with ClamAV...")
            subprocess.run([clamscan_path, "-r", temp_dir])
        else:
            print("ClamAV not found, skippiget_running_firefox_urlsng running file scan.")

    except Exception as e:
        print(f"Error scanning running files: {e}")

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
def is_website_infected(url):
    databases = ['viruswebsites.db', 'viruswebsite.db', 'viruswebsitesbig.db', 'virusip.db', 'viruswebsitessmall.db','abusech.db']
    formatted_url = format_url(url)  # URL'yi biçimlendir
    ip_prefixed_url = "0.0.0.0" + formatted_url  # Başına 0.0.0.0 ve format_url eklenmiş URL
    zero_url = "0.0.0.0" # Başına 0.0.0.0 eklenmiş URL

    for database in databases:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        queries = [
            "SELECT * FROM viruswebsites WHERE field1 = ?",
            "SELECT * FROM viruswebsite WHERE field1 = ?",
            "SELECT * FROM inactive WHERE field1 = ?",
            "SELECT * FROM malwarebazaar WHERE field1 = ?",
            "SELECT * FROM ultimatehostblacklist WHERE field1 = ?",
            "SELECT * FROM continue WHERE field1 = ?",
            "SELECT * FROM virusip WHERE field1 = ?"
            "SELECT * FROM mcafee WHERE field1 = ?",
            "SELECT * FROM full_urls WHERE field1 = ?",
            "SELECT * FROM full_domains WHERE field1 = ?",
            "SELECT * FROM paloaltofirewall WHERE field1 = ?",
            "SELECT * FROM \"full_ip-port\" WHERE field1 = ?"
        ]

        for query in queries:
            try:
                result = cursor.execute(query, (formatted_url,)).fetchone()
                if result:
                    cursor.close()
                    conn.close()
                    return True

                result_ip = cursor.execute(query, (ip_prefixed_url,)).fetchone()
                if result_ip:
                    cursor.close()
                    conn.close()
                    return True

                result_zero = cursor.execute(query, (zero_url,)).fetchone()
                if result_zero:
                    cursor.close()
                    conn.close()
                    return True
            except sqlite3.OperationalError:
                pass  # Tablo bulunmadı hatasını yok say

        cursor.close()
        conn.close()
def format_url(url):
    if url:
        formatted_url = url.strip().lower()
        if formatted_url.startswith("https://"):
            formatted_url = formatted_url.replace("https://", "")
        elif formatted_url.startswith("http://"):
            formatted_url = formatted_url.replace("http://", "")
        formatted_url = formatted_url.split('/')[0]
        
        return formatted_url
    
    return url
def get_running_ips():
    try:
        netstat_output = subprocess.run(["netstat", "-tn"], capture_output=True, text=True)
        lines = netstat_output.stdout.split("\n")[2:]  # İlk iki satırı atla
        running_ips = set()

        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                ip_port = parts[4]
                ip = ip_port.split(":")[0]
                running_ips.add(ip)

        return list(running_ips)
    except Exception as e:
        print(f"Error getting running IPs: {e}")
        return []

def real_time_web_protection():
    infected_ips = []
    while True:
        running_ips = get_running_ips()
        
        for ip in running_ips:
            if is_website_infected(ip):
                print(f"The IP address {ip} is infected.")
                infected_ips.append(ip)
                disconnect_ip(ip)
                open_webguard_page()
            else:
                print(f"The IP address {ip} is clean.")
        return infected_ips
def disconnect_ip(ip):
    try:
        # Örnek olarak Linux üzerinde IP adresini engellemek için kullanılabilecek bir komut
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
        print(f"Disconnected IP address: {ip}")
    except Exception as e:
        print(f"Error disconnecting IP address {ip}: {e}")
def open_webguard_page():
    # Geçerli dizinin yolu
    current_directory = os.getcwd()

    # webguard.html dosyasının yolu
    webguard_path = os.path.join(current_directory, 'WebGuard.html')

    # webguard.html dosyasını Firefox ile aç
    webbrowser.get('firefox').open('file://' + webguard_path)
def find_firefox_profile(default_esr=False):
    try:
        # Kullanıcının ev dizinini alın
        home_dir = os.path.expanduser("~")

        # Firefox profil klasörünü bulmak için glob kullanın
        profile_paths = glob.glob(os.path.join(home_dir, ".mozilla/firefox/*default"))
        
        if default_esr:
            profile_paths = glob.glob(os.path.join(home_dir, ".mozilla/firefox/*default-esr"))

        if profile_paths:
            return profile_paths[0]
        else:
            return None
    except Exception as e:
        print(f"Error finding Firefox profile: {e}")
        return None
def access_firefox_history_continuous():
    try:
        # Firefox profil klasörünü bulun
        profile_path = find_firefox_profile()

        if profile_path is None:
            print("Firefox profile not found.")
            return

        # Firefox geçmiş veritabanının yolunu oluşturun
        firefox_db_path = os.path.join(profile_path, "places.sqlite")

        if not os.path.exists(firefox_db_path):
            # If the database doesn't exist in the default folder, try default-esr folder
            profile_path_esr = find_firefox_profile(default_esr=True)
            if profile_path_esr:
                firefox_db_path = os.path.join(profile_path_esr, "places.sqlite")
            else:
                print("Firefox history database not found.")
                return

        last_visited_websites = []  # To keep track of the last visited websites

        while True:
            # Firefox geçmiş veritabanını geçici bir klasöre kopyalayın
            temp_dir = tempfile.mkdtemp(prefix="firefox_history_")
            copied_db_path = os.path.join(temp_dir, "places.sqlite")
            shutil.copy2(firefox_db_path, copied_db_path)

            # Kopyalanan veritabanıyla bağlantı kurun
            connection = sqlite3.connect(copied_db_path)
            cursor = connection.cursor()

            # Ziyaret edilen siteleri sorgu ile alın
            query = "SELECT title, url FROM moz_places ORDER BY id DESC LIMIT 5;"
            cursor.execute(query)
            results = cursor.fetchall()

            # Ziyaret edilen siteleri tarayın ve sonuçları gösterin
            for row in results:
                title, url = row
                print(f"Scanning URL: {url}")
                if is_website_infected(url):
                    print(f"The website is infected: {url}")
                    if last_visited_websites:
                        last_visited_websites.pop()  # Remove the last visited website
                        open_webguard_page()  # Open the webguard.html file
                else:
                    print(f"The website is clean: {url}")

                if len(last_visited_websites) >= 5:
                    last_visited_websites.pop(0)  # Remove the oldest visited website
                last_visited_websites.append(url)

            # Bağlantıyı kapatın ve geçici klasörü temizleyin
            connection.close()
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"Error accessing Firefox history: {e}")
def run_clamonacc_with_remove():
    try:
        # clamavdaki clamonacc komutunu çalıştırırken "--remove" argümanını kullanarak çağırın
        subprocess.run(["clamonacc", "--remove"], check=True)
        print("clamonacc successfully executed with --remove argument.")
    except subprocess.CalledProcessError as e:
        print("Error executing clamonacc:", e)
def main():
    while True:
        print("Select an option:")
        print("1. Perform a file scan")
        print("2. Enable real-time protection (scan running files with ClamAV)")
        print("3. Check is website infected or not by typing.")
        print("4. Real-time web protection")
        print("5.Real-time web and file protection")
        print("6. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            folder_path = input("Enter the path of the folder to scan: ")

            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                print(f"Scanning folder: {folder_path} with ClamScan...")
                scan_folder_with_clamscan(folder_path)
                print(f"\nScanning folder: {folder_path} with Known Hashes...")
                scan_folder_parallel(folder_path)
            else:
                print("Invalid folder path.")

        elif choice == "2":
            scan_running_files_with_custom_and_clamav_continuous()

        elif choice == "3":
            website_url = input("Enter the website URL to check: ")
            if is_website_infected(website_url):
                print("The website is infected.")
            else:
                print("The website is clean.")

        elif choice == "4":
            # Paralel olarak iki fonksiyonu başlat
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                executor.submit(real_time_web_protection)
                executor.submit(access_firefox_history_continuous)
        elif choice == "5":
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
               executor.submit(real_time_web_protection)
               executor.submit(access_firefox_history_continuous)
               executor.submit(scan_running_files_with_custom_and_clamav_continuous)
            break 
        elif choice == "6":
            print("Exiting...")
            break 
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()