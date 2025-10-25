# Setup script for RAGAnything with Ollama
# Run this script to automatically setup and test Ollama integration

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RAGAnything + Ollama - Automated Setup Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Ollama is installed
Write-Host "Step 1: Checking Ollama installation..." -ForegroundColor Yellow
$ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaInstalled) {
    Write-Host "  [OK] Ollama is installed" -ForegroundColor Green
    Write-Host "  Version: " -NoNewline
    ollama --version
}
else {
    Write-Host "  [FAIL] Ollama is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Ollama from: https://ollama.ai" -ForegroundColor Yellow
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 2: Check if Ollama server is running
Write-Host "Step 2: Checking Ollama server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction Stop
    Write-Host "  [OK] Ollama server is running" -ForegroundColor Green
}
catch {
    Write-Host "  [FAIL] Ollama server is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Starting Ollama server..." -ForegroundColor Yellow
    Start-Process "ollama" -ArgumentList "serve" -NoNewWindow
    Start-Sleep -Seconds 3
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction Stop
        Write-Host "  [OK] Ollama server started successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "  [FAIL] Could not start Ollama server" -ForegroundColor Red
        Write-Host "Please start Ollama manually and run this script again." -ForegroundColor Yellow
        exit 1
    }
}
Write-Host ""

# Step 3: Check required models
Write-Host "Step 3: Checking required models..." -ForegroundColor Yellow
$requiredModels = @{
    "mistral:latest" = "LLM Model"
    "llava:latest"   = "Vision Model"
    "bge-m3:latest"  = "Embedding Model"
}

$installedModels = ollama list | Select-Object -Skip 1 | ForEach-Object {
    ($_ -split '\s+')[0]
}

$missingModels = @()
foreach ($model in $requiredModels.Keys) {
    $modelName = $requiredModels[$model]
    if ($installedModels -contains $model) {
        Write-Host "  [OK] $modelName ($model)" -ForegroundColor Green
    }
    else {
        Write-Host "  [MISSING] $modelName ($model)" -ForegroundColor Yellow
        $missingModels += $model
    }
}
Write-Host ""

# Step 4: Install missing models
if ($missingModels.Count -gt 0) {
    Write-Host "Step 4: Installing missing models..." -ForegroundColor Yellow
    foreach ($model in $missingModels) {
        Write-Host "  Installing $model..." -ForegroundColor Cyan
        ollama pull $model
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] $model installed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "  [FAIL] Failed to install $model" -ForegroundColor Red
        }
    }
    Write-Host ""
}
else {
    Write-Host "Step 4: All required models are already installed" -ForegroundColor Green
    Write-Host ""
}

# Step 5: Setup .env file
Write-Host "Step 5: Setting up .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  [INFO] .env file already exists" -ForegroundColor Cyan
    $overwrite = Read-Host "  Do you want to overwrite it? (y/N)"
    if ($overwrite -eq "y" -or $overwrite -eq "Y") {
        Copy-Item ".env.ollama" ".env" -Force
        Write-Host "  [OK] .env file created from template" -ForegroundColor Green
    }
    else {
        Write-Host "  [SKIP] Keeping existing .env file" -ForegroundColor Yellow
    }
}
else {
    Copy-Item ".env.ollama" ".env"
    Write-Host "  [OK] .env file created from template" -ForegroundColor Green
}
Write-Host ""

# Step 6: Test connection
Write-Host "Step 6: Testing Ollama connection..." -ForegroundColor Yellow
Write-Host "  Running test_ollama_connection.py..." -ForegroundColor Cyan
Write-Host ""
python test_ollama_connection.py
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "  [OK] Connection test passed" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "  [FAIL] Connection test failed" -ForegroundColor Red
    Write-Host "  Please check the error messages above" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now use RAGAnything with Ollama:" -ForegroundColor Green
Write-Host ""
Write-Host "  python raganything_example.py `"path\to\your\document.pdf`"" -ForegroundColor White
Write-Host ""
Write-Host "For more information:" -ForegroundColor Yellow
Write-Host "  - Quick start (Vietnamese): QUICKSTART_VI.md" -ForegroundColor White
Write-Host "  - Full documentation (English): README_OLLAMA.md" -ForegroundColor White
Write-Host "  - Changes summary: CHANGES_SUMMARY.md" -ForegroundColor White
Write-Host ""
Write-Host "Happy RAGing! " -NoNewline -ForegroundColor Cyan
Write-Host "🚀" -ForegroundColor Yellow
Write-Host ""
