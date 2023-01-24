from typing import Optional
from pathlib import Path

import flet as ft

from src.engine_handle import predict

class Main:
    def __init__(self):
        self.page = None
        self.predicted_encoding_text = None
        self.file_path = None

    def main_flet(self, page: ft.Page):
        self.page = page

        def set_predicted_encoding_text(encoding: str):
            self.predicted_encoding_text.value = f'Predicted encoding: {encoding}'
            page.update()

        def set_predicted_encoding_text_default():
            set_predicted_encoding_text('INVALID FILE')

        def validate_filepath_exists(path: str = None) -> Optional[Path]:
            if not path:
                set_predicted_encoding_text_default()

            path = Path(path)
            if not path.is_file() or not path.exists():
                set_predicted_encoding_text_default()
                path = None

            return path

        def handle_filepath_inserted(path: Path):
            """runs when we have a valid path to subtitle"""

            predicted_encoding = predict(path)

            self.file_path.value = path
            set_predicted_encoding_text(predicted_encoding)

        def on_file_picker_dialog(e: ft.FilePickerResultEvent):
            """runs if the path is chosen from file explorer"""

            if not e.files:
                set_predicted_encoding_text_default()
                return

            file_info = e.files[0]
            subtitle_file_path = validate_filepath_exists(file_info.path)

            if subtitle_file_path:
                handle_filepath_inserted(subtitle_file_path)

        def on_path_value_change(e: ft.ControlEvent):
            """runs if value in text field changes"""

            subtitle_file_path = validate_filepath_exists(e.data)

            if subtitle_file_path:
                handle_filepath_inserted(subtitle_file_path)

        def build_app():
            page.window_width = 800
            page.window_height = 300

            title = ft.Text('Subtitle Encoder', size=30)
            title_container = ft.Container(content=title, alignment=ft.alignment.center)

            file_picker = ft.FilePicker(on_result=on_file_picker_dialog)
            page.overlay.append(file_picker)

            self.file_path = ft.TextField(
                label='Insert file path OR choose subtitle file through file explorer',
                width=600,
                text_size=13,
                on_change=on_path_value_change,
            )

            file_btn = ft.ElevatedButton(
                'Choose file',
                on_click=lambda _: file_picker.pick_files(allowed_extensions=['srt', 'sub', 'ass'])
            )
            fu_row = ft.Row(controls=[
                self.file_path,
                file_btn
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            fu_container = ft.Container(content=fu_row, margin=ft.margin.symmetric(0, 20))

            self.predicted_encoding_text = ft.Text(size=16)
            set_predicted_encoding_text('NO FILE CHOSEN')
            self.predicted_encoding_hint = ft.Text('AA', size=16)
            predicted_row = ft.Row(controls=[
                self.predicted_encoding_text,
                self.predicted_encoding_hint
            ], vertical_alignment=ft.CrossAxisAlignment.START)
            predicted_encoding_container = ft.Container(
                content=predicted_row,
                margin=ft.margin.symmetric(0, 20),
                expand=True,
            )

            page.add(
                title_container,
                fu_container,
                predicted_encoding_container
            )

        build_app()

    def start(self):
        ft.app(target=self.main_flet)


if __name__ == '__main__':
    main = Main()
    main.start()


