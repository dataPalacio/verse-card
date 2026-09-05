<#
.SYNOPSIS
    Entrada unica de execucao do verse-card-v5.

.DESCRIPTION
    Resolve o interpretador Python correto (NUNCA python3 — nesta maquina e o
    stub da Microsoft Store), garante que os caminhos sejam relativos ao
    projeto e nao ao diretorio atual, e encadeia validacao, sincronizacao e
    render na ordem certa.

.EXAMPLE
    .\executar.ps1 -Acao preparar
    .\executar.ps1 -Acao render -Conteudo conteudos/publicados/001-confiar-na-espera/conteudo.json
    .\executar.ps1 -Acao verificar
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('preparar', 'validar', 'render', 'testar', 'sincronizar', 'verificar')]
    [string]$Acao,

    [string]$Conteudo,

    # Sobrescreve a pasta de saida. Por padrao ela vem do run_id do conteudo.
    [string]$Saida
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

function Get-Python {
    # Ordem deliberada: 'py -3' e o launcher oficial no Windows; 'python3' e
    # o stub da Store e nunca deve ser usado aqui.
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $v = & py -3 -c "import sys;print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $v) { return @{ Exe = 'py'; Args = @('-3'); Versao = $v } }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $v = & python -c "import sys;print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $v) { return @{ Exe = 'python'; Args = @(); Versao = $v } }
    }
    throw "Python 3.10+ nao encontrado. Instale o Python e tente de novo (nao use o atalho 'python3' da Microsoft Store)."
}

$py = Get-Python
if ([version]$py.Versao -lt [version]'3.10') {
    throw "Python $($py.Versao) e antigo demais. Este projeto precisa de 3.10 ou superior."
}

function Invoke-Py {
    # Chama o Python e propaga o codigo de saida — sem isso um render que
    # falha ainda terminaria o script com sucesso.
    param([string[]]$Argumentos, [string]$Etapa)
    & $py.Exe @($py.Args + $Argumentos)
    if ($LASTEXITCODE -ne 0) {
        throw "$Etapa falhou (codigo $LASTEXITCODE)."
    }
}

function Resolve-Conteudo {
    if (-not $Conteudo) {
        throw "Informe o conteudo: .\executar.ps1 -Acao $Acao -Conteudo conteudos/publicados/<numero-tema>/conteudo.json"
    }
    if (-not (Test-Path $Conteudo)) {
        throw "Conteudo nao encontrado: $Conteudo"
    }
    return $Conteudo
}

switch ($Acao) {

    'preparar' {
        Write-Host "Python $($py.Versao) via '$($py.Exe) $($py.Args)'"
        Invoke-Py @('-m', 'pip', 'install', '-r', 'sistema/requirements.txt') 'Instalacao das dependencias'
        Invoke-Py @('-m', 'playwright', 'install', 'chromium') 'Download do Chromium'
        Write-Host "`nAmbiente pronto."
    }

    'validar' {
        $c = Resolve-Conteudo
        Invoke-Py @('-m', 'sistema.pipeline.validar', $c) 'Validacao'
    }

    'sincronizar' {
        Invoke-Py @('-m', 'sistema.pipeline.sincroniza_template') 'Sincronizacao'
    }

    'testar' {
        Invoke-Py @('-m', 'pytest', 'sistema/testes', '-q') 'Testes'
    }

    'verificar' {
        # Portao rapido: nao abre browser, nao gera arte.
        Invoke-Py @('-m', 'pytest', 'sistema/testes', '-q') 'Testes'
        Invoke-Py @('-m', 'sistema.pipeline.sincroniza_template', '--conferir') 'Conferencia de sincronia'
        Write-Host "`nVerificacao concluida com sucesso."
    }

    'render' {
        $c = Resolve-Conteudo
        # Ordem obrigatoria: validar e conferir template ANTES de gerar arte.
        Invoke-Py @('-m', 'sistema.pipeline.validar', $c) 'Validacao'
        Invoke-Py @('-m', 'sistema.pipeline.sincroniza_template', '--conferir') 'Conferencia de sincronia'
        $args = @('-m', 'sistema.pipeline.render', $c)
        if ($Saida) { $args += @('--saida', $Saida) }
        Invoke-Py $args 'Render'
    }
}
