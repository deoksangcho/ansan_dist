from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressDialog,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.app_paths import get_app_data_dir
from services.batch_service import BatchProcessResult, process_batch_dataframe
from services.distance_service import DistanceLookupError, WalkingDistanceService
from services.settings_service import DEFAULT_SETTINGS, SettingsService
from services.usage_service import UsageService


BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "logo.png"
APP_ICON_PATH = BASE_DIR / "assets" / "walkdist_icon.png"


APP_STYLESHEET = """
QMainWindow, QWidget {
    background: #f6f7f2;
    color: #1f2a2a;
    font-size: 13px;
}

QGroupBox {
    background: #ffffff;
    border: 1px solid #d9e0d2;
    border-radius: 18px;
    margin-top: 12px;
    padding: 20px 16px 16px 16px;
    font-weight: 600;
    color: #29403b;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 4px 10px;
    color: #26453f;
    background: #e9f3ef;
    border: 1px solid #d0e2db;
    border-radius: 10px;
    font-weight: 700;
}

QLabel#heroTitle {
    font-size: 28px;
    font-weight: 700;
    color: #20413a;
}

QLabel#heroSubtitle {
    font-size: 14px;
    color: #63766f;
}

QLabel#deptLabel {
    font-size: 12px;
    color: #56716a;
    background: #edf3ef;
    border: 1px solid #d7e3dc;
    border-radius: 12px;
    padding: 6px 10px;
    font-weight: 600;
}

QLabel#logoLabel {
    background: transparent;
    padding-right: 14px;
}

QLabel#usageChip {
    background: #eef6ee;
    border: 1px solid #d5e8d7;
    border-radius: 16px;
    padding: 10px 14px;
    font-weight: 600;
    color: #21453d;
}

QLabel#pathValue {
    color: #6e7f78;
    background: #fbfcf7;
    border: 1px dashed #d5ddd0;
    border-radius: 12px;
    padding: 8px 10px;
}

QListWidget#navList {
    background: #eef2e7;
    border: 1px solid #dae1d4;
    border-radius: 20px;
    outline: 0;
    padding: 10px;
}

QListWidget#navList::item {
    border-radius: 14px;
    padding: 12px 14px;
    margin: 4px 0;
    color: #51635f;
}

QListWidget#navList::item:selected {
    background: #2f8f83;
    color: white;
    font-weight: 700;
}

QPushButton {
    background: #ffffff;
    color: #29403b;
    border: 1px solid #d3ddd1;
    border-radius: 14px;
    padding: 10px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background: #f3f8f4;
    border-color: #b9ccc0;
}

QPushButton:pressed {
    background: #e8f0ea;
}

QPushButton#primaryButton {
    background: #2f8f83;
    color: white;
    border: 1px solid #2f8f83;
}

QPushButton#primaryButton:hover {
    background: #277b70;
    border-color: #277b70;
}

QPushButton#accentButton {
    background: #fff3dd;
    color: #8b5b12;
    border: 1px solid #f0d8a7;
}

QPushButton#accentButton:hover {
    background: #ffecc9;
}

QLineEdit, QComboBox {
    background: #fcfdf9;
    border: 1px solid #d8e0d4;
    border-radius: 12px;
    padding: 10px 12px;
    selection-background-color: #bfe2db;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #2f8f83;
    background: #ffffff;
}

QTableWidget {
    background: #ffffff;
    border: 1px solid #d8e0d4;
    border-radius: 14px;
    gridline-color: #edf1e8;
    alternate-background-color: #f7faf6;
}

QHeaderView::section {
    background: #eef4ec;
    color: #48635d;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #d8e0d4;
    font-weight: 700;
}

QProgressDialog {
    background: #f6f7f2;
}
"""


class ServiceContainer:
    def __init__(self) -> None:
        self.app_dir = get_app_data_dir("walkdist")
        self.settings_service = SettingsService(self.app_dir / "config.json")
        self.usage_service = UsageService(self.app_dir / "usage_log.json")

    def load_settings(self) -> dict:
        return self.settings_service.load()

    def save_settings(self, updates: dict) -> dict:
        self.settings_service.save(updates)
        return self.load_settings()

    def clear_api_key(self) -> dict:
        self.settings_service.save({"tmap_app_key": ""})
        return self.load_settings()

    def build_distance_service(self) -> WalkingDistanceService:
        settings = self.load_settings()
        return WalkingDistanceService(
            app_key=settings.get("tmap_app_key", ""),
            usage_service=self.usage_service,
        )

    def load_usage(self) -> dict:
        return self.usage_service.today_usage()


def set_table_data(table: QTableWidget, dataframe: pd.DataFrame) -> None:
    preview_df = dataframe.fillna("")
    table.clear()
    table.setColumnCount(len(preview_df.columns))
    table.setHorizontalHeaderLabels([str(column) for column in preview_df.columns])
    table.setRowCount(len(preview_df.index))

    for row_index in range(len(preview_df.index)):
        for column_index, column_name in enumerate(preview_df.columns):
            value = preview_df.iloc[row_index, column_index]
            table.setItem(row_index, column_index, QTableWidgetItem(str(value)))

    table.resizeColumnsToContents()


def make_scrollable(widget: QWidget) -> QScrollArea:
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.NoFrame)
    scroll_area.setWidget(widget)
    return scroll_area


class QStackedWidgetCompat(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._widgets: list[QWidget] = []

    def addWidget(self, widget: QWidget) -> None:
        widget.setVisible(False)
        self._widgets.append(widget)
        self._layout.addWidget(widget)

    def setCurrentIndex(self, index: int) -> None:
        for position, widget in enumerate(self._widgets):
            widget.setVisible(position == index)


class SingleLookupPage(QWidget):
    def __init__(self, services: ServiceContainer, parent_window: "MainWindow") -> None:
        super().__init__()
        self.services = services
        self.parent_window = parent_window

        layout = QVBoxLayout(self)
        group_box = QGroupBox("단건 조회")
        group_layout = QFormLayout(group_box)

        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("예: 서울특별시 종로구 세종대로 110")
        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("예: 서울특별시 중구 세종대로 99")
        self.calculate_button = QPushButton("도보 거리 계산")
        self.calculate_button.setObjectName("primaryButton")
        self.calculate_button.clicked.connect(self.calculate_distance)

        self.distance_label = QLabel("-")
        self.duration_label = QLabel("-")

        group_layout.addRow("출발지 주소", self.start_input)
        group_layout.addRow("도착지 주소", self.end_input)
        group_layout.addRow(self.calculate_button)
        group_layout.addRow("도보 거리", self.distance_label)
        group_layout.addRow("예상 시간", self.duration_label)

        layout.addWidget(group_box)
        layout.addStretch(1)

    def calculate_distance(self) -> None:
        start_address = self.start_input.text().strip()
        end_address = self.end_input.text().strip()

        if not start_address or not end_address:
            QMessageBox.warning(self, "입력 확인", "출발지와 도착지 주소를 모두 입력해 주세요.")
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            result = self.services.build_distance_service().get_walking_distance(start_address, end_address)
        except DistanceLookupError as exc:
            QMessageBox.critical(self, "계산 실패", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()

        self.distance_label.setText(f"{result.distance_km:.2f} km")
        self.duration_label.setText("-" if result.duration_minutes is None else f"{result.duration_minutes:.0f} 분")
        self.parent_window.refresh_usage_summary()


class BatchLookupPage(QWidget):
    def __init__(self, services: ServiceContainer, parent_window: "MainWindow") -> None:
        super().__init__()
        self.services = services
        self.parent_window = parent_window
        self.source_dataframe: Optional[pd.DataFrame] = None
        self.output_result: Optional[BatchProcessResult] = None

        layout = QVBoxLayout(self)

        header_box = QGroupBox("엑셀 일괄 처리")
        header_layout = QVBoxLayout(header_box)
        self.select_file_button = QPushButton("엑셀 파일 선택")
        self.select_file_button.setObjectName("accentButton")
        self.select_file_button.clicked.connect(self.select_excel_file)
        self.file_label = QLabel("선택된 파일이 없습니다.")
        self.note_label = QLabel("엑셀 주소열은 저장된 기본값 또는 업로드 후 선택한 열 기준으로 처리됩니다.")
        self.note_label.setWordWrap(True)
        header_layout.addWidget(self.select_file_button)
        header_layout.addWidget(self.file_label)
        header_layout.addWidget(self.note_label)

        selection_box = QGroupBox("열 설정")
        selection_layout = QFormLayout(selection_box)
        self.start_column_combo = QComboBox()
        self.end_column_combo = QComboBox()
        self.result_column_edit = QLineEdit()
        self.save_defaults_button = QPushButton("현재 선택을 기본값으로 저장")
        self.save_defaults_button.setObjectName("accentButton")
        self.save_defaults_button.clicked.connect(self.save_default_columns)
        selection_layout.addRow("출발지 열", self.start_column_combo)
        selection_layout.addRow("도착지 열", self.end_column_combo)
        selection_layout.addRow("결과 열", self.result_column_edit)
        selection_layout.addRow(self.save_defaults_button)

        action_box = QGroupBox("실행 및 저장")
        action_layout = QVBoxLayout(action_box)
        self.run_button = QPushButton("일괄 계산 실행")
        self.run_button.setObjectName("primaryButton")
        self.run_button.clicked.connect(self.run_batch)
        self.save_output_button = QPushButton("결과 엑셀 저장")
        self.save_output_button.setObjectName("accentButton")
        self.save_output_button.clicked.connect(self.save_output_excel)
        self.save_output_button.setEnabled(False)
        self.save_failure_button = QPushButton("실패 행만 엑셀 저장")
        self.save_failure_button.setObjectName("accentButton")
        self.save_failure_button.clicked.connect(self.save_failure_excel)
        self.save_failure_button.setEnabled(False)
        self.summary_label = QLabel("-")
        self.summary_label.setWordWrap(True)
        action_layout.addWidget(self.run_button)
        action_layout.addWidget(self.save_output_button)
        action_layout.addWidget(self.save_failure_button)
        action_layout.addWidget(self.summary_label)

        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setMinimumHeight(220)
        self.failure_table = QTableWidget()
        self.failure_table.setAlternatingRowColors(True)
        self.failure_table.setMinimumHeight(180)

        layout.addWidget(header_box)
        layout.addWidget(selection_box)
        layout.addWidget(action_box)
        layout.addWidget(QLabel("미리보기"))
        layout.addWidget(self.preview_table)
        layout.addWidget(QLabel("실패 행"))
        layout.addWidget(self.failure_table)
        layout.addStretch(1)

        self.apply_settings(self.services.load_settings())

    def apply_settings(self, settings: dict) -> None:
        self.result_column_edit.setText(settings.get("default_result_column", DEFAULT_SETTINGS["default_result_column"]))
        self._apply_default_columns(settings)

    def _apply_default_columns(self, settings: dict) -> None:
        if self.start_column_combo.count() == 0:
            return

        for combo, key in (
            (self.start_column_combo, "default_start_column"),
            (self.end_column_combo, "default_end_column"),
        ):
            index = combo.findText(settings.get(key, ""))
            if index >= 0:
                combo.setCurrentIndex(index)

    def select_excel_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "엑셀 파일 선택", "", "Excel Files (*.xlsx)")
        if not file_path:
            return

        try:
            dataframe = pd.read_excel(file_path)
        except Exception as exc:
            QMessageBox.critical(self, "파일 오류", f"엑셀 파일을 읽지 못했습니다.\n{exc}")
            return

        self.source_dataframe = dataframe.rename(columns={column: str(column) for column in dataframe.columns})
        self.output_result = None
        self.file_label.setText(file_path)
        set_table_data(self.preview_table, self.source_dataframe.head(10))
        self.failure_table.clear()
        self.failure_table.setRowCount(0)
        self.failure_table.setColumnCount(0)
        self.save_output_button.setEnabled(False)
        self.save_failure_button.setEnabled(False)
        self.summary_label.setText(f"파일 불러오기 완료: {len(self.source_dataframe)}행")

        columns = list(self.source_dataframe.columns)
        self.start_column_combo.clear()
        self.start_column_combo.addItems(columns)
        self.end_column_combo.clear()
        self.end_column_combo.addItems(columns)
        self._apply_default_columns(self.services.load_settings())

    def save_default_columns(self) -> None:
        if self.start_column_combo.count() == 0:
            QMessageBox.information(self, "알림", "먼저 엑셀 파일을 불러와 주세요.")
            return

        settings = self.services.save_settings(
            {
                "default_start_column": self.start_column_combo.currentText(),
                "default_end_column": self.end_column_combo.currentText(),
                "default_result_column": self.result_column_edit.text().strip() or DEFAULT_SETTINGS["default_result_column"],
            }
        )
        self.apply_settings(settings)
        self.parent_window.apply_settings_to_pages()
        QMessageBox.information(self, "저장 완료", "기본 열 설정을 저장했습니다.")

    def run_batch(self) -> None:
        if self.source_dataframe is None:
            QMessageBox.warning(self, "실행 불가", "먼저 엑셀 파일을 선택해 주세요.")
            return

        result_column = self.result_column_edit.text().strip()
        if not result_column:
            QMessageBox.warning(self, "입력 확인", "결과 열 이름을 입력해 주세요.")
            return

        progress_dialog = QProgressDialog("일괄 계산 중...", "취소", 0, len(self.source_dataframe), self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimumDuration(0)

        def progress_callback(current: int, total: int, message: str) -> None:
            progress_dialog.setMaximum(total)
            progress_dialog.setValue(current)
            progress_dialog.setLabelText(f"엑셀 처리 중... {message}")
            QApplication.processEvents()

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            result = process_batch_dataframe(
                dataframe=self.source_dataframe,
                start_column=self.start_column_combo.currentText(),
                end_column=self.end_column_combo.currentText(),
                result_column=result_column,
                distance_service=self.services.build_distance_service(),
                progress_callback=progress_callback,
            )
        except DistanceLookupError as exc:
            QMessageBox.critical(self, "실행 실패", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "실행 실패", f"일괄 처리 중 오류가 발생했습니다.\n{exc}")
            return
        finally:
            progress_dialog.close()
            QApplication.restoreOverrideCursor()

        self.output_result = result
        set_table_data(self.preview_table, result.output_df.head(20))
        if result.failure_df.empty:
            self.failure_table.clear()
            self.failure_table.setRowCount(0)
            self.failure_table.setColumnCount(0)
            self.save_failure_button.setEnabled(False)
        else:
            set_table_data(self.failure_table, result.failure_df)
            self.save_failure_button.setEnabled(True)

        self.summary_label.setText(f"총 {len(result.output_df)}건 처리 / 성공 {result.success_count}건 / 실패 {result.failure_count}건")
        self.save_output_button.setEnabled(True)
        self.parent_window.refresh_usage_summary()
        QMessageBox.information(self, "처리 완료", "일괄 계산이 완료되었습니다.")

    def save_output_excel(self) -> None:
        if self.output_result is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "결과 엑셀 저장", "walking_distance_result.xlsx", "Excel Files (*.xlsx)")
        if not file_path:
            return

        self.output_result.output_df.to_excel(file_path, index=False)
        QMessageBox.information(self, "저장 완료", "결과 파일을 저장했습니다.")

    def save_failure_excel(self) -> None:
        if self.output_result is None or self.output_result.failure_df.empty:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "실패 행 엑셀 저장", "walking_distance_failures.xlsx", "Excel Files (*.xlsx)")
        if not file_path:
            return

        self.output_result.failure_df.to_excel(file_path, index=False)
        QMessageBox.information(self, "저장 완료", "실패 행 파일을 저장했습니다.")


class SettingsPage(QWidget):
    def __init__(self, services: ServiceContainer, parent_window: "MainWindow") -> None:
        super().__init__()
        self.services = services
        self.parent_window = parent_window

        layout = QVBoxLayout(self)

        settings_box = QGroupBox("환경 설정")
        form_layout = QFormLayout(settings_box)

        self.default_start_edit = QLineEdit()
        self.default_end_edit = QLineEdit()
        self.default_result_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)

        form_layout.addRow("기본 출발지 열", self.default_start_edit)
        form_layout.addRow("기본 도착지 열", self.default_end_edit)
        form_layout.addRow("기본 결과 열", self.default_result_edit)
        form_layout.addRow("TMAP App Key", self.api_key_edit)

        button_row = QHBoxLayout()
        self.save_button = QPushButton("설정 저장")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save_settings)
        self.clear_key_button = QPushButton("API Key 삭제")
        self.clear_key_button.setObjectName("accentButton")
        self.clear_key_button.clicked.connect(self.clear_api_key)
        self.open_naver_button = QPushButton("네이버지도")
        self.open_naver_button.setObjectName("accentButton")
        self.open_naver_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://map.naver.com/")))
        self.open_kakao_button = QPushButton("카카오맵")
        self.open_kakao_button.setObjectName("accentButton")
        self.open_kakao_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://map.kakao.com/")))
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.clear_key_button)
        button_row.addStretch(1)
        button_row.addWidget(self.open_naver_button)
        button_row.addWidget(self.open_kakao_button)

        helper_label = QLabel(
            "기본 열 설정은 엑셀 업로드 후 자동 선택에 사용됩니다. "
            "TMAP App Key는 여기서 변경하면 이후 조회부터 바로 반영됩니다."
        )
        helper_label.setWordWrap(True)

        layout.addWidget(settings_box)
        layout.addLayout(button_row)
        layout.addWidget(helper_label)
        layout.addStretch(1)

    def apply_settings(self, settings: dict) -> None:
        self.default_start_edit.setText(settings.get("default_start_column", DEFAULT_SETTINGS["default_start_column"]))
        self.default_end_edit.setText(settings.get("default_end_column", DEFAULT_SETTINGS["default_end_column"]))
        self.default_result_edit.setText(settings.get("default_result_column", DEFAULT_SETTINGS["default_result_column"]))
        self.api_key_edit.setText(settings.get("tmap_app_key", ""))

    def save_settings(self) -> None:
        settings = self.services.save_settings(
            {
                "default_start_column": self.default_start_edit.text().strip() or DEFAULT_SETTINGS["default_start_column"],
                "default_end_column": self.default_end_edit.text().strip() or DEFAULT_SETTINGS["default_end_column"],
                "default_result_column": self.default_result_edit.text().strip() or DEFAULT_SETTINGS["default_result_column"],
                "tmap_app_key": self.api_key_edit.text().strip(),
            }
        )
        self.apply_settings(settings)
        self.parent_window.apply_settings_to_pages()
        QMessageBox.information(self, "저장 완료", "설정을 저장했습니다.")

    def clear_api_key(self) -> None:
        settings = self.services.clear_api_key()
        self.apply_settings(settings)
        self.parent_window.apply_settings_to_pages()
        QMessageBox.information(self, "삭제 완료", "TMAP App Key를 삭제했습니다.")


class MainWindow(QMainWindow):
    def __init__(self, services: ServiceContainer) -> None:
        super().__init__()
        self.services = services
        self.setWindowTitle("도보 거리 계산기")
        self.resize(1120, 800)
        if APP_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(16)

        hero_box = QWidget()
        hero_layout = QVBoxLayout(hero_box)
        hero_layout.setContentsMargins(4, 0, 4, 0)
        hero_title_row = QHBoxLayout()
        hero_title_row.setSpacing(14)
        if LOGO_PATH.exists():
            logo_label = QLabel()
            logo_label.setObjectName("logoLabel")
            logo_pixmap = QPixmap(str(LOGO_PATH))
            if not logo_pixmap.isNull():
                logo_label.setPixmap(
                    logo_pixmap.scaled(
                        96,
                        96,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )
                logo_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
                hero_title_row.addWidget(logo_label, 0, Qt.AlignTop)
        text_column = QVBoxLayout()
        text_column.setSpacing(6)
        hero_title = QLabel("도보 거리 계산기")
        hero_title.setObjectName("heroTitle")
        dept_label = QLabel("안산교육지원청 학교행정지원과")
        dept_label.setObjectName("deptLabel")
        hero_subtitle = QLabel("주소 간 도보 거리를 조회하고 엑셀 결과를 저장합니다.")
        hero_subtitle.setObjectName("heroSubtitle")
        hero_subtitle.setWordWrap(True)
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_row.addWidget(hero_title, 0, Qt.AlignVCenter)
        title_row.addWidget(dept_label, 0, Qt.AlignVCenter)
        title_row.addStretch(1)
        text_column.addLayout(title_row)
        text_column.addWidget(hero_subtitle)
        hero_title_row.addLayout(text_column, 1)
        hero_layout.addLayout(hero_title_row)

        summary_box = QGroupBox("오늘 사용량")
        summary_layout = QHBoxLayout(summary_box)
        self.geocoding_label = QLabel()
        self.geocoding_label.setObjectName("usageChip")
        self.routing_label = QLabel()
        self.routing_label.setObjectName("usageChip")
        self.path_label = QLabel(str(self.services.app_dir))
        self.path_label.setObjectName("pathValue")
        self.path_label.setWordWrap(True)
        summary_layout.addWidget(self.geocoding_label)
        summary_layout.addWidget(self.routing_label)
        summary_layout.addStretch(1)
        summary_layout.addWidget(QLabel("설정 저장 경로"))
        summary_layout.addWidget(self.path_label, 1)

        splitter = QSplitter()
        self.navigation = QListWidget()
        self.navigation.setObjectName("navList")
        self.navigation.setMaximumWidth(180)
        self.navigation.addItem(QListWidgetItem("엑셀 일괄 처리"))
        self.navigation.addItem(QListWidgetItem("단건 조회"))
        self.navigation.addItem(QListWidgetItem("설정"))

        self.pages = QStackedWidgetCompat()
        self.batch_page = BatchLookupPage(services, self)
        self.single_page = SingleLookupPage(services, self)
        self.settings_page = SettingsPage(services, self)
        self.pages.addWidget(make_scrollable(self.batch_page))
        self.pages.addWidget(make_scrollable(self.single_page))
        self.pages.addWidget(make_scrollable(self.settings_page))

        splitter.addWidget(self.navigation)
        splitter.addWidget(self.pages)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(hero_box)
        root_layout.addWidget(summary_box)
        root_layout.addWidget(splitter, 1)

        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)
        self.apply_settings_to_pages()
        self.refresh_usage_summary()

    def apply_settings_to_pages(self) -> None:
        settings = self.services.load_settings()
        self.batch_page.apply_settings(settings)
        self.settings_page.apply_settings(settings)
        self.refresh_usage_summary()

    def refresh_usage_summary(self) -> None:
        usage = self.services.load_usage()
        self.geocoding_label.setText(f"지오코딩: {usage['geocoding_used']} / {usage['geocoding_limit']}")
        self.routing_label.setText(f"경로안내: {usage['routing_used']} / {usage['routing_limit']}")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("walkdist")
    if APP_ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindow(ServiceContainer())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
