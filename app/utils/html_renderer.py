from html import escape
import json
from app.utils.serializer import safe_dumps


def render_result(
    question: str,
    sql: str,
    columns: list,
    rows: list,
    chart_config: str | None = None
) -> str:

    table_headers = "".join(
        [f"<th>{escape(str(col))}</th>" for col in columns])
    table_rows = ""
    for row in rows:
        cells = "".join([f"<td>{escape(str(cell))}</td>" for cell in row])
        table_rows += f"<tr>{cells}</tr>"

    if not rows:
        results_html = """
        <div class="alert alert-info mt-4 text-sm">
            <span>No results found for this query.</span>
        </div>
        """
    else:
        results_html = f"""
        <div class="overflow-x-auto mt-3">
            <table class="table table-zebra table-sm text-sm">
                <thead><tr class="text-base-content/60">{table_headers}</tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
        """

    # Chart — store config in data attribute, NOT inline script
    # index.html listens for htmx:afterSwap and renders it from there
    chart_html = ""
    if chart_config:
        chart_html = f"""
        <div class="divider my-0"></div>
        <div>
            <p class="text-xs text-base-content/40 uppercase tracking-widest mb-3">Chart</p>
            <div style="position:relative; height:260px;">
                <canvas id="resultChart" data-chart='{escape(chart_config)}'></canvas>
            </div>
        </div>
        """

    # Export button — payload in data attribute
    export_btn = ""
    if rows:
        payload_json = safe_dumps({
            "columns": columns,
            "rows": rows,
            "filename": "query_result"
        })
        export_btn = f"""
        <button
            class="btn btn-outline btn-xs gap-1"
            data-export='{escape(payload_json)}'
            onclick="handleExport(this)"
        >
            Export CSV
        </button>
        """

    return f"""
    <div class="card bg-base-100 shadow-xl border border-base-200">
        <div class="card-body gap-4">
            <div>
                <p class="text-xs text-base-content/40 uppercase tracking-widest mb-1">Question</p>
                <p class="text-sm text-base-content/80">{escape(question)}</p>
            </div>
            <div>
                <p class="text-xs text-base-content/40 uppercase tracking-widest mb-2">Generated SQL</p>
                <pre class="bg-base-200 rounded-lg p-3 overflow-x-auto text-xs leading-relaxed"><code class="text-primary">{escape(sql)}</code></pre>
            </div>
            <div class="divider my-0"></div>
            <div>
                <div class="flex items-center justify-between mb-1">
                    <p class="text-xs text-base-content/40 uppercase tracking-widest">Results</p>
                    <div class="flex items-center gap-2">
                        <span class="badge badge-primary badge-sm">
                            {len(rows)} row{"s" if len(rows) != 1 else ""}
                        </span>
                        {export_btn}
                    </div>
                </div>
                {results_html}
            </div>
            {chart_html}
        </div>
    </div>
    """
