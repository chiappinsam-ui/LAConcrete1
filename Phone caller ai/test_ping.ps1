$body = @{
    secret = "1234"
    command = "Update the loader: put 'welcome to' in cursive on top, 'L.A CONCRETE''S' in a thick font in the middle, and 'services' underneath. Make 'welcome to' and 'services' the same size with a softer font. The text starts white, then 'concrete''s' turns orange with an orange glow like a lightbulb. Keep it on screen for 2-3 seconds."
    action = "git_push"
} | ConvertTo-Json

$headers = @{
    "ngrok-skip-browser-warning" = "true"
    "Content-Type" = "application/json"
}

# UPDATE THIS LINK WHENEVER YOU RESTART NGROK
$url = "https://odette-otoscopic-stifledly.ngrok-free.dev/execute"

Invoke-RestMethod -Uri $url -Method Post -Body $body -Headers $headers
Write-Host "Command fired into the tunnel!" -ForegroundColor Green