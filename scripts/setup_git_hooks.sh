#!/usr/bin/env bash
# ==============================================================================
# Setup Git Pre-Commit Hook for PecasBot
# Prevents broken code, unformatted files or failing tests from being committed.
# ==============================================================================

HOOK_PATH=".git/hooks/pre-commit"

cat << 'HOOK' > "$HOOK_PATH"
#!/usr/bin/env bash
echo "Iniciando Quality Gate de Pre-Commit..."
./scripts/quality_gate.sh
if [ $? -ne 0 ]; then
    echo "Commit abortado devido a falhas no Quality Gate!"
    exit 1
fi
HOOK

chmod +x "$HOOK_PATH"
echo "Git pre-commit hook instalado com sucesso em $HOOK_PATH"
