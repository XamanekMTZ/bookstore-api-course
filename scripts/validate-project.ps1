# BookStore API - Project Validation Script (PowerShell)
# This script validates that the project is properly organized for GitHub publication

Write-Host "🔍 BookStore API - Project Validation" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue

# Initialize counters
$passed = 0
$failed = 0

function Test-ProjectFile {
    param([string]$FilePath)
    if (Test-Path $FilePath) {
        Write-Host "✅ $FilePath" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $FilePath (missing)" -ForegroundColor Red
        return $false
    }
}

function Test-ProjectDirectory {
    param([string]$DirPath)
    if (Test-Path $DirPath -PathType Container) {
        Write-Host "✅ $DirPath/" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $DirPath/ (missing)" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n📁 Core Project Structure" -ForegroundColor Blue
Write-Host "=========================" -ForegroundColor Blue

# Essential files
$files = @(
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "requirements.txt",
    "pyproject.toml",
    ".gitignore",
    ".env.example"
)

foreach ($file in $files) {
    if (Test-ProjectFile $file) {
        $passed++
    } else {
        $failed++
    }
}

Write-Host "`n📁 Directory Structure" -ForegroundColor Blue
Write-Host "======================" -ForegroundColor Blue

# Essential directories
$directories = @(
    "bookstore",
    "tests",
    "docs",
    "examples",
    "scripts",
    "k8s",
    "grafana",
    ".github",
    ".github/workflows"
)

foreach ($dir in $directories) {
    if (Test-ProjectDirectory $dir) {
        $passed++
    } else {
        $failed++
    }
}

Write-Host "`n🐍 Python Package Structure" -ForegroundColor Blue
Write-Host "============================" -ForegroundColor Blue

# Python package files
$pythonFiles = @(
    "bookstore/__init__.py",
    "bookstore/main.py",
    "bookstore/models.py",
    "bookstore/schemas.py",
    "bookstore/auth.py",
    "bookstore/database.py",
    "bookstore/config.py",
    "bookstore/logging_config.py",
    "bookstore/middleware.py",
    "run_bookstore.py"
)

foreach ($file in $pythonFiles) {
    if (Test-ProjectFile $file) {
        $passed++
    } else {
        $failed++
    }
}

Write-Host "`n🧪 Testing Framework" -ForegroundColor Blue
Write-Host "====================" -ForegroundColor Blue

# Test files
$testFiles = @(
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/test_unit_basic.py",
    "tests/test_api_integration.py",
    "tests/test_property_based.py",
    "tests/test_performance.py",
    "tests/factories.py",
    "tests/locustfile.py",
    "pytest.ini"
)

foreach ($file in $testFiles) {
    if (Test-ProjectFile $file) {
        $passed++
    } else {
        $failed++
    }
}

Write-Host "`n🚀 CI/CD Pipeline" -ForegroundColor Blue
Write-Host "==================" -ForegroundColor Blue

# CI/CD files
$cicdFiles = @(
    ".github/workflows/ci.yml",
    ".github/workflows/dependencies.yml",
    ".github/workflows/performance.yml",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/pull_request_template.md"
)

foreach ($file in $cicdFiles) {
    if (Test-ProjectFile $file) {
        $passed++
    } else {
        $failed++
    }
}

Write-Host "`n☸️ Kubernetes Deployment" -ForegroundColor Blue
Write-Host "=========================" -ForegroundColor Blue

# Kubernetes files
$k8sFiles = @(
    "k8s/namespace.yaml",
    "k8s/configmap.yaml",
    "k8s/secrets.yaml",
    "k8s/postgresql.yaml",
    "k8s/redis.yaml",
    "k8s/api-deployment.yaml",
    "k8s/ingress.yaml",
    "k8s/monitoring.yaml",
    "k8s/deploy.sh"
)

foreach ($file in $k8sFiles) {
    if (Test-ProjectFile $file) {
        $passed++
    } else {
        $failed++
    }
}

Write-Host "`n📚 Documentation" -ForegroundColor Blue
Write-Host "=================" -ForegroundColor Blue

# Documentation files
$docFiles = @(
    "docs/PROJECT_STRUCTURE.md",
    "docs/PRODUCTION_DEPLOYMENT.md",
    "docs/DOCKER_SETUP.md",
    "docs/CI_CD_SETUP.md",
    "docs/TESTING_SUMMARY.md",
    "docs/GITHUB_SETUP.md"
)

foreach ($file in $docFiles) {
    if (Test-ProjectFile $file) {
        $passed++
    } else {
        $failed++
    }
}

Write-Host "`n📊 Monitoring and Configuration" -ForegroundColor Blue
Write-Host "==============================" -ForegroundColor Blue

# Configuration files
$configFiles = @(
    "prometheus.yml",
    "loki.yml",
    "promtail.yml",
    "redis.conf",
    "nginx.conf",
    "nginx-prod.conf",
    "grafana/dashboards/bookstore-api.json"
)

foreach ($file in $configFiles) {
    if (Test-ProjectFile $file) {
        $passed++
    } else {
        $failed++
    }
}

Write-Host "`n🔍 Environment Checks" -ForegroundColor Blue
Write-Host "=====================" -ForegroundColor Blue

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ Python available: $pythonVersion" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌ Python not available" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "❌ Python not available" -ForegroundColor Red
    $failed++
}

# Check if Docker is available
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "✅ Docker available: $dockerVersion" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "⚠️ Docker not available" -ForegroundColor Yellow
        $failed++
    }
} catch {
    Write-Host "⚠️ Docker not available" -ForegroundColor Yellow
    $failed++
}

Write-Host "`n📋 Validation Summary" -ForegroundColor Blue
Write-Host "=====================" -ForegroundColor Blue

$total = $passed + $failed
$percentage = [math]::Round(($passed * 100) / $total, 1)

Write-Host "Total checks: $total" -ForegroundColor Blue
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host "Success rate: $percentage%" -ForegroundColor Green

if ($failed -eq 0) {
    Write-Host "`n🎉 PROJECT VALIDATION SUCCESSFUL!" -ForegroundColor Green
    Write-Host "✅ Your BookStore API project is ready for GitHub publication!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Create a new GitHub repository"
    Write-Host "2. Push your code: git push origin main"
    Write-Host "3. Configure GitHub secrets for CI/CD"
    Write-Host "4. Deploy to your preferred environment"
    Write-Host ""
    Write-Host "📚 See docs/GITHUB_SETUP.md for detailed instructions"
    exit 0
} elseif ($failed -le 3) {
    Write-Host "`n⚠️ PROJECT VALIDATION MOSTLY SUCCESSFUL" -ForegroundColor Yellow
    Write-Host "Minor issues found, but project is ready for GitHub" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📚 See docs/GITHUB_SETUP.md for setup instructions"
    exit 0
} else {
    Write-Host "`n❌ PROJECT VALIDATION FAILED" -ForegroundColor Red
    Write-Host "Please fix the missing files/directories before publishing" -ForegroundColor Red
    exit 1
}