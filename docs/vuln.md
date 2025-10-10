
Test results:
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b110_try_except_pass.html
   Location: .\access\views.py:196:8
195                 )
196             except:
197                 pass  # Don't fail access check if logging fails
198

--------------------------------------------------
>> Issue: [B404:blacklist] Consider possible security implications associated with the subprocess module.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_imports.html#b404-import-subprocess
   Location: .\adminstrator\views.py:14:0
13      from datetime import datetime
14      import subprocess
15

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b607_start_process_with_partial_path.html
   Location: .\adminstrator\views.py:262:12
261             try:
262                 subprocess.run(
263                     ["pg_dump", "-U", db_user, db_name, "-f", backup_file],
264                     check=True, env=env
265                 )
266                 return Response({"status": "success", "backup_file": backup_file}, status=status.HTTP_200_OK)

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b603_subprocess_without_shell_equals_true.html
   Location: .\adminstrator\views.py:262:12
261             try:
262                 subprocess.run(
263                     ["pg_dump", "-U", db_user, db_name, "-f", backup_file],
264                     check=True, env=env
265                 )
266                 return Response({"status": "success", "backup_file": backup_file}, status=status.HTTP_200_OK)

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b607_start_process_with_partial_path.html
   Location: .\adminstrator\views.py:286:12
285             try:
286                 subprocess.run(
287                     ["psql", "-U", db_user, "-d", db_name, "-f", backup_path],
288                     check=True, env=env
289                 )
290                 return Response({"status": "success", "message": "Database restored"}, status=status.HTTP_200_OK)

--------------------------------------------------
>> Issue: [B603:subprocess_without_shell_equals_true] subprocess call - check for execution of untrusted input.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b603_subprocess_without_shell_equals_true.html
   Location: .\adminstrator\views.py:286:12
285             try:
286                 subprocess.run(
287                     ["psql", "-U", db_user, "-d", db_name, "-f", backup_path],
288                     check=True, env=env
289                 )
290                 return Response({"status": "success", "message": "Database restored"}, status=status.HTTP_200_OK)

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: .\authenication\views.py:216:27
215             # Generate new OTP
216             new_otp_code = str(random.randint(100000, 999999))
217             otp_obj.otp_code = new_otp_code

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'django-insecure-0yu!yvip*&mr%r88wklonhzfhk^9#4)g6d9a&f0y%c5=ybk%cl'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: .\backend\settings.py:28:13
27      # SECURITY WARNING: keep the secret key used in production secret!
28      SECRET_KEY = 'django-insecure-0yu!yvip*&mr%r88wklonhzfhk^9#4)g6d9a&f0y%c5=ybk%cl'
29

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'piik ctai zlyk owfm '
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: .\backend\settings.py:167:22
166     EMAIL_HOST_USER = 'testorder1245@gmail.com'
167     EMAIL_HOST_PASSWORD = 'piik ctai zlyk owfm '  # Replace with actual app password
168     DEFAULT_FROM_EMAIL = 'testorder1245@gmail.com'

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: .\cardmanage\models.py:61:23
60              prefix = "DGBC"
61              code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
62              return f"{prefix} {code}"

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: .\cardmanage\pdf_service.py:41:23
40              prefix = "DGBC"
41              code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
42              return f"{prefix} {code}"

--------------------------------------------------
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b110_try_except_pass.html
   Location: .\cardmanage\pdf_service.py:98:20
97                                  return ImageReader(img_buffer)
98                          except Exception as img_error:
99                              pass
100             except Exception as e:

--------------------------------------------------
>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b110_try_except_pass.html
   Location: .\cardmanage\pdf_service.py:100:8
99                              pass
100             except Exception as e:
101                 pass
102

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: .\cardmanage\serializers.py:105:38
104                 while True:
105                     rfid_number = ''.join(random.choices(string.digits, k=10))
106                     if not Card.objects.filter(rfid_number=rfid_number).exists():

--------------------------------------------------
>> Issue: [B311:blacklist] Standard pseudo-random generators are not suitable for security/cryptographic purposes.
   Severity: Low   Confidence: High
   CWE: CWE-330 (https://cwe.mitre.org/data/definitions/330.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b311-random
   Location: .\cardmanage\views.py:385:46
384                         while True:
385                             rfid_number = ''.join(random.choices(string.digits, k=10))
386                             if not Card.objects.filter(rfid_number=rfid_number).exists():

--------------------------------------------------
>> Issue: [B106:hardcoded_password_funcarg] Possible hardcoded password: 'admin123'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b106_hardcoded_password_funcarg.html
   Location: .\staff\tests.py:36:26
35          def setUp(self):
36              self.admin_user = User.objects.create_user(
37                  username='admin',
38                  password='admin123',
39                  user_type='administrator'
40              )
41              self.staff_data = {

--------------------------------------------------

Code scanned:
        Total lines of code: 4594
        Total lines skipped (#nosec): 0

Run metrics:
        Total issues (by severity):
                Undefined: 0
                Low: 16
                Medium: 0
                High: 0
        Total issues (by confidence):
                Undefined: 0
                Low: 0
                Medium: 3
                High: 13
Files skipped (0):


csv  upload
