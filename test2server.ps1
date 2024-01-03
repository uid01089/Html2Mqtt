$body = @{
    topic = "/home/test"
    value = "example_value"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://koserver.parents:8099/api/store" -Method Post -Headers @{"Content-Type" = "application/json" } -Body $body
