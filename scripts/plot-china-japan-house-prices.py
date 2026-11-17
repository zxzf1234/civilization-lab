#!/usr/bin/env python3
"""下载 BIS 中日住宅价格数据并绘制历史走势与峰值对齐图。"""

from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
from matplotlib import font_manager


BIS_BULK_URL = "https://data.bis.org/static/bulk/WS_SPP_csv_flat.zip"
COUNTRIES = {"CN": "中国", "JP": "日本"}
VALUE_CODES = {"real": "R", "nominal": "N"}
VALUE_LABELS = {"real": "实际住宅价格（CPI 调整）", "nominal": "名义住宅价格"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--measure",
        choices=VALUE_CODES,
        default="real",
        help="价格口径，默认 real（实际价格）；也可选 nominal（名义价格）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("figures/china-japan-house-prices.png"),
        help="走势图输出路径",
    )
    parser.add_argument(
        "--data-output",
        type=Path,
        default=Path("data/china-japan-house-prices.csv"),
        help="清洗后数据输出路径",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60,
        help="网络请求超时秒数",
    )
    return parser.parse_args()


def download_bis(timeout: float) -> tuple[pd.DataFrame, str]:
    response = requests.get(
        BIS_BULK_URL,
        timeout=timeout,
        headers={"User-Agent": "civilization-lab-house-price-comparison/1.0"},
    )
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        csv_names = [name for name in archive.namelist() if name.endswith(".csv")]
        if len(csv_names) != 1:
            raise RuntimeError(f"BIS 压缩包中的 CSV 数量异常：{csv_names}")
        with archive.open(csv_names[0]) as csv_file:
            frame = pd.read_csv(csv_file, low_memory=False)
    return frame, response.headers.get("last-modified", "未提供")


def prepare_data(raw: pd.DataFrame, measure: str) -> pd.DataFrame:
    area_col = "REF_AREA:Reference area"
    value_col = "VALUE:Value"
    unit_col = "UNIT_MEASURE:Unit of measure"
    time_col = "TIME_PERIOD:Time period or range"
    obs_col = "OBS_VALUE:Observation Value"

    area_code = raw[area_col].astype(str).str.split(":", n=1).str[0]
    value_code = raw[value_col].astype(str).str.split(":", n=1).str[0]
    unit_code = raw[unit_col].astype(str).str.split(":", n=1).str[0]

    selected = raw.loc[
        area_code.isin(COUNTRIES)
        & value_code.eq(VALUE_CODES[measure])
        & unit_code.eq("628"),
        [area_col, time_col, obs_col],
    ].copy()
    selected["country_code"] = selected[area_col].str.split(":", n=1).str[0]
    selected["country"] = selected["country_code"].map(COUNTRIES)
    selected["quarter"] = pd.PeriodIndex(selected[time_col], freq="Q")
    selected["date"] = selected["quarter"].dt.to_timestamp(how="end").dt.normalize()
    selected["price_index_2010_100"] = pd.to_numeric(selected[obs_col], errors="coerce")
    selected = selected.dropna(subset=["price_index_2010_100"])
    selected = selected.sort_values(["country_code", "quarter"])
    selected["yoy_percent"] = selected.groupby("country_code")[
        "price_index_2010_100"
    ].pct_change(4, fill_method=None) * 100

    peak_rows = selected.loc[
        selected.groupby("country_code")["price_index_2010_100"].idxmax(),
        ["country_code", "quarter", "price_index_2010_100"],
    ].rename(columns={"quarter": "peak_quarter", "price_index_2010_100": "peak_value"})
    selected = selected.merge(peak_rows, on="country_code", how="left")
    selected["quarters_from_peak"] = selected.apply(
        lambda row: row["quarter"].ordinal - row["peak_quarter"].ordinal, axis=1
    )
    selected["peak_normalized_100"] = (
        selected["price_index_2010_100"] / selected["peak_value"] * 100
    )
    return selected[
        [
            "country_code",
            "country",
            "quarter",
            "date",
            "price_index_2010_100",
            "yoy_percent",
            "peak_quarter",
            "quarters_from_peak",
            "peak_normalized_100",
        ]
    ]


def configure_chinese_font() -> None:
    candidates = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS"]
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for candidate in candidates:
        if candidate in installed:
            plt.rcParams["font.sans-serif"] = [candidate]
            break
    plt.rcParams["axes.unicode_minus"] = False


def plot_comparison(data: pd.DataFrame, measure: str, output: Path) -> None:
    configure_chinese_font()
    colors = {"CN": "#c43c39", "JP": "#356aa0"}
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    fig.subplots_adjust(top=0.88, bottom=0.09, hspace=0.38)

    aligned = data[data["quarters_from_peak"].between(-40, 60)]
    for code, country in COUNTRIES.items():
        country_data = aligned[aligned["country_code"] == code]
        peak_quarter = country_data["peak_quarter"].iloc[0]
        axes[0].plot(
            country_data["quarters_from_peak"] / 4,
            country_data["peak_normalized_100"],
            label=f"{country}（峰值 {peak_quarter}）",
            color=colors[code],
            linewidth=2.2,
        )
    axes[0].axvline(0, color="#555555", linestyle="--", linewidth=1)
    axes[0].axhline(100, color="#999999", linestyle=":", linewidth=1)
    axes[0].set_title("各自样本峰值对齐（峰值 = 100）")
    axes[0].set_xlabel("距各自峰值的年数")
    axes[0].set_ylabel("峰值标准化指数")
    axes[0].legend()

    for code, country in COUNTRIES.items():
        country_data = aligned[aligned["country_code"] == code]
        axes[1].plot(
            country_data["quarters_from_peak"] / 4,
            country_data["yoy_percent"],
            label=country,
            color=colors[code],
            linewidth=1.9,
        )
    # 情景外推只描述“同比跌幅逐年收窄”的速度，不是结构模型预测。
    china = aligned[aligned["country_code"] == "CN"]
    last_x = china["quarters_from_peak"].iloc[-1] / 4
    last_y = china["yoy_percent"].iloc[-1]
    target_y = -2.0
    scenario_slopes = {"较快收窄": 2.0, "近期趋势": 1.3, "较慢收窄": 0.75}
    scenario_styles = {"较快收窄": "--", "近期趋势": "-.", "较慢收窄": ":"}
    for label, slope in scenario_slopes.items():
        years_needed = max(0.0, (target_y - last_y) / slope)
        axes[1].plot(
            [last_x, last_x + years_needed],
            [last_y, target_y],
            color=colors["CN"],
            linestyle=scenario_styles[label],
            linewidth=1.4,
            alpha=0.75,
            label=f"中国情景：{label}",
        )
    axes[1].axhline(-2, color="#777777", linestyle="--", linewidth=1, alpha=0.7)
    axes[1].text(15.1, -1.8, "少跌阈值：同比 -2%", fontsize=9, color="#555555")
    axes[1].axvline(0, color="#555555", linestyle="--", linewidth=1)
    axes[1].axhline(0, color="#999999", linestyle=":", linewidth=1)
    axes[1].set_xlim(-10.5, 17.5)
    axes[1].set_title("各自峰值前后的同比涨跌幅及中国情景外推")
    axes[1].set_xlabel("距各自峰值的年数")
    axes[1].set_ylabel("同比（%）")
    axes[1].legend(ncol=2, fontsize=9)

    for axis in axes:
        axis.grid(alpha=0.22)

    fig.suptitle(
        "中国与日本住宅价格周期比较\n数据：BIS Selected Residential Property Prices",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.018,
        "说明：实际价格为名义住宅价格经 CPI 调整。各国基础序列虽经 BIS 筛选以提高可比性，统计覆盖仍不完全相同。",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    raw, last_modified = download_bis(args.timeout)
    data = prepare_data(raw, args.measure)
    args.data_output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(args.data_output, index=False, encoding="utf-8-sig")
    plot_comparison(data, args.measure, args.output)

    print(f"BIS 数据更新时间（HTTP）：{last_modified}")
    for code, country in COUNTRIES.items():
        country_data = data[data["country_code"] == code]
        peak = country_data.loc[country_data["price_index_2010_100"].idxmax()]
        latest = country_data.iloc[-1]
        decline = (latest["price_index_2010_100"] / peak["price_index_2010_100"] - 1) * 100
        print(
            f"{country}: 峰值 {peak['quarter']}，最新 {latest['quarter']}，"
            f"较峰值 {decline:.1f}%"
        )
    print(f"图表：{args.output.resolve()}")
    print(f"数据：{args.data_output.resolve()}")


if __name__ == "__main__":
    main()
