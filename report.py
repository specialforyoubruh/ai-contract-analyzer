# report.py

def format_report(results: dict) -> None:
    """
    Формирует и выводит структурированный отчёт о рисках по договору.
    """
    print("\n========== CONTRACT RISK REPORT ==========\n")

    for category, data in results.items():
        level = data.get("risk_level", "OK")

        prefix = {
            "CRITICAL": "⚠️ КРИТИЧЕСКИЙ РИСК",
            "HIGH": "⚡ ВЫСОКИЙ РИСК",
            "OK": "✓ OK"
        }.get(level, "ℹ️")

        print(f"{prefix}: {category}")

        if data.get("clause"):
            print(f"Пункт договора: {data['clause']}")

        print(f"Описание: {data.get('description')}")
        print(f"Рекомендация: {data.get('recommendation')}")
        print()

