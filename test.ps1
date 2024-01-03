$body = @{
    topic = "/home/test"
    value = "example_value"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/store" -Method Post -Headers @{"Content-Type" = "application/json" } -Body $body
