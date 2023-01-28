from typing import Optional
from pathlib import Path

import flet as ft

from src.engine_handle import predict
from src.encodings import encodings


class Main:
    def __init__(self):
        self.page = None
        self.predicted_encoding_text = None
        self.file_path = None

    def main_flet(self, page: ft.Page):
        self.page = page

        def set_predicted_encoding_text(encoding: str):
            self.predicted_encoding_text.value = f'Predicted encoding of the original file: {encoding.upper()}'
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
            page.window_height = 550

            title = ft.Text('Plain Text Encoder', size=30)
            title_container = ft.Container(content=title, alignment=ft.alignment.center, padding=20)

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
                on_click=lambda _: file_picker.pick_files()
            )
            fu_row = ft.Row(controls=[
                self.file_path,
                file_btn
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            fu_container = ft.Container(content=fu_row, margin=ft.margin.symmetric(0, 20))

            # PREDICTED
            def on_hint_click(_):
                if predicted_encoding_hint.visible:
                    predicted_encoding_hint.visible = False
                    page.window_height = page.window_height - 50
                else:
                    predicted_encoding_hint.visible = True
                    page.window_height = page.window_height + 50
                page.update()

            self.predicted_encoding_text = ft.Text(size=16)
            set_predicted_encoding_text('NO FILE CHOSEN')
            predicted_encoding_hint_icon = ft.Container(
                content=ft.Icon(ft.icons.QUESTION_MARK_SHARP, size=20),
                on_hover=on_hint_click
            )

            # HINT
            predicted_encoding_hint_row = ft.Column(controls=[
                ft.Row(controls=[
                    ft.Icon(ft.icons.ALBUM),
                    ft.Text('Globally accepted standard is the "UTF-8"'),
                ]),
                ft.Row(controls=[
                    ft.Icon(ft.icons.ALBUM),
                    ft.Text('For most TV subtitles I recommend the "UTF-8-SIG"')
                ]),
            ], spacing=0)
            predicted_encoding_hint = ft.Container(
                content=predicted_encoding_hint_row,
                visible=False
            )

            predicted_row1 = ft.Row(controls=[
                self.predicted_encoding_text,
                predicted_encoding_hint_icon,
            ], vertical_alignment=ft.CrossAxisAlignment.START)

            predicted_row2 = ft.Row(controls=[
                predicted_encoding_hint,
            ], vertical_alignment=ft.CrossAxisAlignment.START)

            predicted_encoding_container1 = ft.Container(
                content=predicted_row1,
                margin=ft.margin.symmetric(0, 20),
                padding=ft.padding.only(top=10),
            )
            predicted_encoding_container2 = ft.Container(
                content=predicted_row2,
                margin=ft.margin.symmetric(0, 20),
                padding=ft.padding.only(bottom=10, left=20),
            )

            # DROPDOWN & CONVERT
            available_encodings_dropdown = ft.Dropdown(
                options=[*[ft.dropdown.Option(x) for x in encodings]],
            )
            available_encodings_dropdown.value = 'UTF-8-SIG'

            available_encodings_container = ft.Container(
                content=available_encodings_dropdown,
            )

            convert_button = ft.ElevatedButton(
                'Convert file',
            )

            convert_row2 = ft.Row(controls=[
                available_encodings_container,
                convert_button,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

            convert_row1 = ft.Row(controls=[
                ft.Text('Choose destination encoding', size=16)
            ])

            convert_column = ft.Column(controls=[
                convert_row1,
                convert_row2,
            ])

            convert_container = ft.Container(
                content=convert_column,
                margin=ft.margin.symmetric(0, 20),
                padding=ft.padding.only(top=10),
            )

            # ADD MAIN COMPONENTS
            page.add(
                title_container,
                fu_container,
                ft.Column(controls=[
                    predicted_encoding_container1,
                    predicted_encoding_container2,
                ]),
                convert_container,
            )

        build_app()

    def start(self):
        ft.app(target=self.main_flet)


if __name__ == '__main__':
    main = Main()
    main.start()


