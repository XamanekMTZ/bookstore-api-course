# Simple Project Validation Script
Write-Host "Project Validation" -ForegroundColor Blue
Write-Host "==================" -ForegroundColor Blue

$passed = 0
$failed = 0

# Check essential files
$essentialFiles = @(
    "README.md",
    "LICENSE", 
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "bookstore/main.py",
    "tests/conftest.py"
)

Write-Host "`nChecking Essential Files:" -ForegroundColor Blue
foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Host "OK $file" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "MISSING $file" -ForegroundColor Red
        $failed++
    }
}

# Check directories
$essentialDirs = @(
    "bookstore",
    "tests", 
    "docs",
    "k8s",
    ".github"
)

Write-Host "`nChecking Essential Directories:" -ForegroundColor Blue
foreach ($dir in $essentialDirs) {
    if (Test-Path $dir -PathType Container) {
        Write-Host "OK $dir/" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "MISSING $dir/" -ForegroundColor Red
        $failed++
    }
}

$total = $passed + $failed
$percentage = [math]::Round(($passed * 100) / $total, 1)

Write-Host "`nSummary:" -ForegroundColor Blue
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host "Success: $percentage%" -ForegroundColor Green

if ($failed -eq 0) {
    Write-Host "`nPROJECT READY FOR GITHUB!" -ForegroundColor Green
} else {
    Write-Host "`nSome files missing, but mostly ready" -ForegroundColor Yellow
}

Write-Host "`nNext: See docs/GITHUB_SETUP.md for publishing guide" -ForegroundColor Blue