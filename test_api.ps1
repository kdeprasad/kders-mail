$regBody = '{"email":"test+ai-6@example.com","password":"password","full_name":"AI Test","is_teacher":false}'
$loginBody = '{"email":"test+ai-6@example.com","password":"password"}'
$composeBody = '{"recipient":"test+ai-6@example.com","subject":"RAG test","body":"Vector retrieval test message about eigenvalues and matrices."}'
$aiBody = '{"query":"eigenvalues matrices","group_id":0,"since_days":7}'

Write-Output "REGISTER:"
$reg = Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/auth/register' -Body $regBody -ContentType 'application/json'
$reg | ConvertTo-Json | Write-Output

Write-Output "LOGIN:"
$login = Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/auth/login' -Body $loginBody -ContentType 'application/json'
$login | ConvertTo-Json | Write-Output

$token = $login.access_token
$hdr = @{ Authorization = "Bearer $token" }

Write-Output "COMPOSE:"
$compose = Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/mail/compose' -Headers $hdr -Body $composeBody -ContentType 'application/json'
$compose | ConvertTo-Json | Write-Output

Write-Output "AI:"
$ai = Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/ai/query' -Headers $hdr -Body $aiBody -ContentType 'application/json'
$ai | ConvertTo-Json | Write-Output
