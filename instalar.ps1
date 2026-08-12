# =============================================================================
#  Trayectorias Informática — Instalador
#  Colegio de Bachilleres · Curso de Marketing Digital
#
#  Uso:
#    irm https://raw.githubusercontent.com/gabrielmondragontorres-rgb/trayectorias-informatica/main/instalar.ps1 | iex
#
#  Qué hace:
#    1. Comprueba los programas necesarios
#    2. Instala el comando "trayectorias" en tu perfil de PowerShell
#    3. Deja todo listo para crear proyectos del curso
# =============================================================================

$ErrorActionPreference = "Stop"

$REPO  = "gabrielmondragontorres-rgb/trayectorias-informatica"
$INICIO = "# >>> Trayectorias Informatica >>>"
$FIN    = "# <<< Trayectorias Informatica <<<"

function Escribir($texto, $color = "White") { Write-Host $texto -ForegroundColor $color }

Escribir ""
Escribir "  ==========================================" "Cyan"
Escribir "   Trayectorias Informatica" "Cyan"
Escribir "   Curso de Marketing Digital" "Cyan"
Escribir "  ==========================================" "Cyan"
Escribir ""

# --- 1. Requisitos previos ---------------------------------------------------
Escribir "  Revisando lo que necesitas..." "Yellow"
Escribir ""

$faltantes = @()

function Revisar($nombre, $comando, $ayuda) {
    $existe = Get-Command $comando -ErrorAction SilentlyContinue
    if ($existe) {
        $version = ""
        try { $version = (& $comando --version 2>$null | Select-Object -First 1) } catch {}
        Escribir "    [OK]    $nombre $version" "Green"
        return $true
    } else {
        Escribir "    [FALTA] $nombre" "Red"
        Escribir "            $ayuda" "DarkGray"
        return $false
    }
}

if (-not (Revisar "Node.js" "node" "Descargalo en https://nodejs.org (version 20 o superior)")) { $faltantes += "Node.js" }
if (-not (Revisar "Claude Code" "claude" "Instalalo con: npm install -g @anthropic-ai/claude-code")) { $faltantes += "Claude Code" }
if (-not (Revisar "Git" "git" "Opcional. Descargalo en https://git-scm.com")) { }

Escribir ""

# --- 2. Instalar el comando en el perfil -------------------------------------
$perfil = $PROFILE.CurrentUserAllHosts
$carpeta = Split-Path $perfil -Parent
if (-not (Test-Path $carpeta)) { New-Item -ItemType Directory -Path $carpeta -Force | Out-Null }
if (-not (Test-Path $perfil))  { New-Item -ItemType File -Path $perfil -Force | Out-Null }

$bloque = @"
$INICIO
function trayectorias {
    param([switch]`$Forzar)

    `$repo = "$REPO"
    `$destino = (Get-Location).Path

    # Avisar si la carpeta ya tiene contenido
    `$contenido = Get-ChildItem -Path `$destino -Force | Where-Object { `$_.Name -notin @('.','..') }
    if (`$contenido -and -not `$Forzar) {
        Write-Host ""
        Write-Host "  Esta carpeta no esta vacia:" -ForegroundColor Yellow
        Write-Host "  `$destino" -ForegroundColor DarkGray
        Write-Host ""
        `$r = Read-Host "  Los archivos con el mismo nombre se reemplazaran. Continuar? (s/n)"
        if (`$r -ne 's' -and `$r -ne 'S') { Write-Host "  Cancelado." -ForegroundColor DarkGray; return }
    }

    Write-Host ""
    Write-Host "  Descargando la plantilla del curso..." -ForegroundColor Cyan

    `$tmp = Join-Path `$env:TEMP ("trayectorias-" + [guid]::NewGuid().ToString("N").Substring(0,8))
    `$zip = "`$tmp.zip"
    try {
        `$url = "https://github.com/`$repo/archive/refs/heads/main.zip"
        `$anterior = `$ProgressPreference; `$ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri `$url -OutFile `$zip -UseBasicParsing
        `$ProgressPreference = `$anterior

        Expand-Archive -Path `$zip -DestinationPath `$tmp -Force
        `$origen = Join-Path `$tmp ((Split-Path `$repo -Leaf) + "-main\plantilla")
        if (-not (Test-Path `$origen)) { throw "La plantilla no venia en el paquete descargado." }

        Get-ChildItem -Path `$origen -Force | Copy-Item -Destination `$destino -Recurse -Force

        Write-Host ""
        Write-Host "  Listo. Proyecto creado en:" -ForegroundColor Green
        Write-Host "  `$destino" -ForegroundColor White
        Write-Host ""
        Write-Host "  Siguientes pasos:" -ForegroundColor Cyan
        Write-Host "    1. npm install                 (instalar, solo la primera vez)"
        Write-Host "    2. copy .env.local.example .env.local"
        Write-Host "    3. claude                      (abrir tu asistente)"
        Write-Host ""
        Write-Host "  Cuando abra Claude, escribe: /primer" -ForegroundColor Yellow
        Write-Host ""
    }
    catch {
        Write-Host ""
        Write-Host "  No se pudo descargar la plantilla." -ForegroundColor Red
        Write-Host "  `$(`$_.Exception.Message)" -ForegroundColor DarkGray
        Write-Host "  Revisa tu conexion a internet e intenta de nuevo." -ForegroundColor DarkGray
        Write-Host ""
    }
    finally {
        if (Test-Path `$zip) { Remove-Item `$zip -Force -ErrorAction SilentlyContinue }
        if (Test-Path `$tmp) { Remove-Item `$tmp -Recurse -Force -ErrorAction SilentlyContinue }
    }
}

# Nombres alternativos del mismo comando
function trayectorias-informatica { trayectorias @args }
function Trayectorias-informática { trayectorias @args }
Set-Alias -Name ti -Value trayectorias -Scope Global -ErrorAction SilentlyContinue
$FIN
"@

# Quitar instalacion previa y volver a escribir (idempotente)
$actual = Get-Content $perfil -Raw -ErrorAction SilentlyContinue
if ($null -eq $actual) { $actual = "" }
$patron = [regex]::Escape($INICIO) + "[\s\S]*?" + [regex]::Escape($FIN)
$limpio = [regex]::Replace($actual, $patron, "").TrimEnd()
$yaEstaba = $actual -match [regex]::Escape($INICIO)

$final = if ($limpio) { "$limpio`r`n`r`n$bloque`r`n" } else { "$bloque`r`n" }
$final | Out-File -FilePath $perfil -Encoding utf8 -Force

if ($yaEstaba) { Escribir "  Comando actualizado en tu perfil." "Green" }
else           { Escribir "  Comando instalado en tu perfil." "Green" }
Escribir "  $perfil" "DarkGray"
Escribir ""

# --- 3. Cierre ---------------------------------------------------------------
if ($faltantes.Count -gt 0) {
    Escribir "  ATENCION: falta instalar $($faltantes -join ' y ')." "Yellow"
    Escribir "  El comando ya quedo listo, pero necesitaras eso antes de empezar." "Yellow"
    Escribir ""
}

Escribir "  Para empezar, abre una terminal NUEVA y escribe:" "Cyan"
Escribir ""
Escribir "      mkdir mi-proyecto" "White"
Escribir "      cd mi-proyecto" "White"
Escribir "      trayectorias" "White"
Escribir ""
Escribir "  (tambien funciona como: trayectorias-informatica  o  ti)" "DarkGray"
Escribir ""
