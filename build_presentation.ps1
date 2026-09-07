$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$out = Join-Path $root 'VeriGuard_AI_SIH2026.pptx'
$shot = Join-Path $root 'results_capture.png'

$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Presentations.Add() | Out-Null
$presentation = $ppt.Presentations.Item(1)
$presentation.PageSetup.SlideSize = 2

$navy = 0x263B55
$blue = 0x2B6CB0
$teal = 0x2C7A7B
$gold = 0xC9972B
$ink = 0x1F2937
$muted = 0x5B6675
$white = 0xFFFFFF
$light = 0xF3F6F8
$green = 0x2E7D32
$red = 0x9B2C2C

function Add-Text($slide, $text, $left, $top, $width, $height, $size, $color, $bold = $false) {
    $box = $slide.Shapes.AddTextbox(1, $left, $top, $width, $height)
    $box.TextFrame.TextRange.Text = $text
    $box.TextFrame.TextRange.Font.Size = $size
    $box.TextFrame.TextRange.Font.Bold = $bold
    $box.TextFrame.WordWrap = -1
    return $box
}

function Add-Header($slide, $kicker, $title, $number) {
    $bar = $slide.Shapes.AddShape(1, 0, 0, 720, 34)
    $bar.Line.Visible = 0
    Add-Text $slide $kicker.ToUpper() 28 8 390 18 10 $white $true | Out-Null
    Add-Text $slide $number 650 8 40 18 10 $white $true | Out-Null
    Add-Text $slide $title 30 52 650 38 25 $navy $true | Out-Null
}

function Add-BulletBlock($slide, $items, $left, $top, $width, $height, $size = 15) {
    $text = ($items | ForEach-Object { [char]0x2022 + ' ' + $_ }) -join "`r`n"
    $box = Add-Text $slide $text $left $top $width $height $size $ink $false
    $box.TextFrame.TextRange.ParagraphFormat.SpaceAfter = 7
    return $box
}

function Add-Footer($slide) {
    Add-Text $slide 'Abstract_Minds  |  SIH2026-T2851  |  VeriGuard AI' 30 520 650 16 9 $muted $false | Out-Null
}

# 1 Title
$presentation.Slides.Add(1, 12) | Out-Null
$slide = $presentation.Slides.Item(1)
$band = $slide.Shapes.AddShape(1, 0, 0, 720, 145)
$band.Line.Visible = 0
Add-Text $slide 'SMART INDIA HACKATHON 2026' 34 30 650 24 15 $white $true | Out-Null
Add-Text $slide 'VeriGuard AI' 34 190 650 62 38 $navy $true | Out-Null
Add-Text $slide 'AI-Based Fake Identity & Document Screening System' 36 258 640 28 17 $teal $true | Out-Null
Add-Text $slide 'Problem Statement ID: SIH26188' 36 330 640 22 14 $ink $false | Out-Null
Add-Text $slide 'Team ID: SIH2026-T2851' 36 362 640 22 14 $ink $false | Out-Null
Add-Text $slide 'Team: Abstract_Minds' 36 394 640 22 14 $ink $false | Out-Null
Add-Text $slide 'Repository: https://github.com/arnaashah06/veriguard-ai' 36 456 640 20 11 $blue $false | Out-Null

# 2 Scope
$presentation.Slides.Add(2, 12) | Out-Null
$slide = $presentation.Slides.Item(2)
Add-Header $slide '01 | Verified Project Scope' 'What the prototype does' '02'
Add-BulletBlock $slide @(
    'Screens identity-document images and an optional selfie.',
    'Supports Aadhaar, PAN, Voter ID / EPIC, Driving Licence, and Passport workflows.',
    'Processes one document or a multi-document submission.',
    'Returns structured findings, risk assessment, explanations, and audit events.',
    'Uses synthetic local demo assets for repeatable demonstrations.'
) 42 125 620 250 17
$callout = $slide.Shapes.AddShape(5, 42, 405, 635, 62)
Add-Text $slide 'Scope note: this is a prototype screening workflow, not an issuing-authority verification service.' 60 424 600 24 13 $teal $true | Out-Null
Add-Footer $slide

# 3 Workflow
$presentation.Slides.Add(3, 12) | Out-Null
$slide = $presentation.Slides.Item(3)
Add-Header $slide '02 | Processing Workflow' 'From upload to evidence dossier' '03'
$steps = @('Upload', 'Quality check', 'OCR + parsing', 'Validation', 'Cross-document', 'Risk + audit')
$x = 42
for ($i = 0; $i -lt $steps.Count; $i++) {
    $card = $slide.Shapes.AddShape(5, $x, 150, 96, 92)
    Add-Text $slide ('0' + ($i + 1)) ($x + 10) 162 30 18 11 $gold $true | Out-Null
    Add-Text $slide $steps[$i] ($x + 10) 190 76 38 12 $ink $true | Out-Null
    if ($i -lt 5) {
        $arrow = $slide.Shapes.AddShape(33, $x + 98, 185, 22, 20)
        $arrow.Line.Visible = 0
    }
    $x += 110
}
Add-BulletBlock $slide @(
    'The frontend sends multipart document and selfie data to /verify or /verify-multiple.',
    'The backend validates file type, size, and image readability before analysis.',
    'The response is rendered in the ResultsPage dossier with evidence panels and officer actions.'
) 50 300 610 150 16
Add-Footer $slide

# 4 Implementation
$presentation.Slides.Add(4, 12) | Out-Null
$slide = $presentation.Slides.Item(4)
Add-Header $slide '03 | Implementation' 'Engineering components' '04'
$left = @(
    'Frontend: React + Vite',
    'Backend: FastAPI + Uvicorn',
    'OCR: Tesseract with preprocessing and multiple page-segmentation paths',
    'Validation: Verhoeff, PAN, EPIC, RTO, and MRZ-oriented checks'
)
$right = @(
    'Biometrics: face detection, quality checks, and encoding comparison',
    'Forensics: Error Level Analysis signal',
    'Reconciliation: normalized names, dates, and document attributes',
    'Explainability: identity story and four-domain risk decomposition'
)
Add-BulletBlock $slide $left 42 130 300 250 14
Add-BulletBlock $slide $right 370 130 305 250 14
$line = $slide.Shapes.AddShape(1, 352, 122, 2, 275)
$line.Line.Visible = 0
Add-Footer $slide

# 5 Validation
$presentation.Slides.Add(5, 12) | Out-Null
$slide = $presentation.Slides.Item(5)
Add-Header $slide '04 | Validation Logic' 'What is checked' '05'
$rows = @(
    @('Aadhaar', 'Length and Verhoeff checksum path'),
    @('PAN', 'Structure, entity character, surname initial'),
    @('Voter ID', 'EPIC-style format checks'),
    @('Driving Licence', 'State-code and expiry checks'),
    @('Passport', 'MRZ structure and weighted check digits'),
    @('Images', 'Blur, brightness, exposure, and tamper signals')
)
$y = 125
foreach ($row in $rows) {
    $stripe = $slide.Shapes.AddShape(1, 42, $y, 635, 42)
    $stripe.Line.Visible = 0
    Add-Text $slide $row[0] 58 ($y + 11) 130 18 13 $navy $true | Out-Null
    Add-Text $slide $row[1] 200 ($y + 11) 440 18 13 $ink $false | Out-Null
    $y += 48
}
Add-Footer $slide

# 6 Testing
$presentation.Slides.Add(6, 12) | Out-Null
$slide = $presentation.Slides.Item(6)
Add-Header $slide '05 | Test Evidence' 'Repository test coverage' '06'
Add-BulletBlock $slide @(
    'The repository contains suites for document rules, cross-document comparison, advanced features, edge cases, face checks, forensics, and end-to-end flows.',
    'The walkthrough records 18 real-versus-fake scenarios and additional focused suites.',
    'The walkthrough also records frontend lint and production-build checks.',
    'These figures are repository-documented results and should be rerun before final submission.'
) 42 125 630 225 16
$warn = $slide.Shapes.AddShape(5, 42, 390, 635, 70)
Add-Text $slide 'Evidence standard: report dated command output for the final submission.' 62 414 590 22 14 $ink $true | Out-Null
Add-Footer $slide

# 7 UI Evidence
$presentation.Slides.Add(7, 12) | Out-Null
$slide = $presentation.Slides.Item(7)
Add-Header $slide '06 | Live Prototype Evidence' 'Results dossier from local demo flow' '07'
if (Test-Path $shot) {
    $slide.Shapes.AddPicture($shot, 0, -1, 42, 112, 636, 356) | Out-Null
} else {
    Add-Text $slide 'Live results screenshot not available.' 42 160 600 40 18 $red $true | Out-Null
}
Add-Text $slide 'Captured from the local clean multi-document demonstration flow.' 42 480 630 20 12 $muted $false | Out-Null
Add-Footer $slide

# 8 Limitations
$presentation.Slides.Add(8, 12) | Out-Null
$slide = $presentation.Slides.Item(8)
Add-Header $slide '07 | Responsible Use' 'Limitations and next validation steps' '08'
Add-BulletBlock $slide @(
    'OCR and face results vary with image quality, lighting, layout, and model availability.',
    'ELA is a suspicious-signal tool and does not prove fraud by itself.',
    'Synthetic demo assets do not establish real-world accuracy.',
    'Production use requires independent security, privacy, access-control, and regulatory review.',
    'External statistics, costs, legal conclusions, and regulatory approvals are intentionally omitted.'
) 42 125 630 250 16
$close = $slide.Shapes.AddShape(5, 42, 405, 635, 58)
Add-Text $slide 'Next step: rerun the complete test set and attach only approved evidence.' 60 423 600 22 14 $green $true | Out-Null
Add-Footer $slide

$presentation.SaveAs($out)
$presentation.Close()
$ppt.Quit()
Write-Output "Created: $out"
