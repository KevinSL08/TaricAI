"""
Benchmark de precision del clasificador TARIC.

Ejecuta N clasificaciones contra casos de prueba conocidos
y mide precision a nivel de heading (4 dig) y codigo completo (10 dig).
"""

import json
import sys
import time
import io
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

API_URL = "http://localhost:8000/api/v1/classify"
BENCHMARK_DIR = Path(__file__).parent.parent / "data" / "benchmarks"
DEFAULT_BENCHMARK = BENCHMARK_DIR / "benchmark_105.json"


def run_benchmark(max_cases: int = 105, benchmark_file: Path = DEFAULT_BENCHMARK):
    print("=" * 60)
    print("  TaricAI - Benchmark de Precision")
    print("=" * 60)

    with open(benchmark_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cases = data["cases"][:max_cases]
    print(f"\nCasos a evaluar: {len(cases)}")
    print("-" * 60)

    results = {
        "total": len(cases),
        "exact_match": 0,       # Codigo 10 dig exacto
        "heading_match": 0,     # Heading 4 dig correcto
        "subheading_match": 0,  # 6 primeros digitos correctos
        "errors": 0,
        "details": [],
    }

    for i, case in enumerate(cases):
        desc = case["description"]
        origin = case.get("origin", "")
        expected_code = case["expected_code"]
        expected_heading = case["expected_heading"]

        try:
            payload = {"description": desc}
            if origin:
                payload["origin_country"] = origin

            start = time.time()
            r = requests.post(API_URL, json=payload, timeout=60)
            elapsed = time.time() - start
            resp = r.json()

            predicted_code = resp.get("top_code", "")
            confidence = resp.get("top_confidence", 0)
            source = resp.get("source", "unknown")

            # Comparaciones
            exact = predicted_code == expected_code
            heading_ok = predicted_code[:4] == expected_heading
            subheading_ok = predicted_code[:6] == expected_code[:6]

            if exact:
                results["exact_match"] += 1
                status = "OK EXACT"
            elif subheading_ok:
                results["subheading_match"] += 1
                status = "~SUBHEAD"
            elif heading_ok:
                results["heading_match"] += 1
                status = "~HEADING"
            else:
                status = "X MISS"

            detail = {
                "description": desc,
                "expected": expected_code,
                "predicted": predicted_code,
                "confidence": confidence,
                "heading_match": heading_ok,
                "exact_match": exact,
                "time_s": round(elapsed, 1),
                "source": source,
            }
            results["details"].append(detail)

            print(f"  [{i+1:2d}/{len(cases)}] {status} | {predicted_code} vs {expected_code} | {confidence*100:4.0f}% | {elapsed:.1f}s | {desc[:40]}")

        except Exception as e:
            results["errors"] += 1
            print(f"  [{i+1:2d}/{len(cases)}] ERROR  | {desc[:40]} | {str(e)[:30]}")
            results["details"].append({
                "description": desc,
                "expected": expected_code,
                "predicted": "ERROR",
                "error": str(e),
            })

    # Resumen
    total = results["total"]
    exact = results["exact_match"]
    subhead = results["subheading_match"]
    heading = results["heading_match"]
    errors = results["errors"]

    # Precision acumulada
    heading_precision = (exact + subhead + heading) / total * 100 if total > 0 else 0
    subheading_precision = (exact + subhead) / total * 100 if total > 0 else 0
    exact_precision = exact / total * 100 if total > 0 else 0

    print("\n" + "=" * 60)
    print("  RESULTADOS DEL BENCHMARK")
    print("=" * 60)
    print(f"  Total casos:           {total}")
    print(f"  Errores API:           {errors}")
    print(f"")
    print(f"  Codigo exacto (10d):   {exact}/{total} = {exact_precision:.1f}%")
    print(f"  Subpartida (6d):       {exact+subhead}/{total} = {subheading_precision:.1f}%")
    print(f"  Partida (4d):          {exact+subhead+heading}/{total} = {heading_precision:.1f}%")
    print(f"")
    print(f"  ** Precision heading:  {heading_precision:.1f}% **")
    print(f"  ** Benchmark:          {benchmark_file.name} **")
    print("=" * 60)

    # Guardar resultados
    output_file = Path(__file__).parent.parent / "data" / "benchmarks" / f"results_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total": total,
                "exact_match": exact,
                "subheading_match": subhead,
                "heading_match": heading,
                "errors": errors,
                "exact_precision_pct": round(exact_precision, 1),
                "subheading_precision_pct": round(subheading_precision, 1),
                "heading_precision_pct": round(heading_precision, 1),
            },
            "details": results["details"],
        }, f, indent=2, ensure_ascii=False)
    print(f"\nResultados guardados en: {output_file.name}")


if __name__ == "__main__":
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 105
    # Optional: pass benchmark file as second argument
    bench = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_BENCHMARK
    run_benchmark(max_n, bench)
