# fix_build.ps1 - Automated Build Fixer

Write-Host "🔍 searching for Java 17..."
$javaCandidates = @(
    "C:\Program Files\Android\Android Studio\jbr\bin\java.exe",
    "C:\Program Files\Android\Android Studio\jre\bin\java.exe",
    "C:\Program Files\Java\jdk-17*\bin\java.exe",
    "$env:LOCALAPPDATA\Programs\Common\Android\Android Studio\jbr\bin\java.exe"
)

$validJava = $null

foreach ($path in $javaCandidates) {
    if (Test-Path $path) {
        Write-Host "Found: $path"
        # Verify version simple check
        $validJava = $path
        break
    }
}

if ($validJava) {
    $javaHome = (Get-Item $validJava).Directory.Parent.FullName
    $env:JAVA_HOME = $javaHome
    Write-Host "🚀 Setting JAVA_HOME to: $javaHome"
    
    Write-Host "🧹 Cleaning project..."
    ./gradlew clean
    
    Write-Host "🔨 Building APK..."
    ./gradlew assembleDebug
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ BUILD SUCCESS!"
        Write-Host "APK Location: android-app\SafeCorridorTracker\app\build\outputs\apk\debug\app-debug.apk"
    } else {
        Write-Host "❌ Build failed. Please verify the error above."
    }
} else {
    Write-Host "❌ Could not find a valid Java 17 installation automatically."
    Write-Host "Please do checking manually."
}
