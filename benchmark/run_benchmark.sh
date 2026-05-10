#!/usr/bin/env bash
# =============================================================================
# benchmark/run_benchmark.sh
# Benchmark script using ApacheBench (ab)
#
# Usage:
#   ./run_benchmark.sh [HOST] [PORT]
#
# Examples:
#   ./run_benchmark.sh                  # defaults: localhost:80
#   ./run_benchmark.sh 192.168.1.10 80
#
# Requirements:
#   - apache2-utils (ab command)
#   - Install on Debian/Ubuntu: sudo apt install apache2-utils
# =============================================================================

set -euo pipefail

HOST="${1:-localhost}"
PORT="${2:-80}"
BASE_URL="http://${HOST}:${PORT}"

TOTAL_REQUESTS=500
CONCURRENCY_LEVELS=(10 50 100 200)

OUTPUT_DIR="./results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${OUTPUT_DIR}/benchmark_${TIMESTAMP}.txt"

mkdir -p "$OUTPUT_DIR"

# ── Helpers ──────────────────────────────────────────────────────────────────

header() { echo; echo "═══════════════════════════════════════════════════════"; echo "  $1"; echo "═══════════════════════════════════════════════════════"; }
section() { echo; echo "── $1"; }

run_ab() {
  local label="$1"
  local url="$2"
  local c="$3"
  local n="$4"

  echo
  echo "  Concurență: ${c} | Total requesturi: ${n}"
  echo "  URL: ${url}"

  ab -n "$n" -c "$c" -q "$url" 2>&1 \
    | grep -E "Requests per second|Time per request \(mean\)|Failed requests|50%|95%|99%" \
    | sed 's/^/    /'
}

# ── Intro ────────────────────────────────────────────────────────────────────

{
header "Flask Performance Benchmark – $(date)"
echo "  Target: ${BASE_URL}"
echo "  Requesturi per test: ${TOTAL_REQUESTS}"
echo "  Niveluri de concurență: ${CONCURRENCY_LEVELS[*]}"

# ── Health check ─────────────────────────────────────────────────────────────

header "Health Check"
HEALTH=$(curl -sf "${BASE_URL}/health" || echo '{"status":"UNREACHABLE"}')
echo "  $HEALTH"

# ── CPU-bound benchmark ───────────────────────────────────────────────────────

header "CPU-BOUND BENCHMARK  (/api/benchmark/cpu?value=42)"
for C in "${CONCURRENCY_LEVELS[@]}"; do
  run_ab "cpu" "${BASE_URL}/api/benchmark/cpu?value=42" "$C" "$TOTAL_REQUESTS"
done

# ── I/O-bound benchmark (5 inserts per request) ───────────────────────────────

header "I/O-BOUND BENCHMARK  (/api/benchmark/io?count=5)"
for C in "${CONCURRENCY_LEVELS[@]}"; do
  run_ab "io" "${BASE_URL}/api/benchmark/io?count=5" "$C" "$TOTAL_REQUESTS"
done

# ── Done ──────────────────────────────────────────────────────────────────────

header "Benchmark finalizat – rezultate salvate în ${OUTPUT_FILE}"

} | tee "$OUTPUT_FILE"
