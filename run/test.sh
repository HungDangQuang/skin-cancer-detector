#!/usr/bin/env bash
# ============================================================================
# Run the unit tests inside the SERVER venv (./.venv-linux). CPU-only.
#
# The Mac has no torch/timm and must not run Python (CLAUDE.md "Local
# environment != runtime environment"), so tests/ only ever run here.
# No coverage plugin: pytest-cov is not in .venv-linux (`make test` needs it).
#
# Usage:
#   bash run/test.sh                                              # all of tests/
#   bash run/test.sh TESTS="tests/test_sampler.py tests/test_callbacks.py"
#
# Args (KEY=VALUE):
#   TESTS   space-separated test files / node ids   (default tests/)
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "test"
activate_venv
# Tests are CPU-only; keep them off a card a training job may be using.
export CUDA_VISIBLE_DEVICES=""
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
mkdir -p "${TMPDIR}"

TESTS="${TESTS:-tests/}"
echo "[run] Tests: ${TESTS}"
# shellcheck disable=SC2086
python -m pytest ${TESTS} -q -p no:cacheprovider
echo "[run] DONE"
