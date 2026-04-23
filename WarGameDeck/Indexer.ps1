$assetsPath = "Assets"
$outputPath = "Assets/Other/js/pages.js"
$updatesPath = "Assets/Other/Update/OldUpdate"
$updatesJsPath = "Assets/Other/js/updates.js"
$pointDocPath = "Assets/Other/docs/Point.md"
$whatsnewDocPath = "Assets/Other/Update/LastUpdate/whatsnew.md"

# Robust HTML Entity for arrow
$arrowEntity = "&#8592;"
$e_acc = [char]0xE9

# Mapping des noms vers adjectifs et noms propres propres
$countryMap = @{
    "france" = "France"; "chine" = "Chine"; "japon" = "Japon"; "japan" = "Japon";
    "afrique_du_sud" = "Afrique du Sud"; "south africa" = "Afrique du Sud";
    "south korea" = "Cor${e_acc}e du Sud"; "cor" = "Cor${e_acc}e du Sud";
    "allemagne" = "Allemagne"; "germany" = "Allemagne";
    "italie" = "Italie"; "italy" = "Italie";
    "usa" = "USA"; "etats-unis" = "USA";
    "bresil" = "Br${e_acc}sil"; "brazil" = "Br${e_acc}sil";
    "ranked_basique" = "G${e_acc}n${e_acc}rique"; "basique" = "G${e_acc}n${e_acc}rique"
}

$adjMap = @{
    "france" = "fran${e_acc}aises"; "chine" = "chinoises"; "japon" = "japonaises"; 
    "afrique_du_sud" = "sud-africaines"; "south korea" = "sud-cor${e_acc}ennes";
    "allemagne" = "allemandes"; "italie" = "italiennes"; "usa" = "am${e_acc}ricaines";
    "bresil" = "br${e_acc}siliennes"; "brazil" = "br${e_acc}siliennes";
    "ranked_basique" = "g${e_acc}n${e_acc}riques"; "basique" = "g${e_acc}n${e_acc}riques"
}

[console]::InputEncoding = [console]::OutputEncoding = [System.Text.Encoding]::UTF8
$flagMap = @{
    "france" = "fr"; "allemagne" = "de"; "germany" = "de"; "italie" = "it"; "italy" = "it"; "espagne" = "es"; "spain" = "es"; 
    "royaume-uni" = "gb"; "uk" = "gb"; "belgique" = "be"; "suisse" = "ch"; "swiss" = "ch";
    "pologne" = "pl"; "suede" = "se"; "sweden" = "se"; "norvege" = "no"; "norway" = "no"; "finlande" = "fi";
    "danemark" = "dk"; "ukraine" = "ua"; "russie" = "ru"; "russia" = "ru"; "pays-bas" = "nl"; "netherlands" = "nl";
    "japon" = "jp"; "japan" = "jp"; "chine" = "cn"; "china" = "cn"; "cor" = "kr"; "korea" = "kr"; "vietnam" = "vn";
    "inde" = "in"; "india" = "in"; "israel" = "il"; "turquie" = "tr"; "taiwan" = "tw";
    "thailande" = "th"; "pakistan" = "pk"; "irak" = "iq"; "iran" = "ir"; "north korea" = "kp";
    "usa" = "us"; "etats-unis" = "us"; "america" = "us"; "canada" = "ca"; "bresil" = "br"; "brazil" = "br";
    "mexique" = "mx"; "mexico" = "mx"; "argentine" = "ar"; "chili" = "cl"; "colombie" = "co";
    "afrique" = "za"; "south africa" = "za"; "egypte" = "eg"; "maroc" = "ma"; "algerie" = "dz";
    "australie" = "au"; "australia" = "au"; "nouvelle-zelande" = "nz"; "tunisie" = "tn";
    "basique" = "un"; "ranked" = "un"; "world" = "un";
}

$pages = Get-ChildItem -Path $assetsPath -Filter *.html | Where-Object { $_.FullName -notmatch "Assets\\Other" }
$enc = New-Object System.Text.UTF8Encoding $true

$pData = $pages | ForEach-Object {
    $fileInfo = $_
    $content = [System.IO.File]::ReadAllText($fileInfo.FullName, [System.Text.Encoding]::UTF8)
    $filenameLower = $fileInfo.Name.ToLower()
    
    $code = "un"
    foreach ($key in ($flagMap.Keys | Sort-Object Length -Descending)) {
        if ($filenameLower.Contains($key)) { $code = $flagMap[$key]; break }
    }

    $modified = $false

    # Fix Encoding
    if ($content -match "Ã©" -or $content -match "unitA©") {
        $content = $content -replace "Ã©", $e_acc
        $content = $content -replace "unitA©", "unit${e_acc}"
        $modified = $true
    }

    # Fix relative paths to CSS in HTML files
    if ($content -match "Other/deck_style.css" -and $content -notmatch "Other/css/deck_style.css") {
        $content = $content -replace "Other/deck_style.css", "Other/css/deck_style.css"
        $modified = $true
    }

    # Determine Country and Adjective based ON FILENAME
    $currentCountry = $fileInfo.BaseName -replace "_", " "
    $currentAdj = "de $currentCountry"
    
    foreach ($key in ($countryMap.Keys | Sort-Object Length -Descending)) {
        if ($filenameLower.Contains($key)) { $currentCountry = $countryMap[$key]; break }
    }
    foreach ($key in ($adjMap.Keys | Sort-Object Length -Descending)) {
        if ($filenameLower.Contains($key)) { $currentAdj = $adjMap[$key]; break }
    }

    $headerHtml = @"
        <header>
            <div class="header-title">
                <img src="Other/img/Logo_Ranked.png" alt="Logo">
                <h1>Deck : $currentCountry</h1>
            </div>
            <a href="../index.html" class="back-btn">$arrowEntity Retour au Portail</a>
        </header>

        <div style="max-width: 1000px; margin: auto; padding: 20px 3px 0 3px">
            <p style="color: var(--text-muted); text-align: center;">Liste des unit${e_acc}s $currentAdj du Wargame Ranked</p>
        </div>
"@

    # FORCE TITLE SYNC
    if ($content -match "<title>(.*?)</title>") {
        if ($matches[1] -ne $currentCountry) {
            Write-Host "Updating title for: $($fileInfo.Name) -> $currentCountry" -ForegroundColor Cyan
            $content = $content -replace "<title>.*?</title>", "<title>$currentCountry</title>"
            $modified = $true
        }
    }

    # FORCE HEADER UPDATE (Aggressive check with newline support)
    if ($content -match "(?s)<header>.*?</header>") {
        if ($content -notmatch "<h1>Deck : $currentCountry</h1>") {
            Write-Host "Updating mismatched header in: $($fileInfo.Name) -> $currentCountry" -ForegroundColor Magenta
            # Match the header and the following div (intro paragraph)
            $content = $content -replace '(?s)<header>.*?</header>\s*(<div style="max-width: 1000px; margin: auto; padding: 20px 3px 0 3px">.*?</div>)?', $headerHtml
            $modified = $true
        }
    }
    elseif ($content -notmatch "<header>") {
        Write-Host "Patching missing theme for: $($fileInfo.Name)" -ForegroundColor Yellow
        $newHeadLinks = "        <link rel=`"stylesheet`" href=`"Other/css/deck_style.css`">`n        <link href=`"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap`" rel=`"stylesheet`">"
        if ($content -match "</head>") { $content = $content -replace "</head>", ($newHeadLinks + "`n    </head>") }
        $content = $content -replace '<h1[^>]*>.*?</h1>', ''
        if ($content -match '<div style="max-width: 1000px; margin: auto; padding: 0 3px 0 3px"><p>.*?</p>\s*</div>') {
            $content = $content -replace '<div style="max-width: 1000px; margin: auto; padding: 0 3px 0 3px"><p>.*?</p>\s*</div>', $headerHtml
        }
        else {
            $content = $content -replace "<body>", "<body>`n$headerHtml"
        }
        $modified = $true
    }

    # Ensure Logo path is correct
    if ($content -match "Other/Logo_Ranked.png") {
        $content = $content -replace "Other/Logo_Ranked.png", "Other/img/Logo_Ranked.png"
        $modified = $true
    }

    if ($modified) { [System.IO.File]::WriteAllText($fileInfo.FullName, $content, $enc) }
    [PSCustomObject]@{ filename = $fileInfo.Name; flag = $code }
}

function Get-EscapedContent($path) {
    if (Test-Path $path) {
        return [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
    }
    return ""
}

$jsonPages = $pData | ConvertTo-Json -Compress
$jsonPoints = Get-EscapedContent $pointDocPath | ConvertTo-Json -Compress
$jsonWhatsnew = Get-EscapedContent $whatsnewDocPath | ConvertTo-Json -Compress

$jsContent = "window.PAGES_DATA = $jsonPages;
window.POINTS_CONTENT = $jsonPoints;
window.WHATSNEW_CONTENT = $jsonWhatsnew;"

$oldUpdatesMap = @{}
if (Test-Path $updatesPath) {
    $oldFiles = Get-ChildItem -Path $updatesPath -Filter *.md | Sort-Object LastWriteTime -Descending
    foreach ($f in $oldFiles) {
        $oldUpdatesMap[$f.Name] = Get-EscapedContent $f.FullName
    }
}
$jsonOldUpdates = $oldUpdatesMap | ConvertTo-Json -Compress
$jsContent += "`nwindow.OLD_UPDATES_DATA = $jsonOldUpdates;"

[System.IO.File]::WriteAllText($outputPath, $jsContent, [System.Text.Encoding]::UTF8)

Write-Host "Indexation terminee. $( ($pData | Measure-Object).Count ) pages trouvees." -ForegroundColor Cyan

# Update Deck Builder Data
Write-Host "Mise à jour des données du Deck Builder..." -ForegroundColor Yellow
node "Assets/scripts/js/extract_vehicles.js"
