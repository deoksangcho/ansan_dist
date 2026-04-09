from dataclasses import dataclass
from typing import Callable, Optional

import pandas as pd

from services.distance_service import DistanceLookupError, WalkingDistanceService


ProgressCallback = Callable[[int, int, str], None]


@dataclass
class BatchProcessResult:
    output_df: pd.DataFrame
    failure_df: pd.DataFrame
    success_count: int
    failure_count: int


def process_batch_dataframe(
    dataframe: pd.DataFrame,
    start_column: str,
    end_column: str,
    result_column: str,
    distance_service: WalkingDistanceService,
    progress_callback: Optional[ProgressCallback] = None,
) -> BatchProcessResult:
    output_df = dataframe.copy()
    result_values: list[object] = []
    failure_records: list[dict[str, object]] = []
    success_count = 0
    failure_count = 0
    total_rows = len(output_df.index)

    for position, (_, row) in enumerate(output_df.iterrows(), start=1):
        start_address = row[start_column]
        end_address = row[end_column]
        excel_row_number = position + 1

        if pd.isna(start_address) or pd.isna(end_address):
            message = "주소 누락"
            result_values.append(message)
            failure_records.append(
                {
                    "행 번호": excel_row_number,
                    "출발지": start_address,
                    "도착지": end_address,
                    "오류": message,
                }
            )
            failure_count += 1
        else:
            try:
                result = distance_service.get_walking_distance(str(start_address), str(end_address))
                result_values.append(round(result.distance_km, 3))
                success_count += 1
            except DistanceLookupError as exc:
                message = str(exc)
                result_values.append(f"실패: {message}")
                failure_records.append(
                    {
                        "행 번호": excel_row_number,
                        "출발지": start_address,
                        "도착지": end_address,
                        "오류": message,
                    }
                )
                failure_count += 1

        if progress_callback is not None:
            progress_callback(position, total_rows, f"{position}/{total_rows}")

    output_df[result_column] = result_values
    failure_df = pd.DataFrame(failure_records)

    return BatchProcessResult(
        output_df=output_df,
        failure_df=failure_df,
        success_count=success_count,
        failure_count=failure_count,
    )
