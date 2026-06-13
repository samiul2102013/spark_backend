param(
    [string]$BaseUrl = "http://localhost/api/v1"
)

$pass = 0
$fail = 0

function Test-Step {
    param($Name, $Method, $Path, $Body, $Token, $ExpectedStatus)
    $url = "$BaseUrl$Path"
    $headers = @{ "Content-Type" = "application/json" }
    if ($Token) { $headers["Authorization"] = "Bearer $Token" }

    if ($Body) {
        $tmp = [System.IO.Path]::GetTempFileName() + ".json"
        $Body | Set-Content -Path $tmp -Encoding Ascii -NoNewline
        try {
            $r = curl.exe -s -X $Method $url -H @($headers.Keys | ForEach-Object { "$($_): $($headers[$_])" }) -d "`@$tmp"
        } finally { Remove-Item -Force $tmp -ErrorAction SilentlyContinue }
    } else {
        $r = curl.exe -s -X $Method $url -H @($headers.Keys | ForEach-Object { "$($_): $($headers[$_])" })
    }

    try { $parsed = $r | ConvertFrom-Json } catch { $parsed = $null }
    $ok = $parsed -and $parsed.status -eq "success"
    if ($ok) { $script:pass++; Write-Host "  ✓ $Name" -ForegroundColor Green }
    else {
        $script:fail++
        $msg = if ($parsed) { $parsed.message } else { $r.Substring(0, [Math]::Min(100, $r.Length)) }
        Write-Host "  ✗ $Name — $msg" -ForegroundColor Red
    }
    return $parsed
}

function Test-Step-Raw {
    param($Name, $Method, $Path, $Body, $Token)
    $url = "$BaseUrl$Path"
    $headers = @{ "Content-Type" = "application/json" }
    if ($Token) { $headers["Authorization"] = "Bearer $Token" }

    if ($Body) {
        $tmp = [System.IO.Path]::GetTempFileName() + ".json"
        $Body | Set-Content -Path $tmp -Encoding Ascii -NoNewline
        try {
            $r = curl.exe -s -X $Method $url -H @($headers.Keys | ForEach-Object { "$($_): $($headers[$_])" }) -d "`@$tmp"
        } finally { Remove-Item -Force $tmp -ErrorAction SilentlyContinue }
    } else {
        $r = curl.exe -s -X $Method $url -H @($headers.Keys | ForEach-Object { "$($_): $($headers[$_])" })
    }
    return $r
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  SPARK API — Auth Endpoint Test Suite" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── 0. Health Check ──────────────────────────────────────
Write-Host "`n── 0. Health Check ────────────────────────" -ForegroundColor Yellow
$health = Test-Step -Name "Health endpoint" -Method GET -Path "/health/" -Body $null

# ── 1. Register Resident ─────────────────────────────────
Write-Host "`n── 1. Resident Registration ───────────────" -ForegroundColor Yellow
$register = Test-Step -Name "Register John (lat:17.97, lng:-76.79)" -Method POST -Path "/auth/register/" -Body @"
{"phone":"+18765550001","full_name":"John Doe","household_size":3,"medical_needs":"Asthma","latitude":17.9712,"longitude":-76.7936}
"@

# ── 2. Register Jane in different location ───────────────
$register2 = Test-Step -Name "Register Jane (lat:18.01, lng:-76.75)" -Method POST -Path "/auth/register/" -Body @"
{"phone":"+18765550002","full_name":"Jane Smith","household_size":5,"medical_needs":"None","latitude":18.0150,"longitude":-76.7500}
"@

# ── 3. OTP Login for John ────────────────────────────────
Write-Host "`n── 2. OTP Flow (get code from Docker logs) ─" -ForegroundColor Yellow
Write-Host "  Run: docker compose logs django --tail 5" -ForegroundColor DarkGray
Write-Host "  Then copy the 6-digit OTP for +18765550001" -ForegroundColor DarkGray
$otp1 = Read-Host "  Enter OTP for +18765550001"
if ($otp1) {
    $otp_verify = Test-Step -Name "Verify OTP for John" -Method POST -Path "/auth/otp/verify/" -Body @"
{"phone":"+18765550001","code":"$otp1"}
"@
    $jwt = if ($otp_verify -and $otp_verify.data.access) { $otp_verify.data.access } else { $null }
}

# ── 4. Profile (authenticated) ──────────────────────────
Write-Host "`n── 3. Profile ──────────────────────────────" -ForegroundColor Yellow
if ($jwt) {
    Test-Step -Name "GET profile" -Method GET -Path "/users/profile/" -Token $jwt
    Test-Step -Name "PUT profile" -Method PUT -Path "/users/profile/" -Body @'
{"full_name":"John Updated","household_size":2}
'@ -Token $jwt
}

# ── 5. Login as Admin (hardcoded) ───────────────────────
Write-Host "`n── 4. Admin Login ──────────────────────────" -ForegroundColor Yellow
$admin_login = Test-Step -Name "Login admin@test.com / admin1234" -Method POST -Path "/auth/login/" -Body @'
{"username":"admin@test.com","password":"admin1234"}
'@
$admin_jwt = if ($admin_login -and $admin_login.data.access) { $admin_login.data.access } else { $null }

# ── 6. Invite Government ───────────────────────────────
Write-Host "`n── 5. Government Invite ────────────────────" -ForegroundColor Yellow
$invite = Test-Step -Name "Invite gov@demo.com" -Method POST -Path "/admin/users/invite/" -Body @'
{"email":"gov@demo.com","full_name":"Demo Gov Official"}
'@ -Token $admin_jwt

# ── 7. Accept Invite ───────────────────────────────────
Write-Host "`n── 6. Accept Invite ────────────────────────" -ForegroundColor Yellow
Write-Host "  Copy the invite token from:" -ForegroundColor DarkGray
Write-Host "  docker compose logs django --tail 2" -ForegroundColor DarkGray
$token = Read-Host "  Paste invite token (full JWT)"
if ($token) {
    Test-Step -Name "Validate invite token" -Method POST -Path "/auth/invite/$token/"
    Test-Step -Name "Accept invite" -Method POST -Path "/auth/invite/accept/" -Body @"
{"token":"$token","password":"DemoGov123","confirm_password":"DemoGov123"}
"@
}

# ── 8. Login as Government ─────────────────────────────
Write-Host "`n── 7. Government Login ─────────────────────" -ForegroundColor Yellow
$gov_login = Test-Step -Name "Login gov@demo.com / DemoGov123" -Method POST -Path "/auth/login/" -Body @'
{"username":"gov@demo.com","password":"DemoGov123"}
'@
$gov_jwt = if ($gov_login -and $gov_login.data.access) { $gov_login.data.access } else { $null }

# ── 9. Admin → Set Coordinator ─────────────────────────
Write-Host "`n── 8. Promote to Coordinator ──────────────" -ForegroundColor Yellow
if ($admin_jwt) {
    Test-Step -Name "John → coordinator" -Method PATCH -Path "/admin/users/+18765550001/set-role/" -Body @'
{"role":"coordinator"}
'@ -Token $admin_jwt
}

# ── 10. Biometric ──────────────────────────────────────
Write-Host "`n── 9. Biometric ────────────────────────────" -ForegroundColor Yellow
if ($jwt) {
    Test-Step -Name "Register biometric" -Method POST -Path "/auth/biometric/register/" -Body @'
{"key":"john-fingerprint-abc123"}
'@ -Token $jwt
}
Test-Step -Name "Biometric login" -Method POST -Path "/auth/biometric/login/" -Body @'
{"key":"john-fingerprint-abc123"}
'@

# ── 11. Offline Token ──────────────────────────────────
Write-Host "`n── 10. Offline Token ───────────────────────" -ForegroundColor Yellow
if ($jwt) {
    Test-Step -Name "Issue offline token" -Method POST -Path "/auth/offline-token/" -Token $jwt
}

# ── 12. Change Password ────────────────────────────────
Write-Host "`n── 11. Change Password ─────────────────────" -ForegroundColor Yellow
if ($gov_jwt) {
    Test-Step -Name "Gov change password" -Method PUT -Path "/users/change-password/" -Body @'
{"old_password":"DemoGov123","new_password":"NewGov456","confirm_password":"NewGov456"}
'@ -Token $gov_jwt
}

# ── 13. Forgot / Reset Password ────────────────────────
Write-Host "`n── 12. Password Reset ──────────────────────" -ForegroundColor Yellow
Test-Step -Name "Forgot password (email)" -Method POST -Path "/auth/forgot-password/" -Body @'
{"identifier":"admin@test.com"}
'@

# ── 14. Logout ─────────────────────────────────────────
Write-Host "`n── 13. Logout ──────────────────────────────" -ForegroundColor Yellow
if ($jwt) {
    Test-Step -Name "Resident logout" -Method POST -Path "/auth/logout/" -Body @"
{"refresh":"$(if ($otp_verify -and $otp_verify.data.refresh) { $otp_verify.data.refresh } else { 'test' })"}
"@
}

# ── 15. Token Refresh ──────────────────────────────────
Write-Host "`n── 14. Token Refresh ───────────────────────" -ForegroundColor Yellow
if ($gov_login -and $gov_login.data.refresh) {
    Test-Step -Name "Refresh token" -Method POST -Path "/auth/refresh/" -Body @"
{"refresh":"$($gov_login.data.refresh)"}
"@
}

# ── Summary ─────────────────────────────────────────────
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Results: $pass passed, $fail failed" -ForegroundColor $(if ($fail -eq 0) { "Green" } else { "Red" })
Write-Host "============================================" -ForegroundColor Cyan
            