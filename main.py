from typing import Optional
from pathlib import Path

import flet as ft

from src.engine_handle import predict, convert_file
from src.encodings import encodings


class Main:
    def __init__(self):
        self.page = None
        self.predicted_encoding: str = None
        self.predicted_encoding_text: Optional[ft.Text] = None
        self.file_path: Optional[ft.Text] = None
        self.convert_button: Optional[ft.ElevatedButton] = None
        self.result_encoding: str = 'UTF-8'
        self.result_text: Optional[ft.Text] = None

    def main_flet(self, page: ft.Page):
        self.page = page

        def set_predicted_encoding_text(encoding: str, error: bool = False):
            if error:
                self.predicted_encoding_text.value = encoding.upper()
            else:
                self.predicted_encoding_text.value = f'Predicted encoding of the original file: {encoding.upper()}'

            page.update()

        def set_predicted_encoding_text_default():
            set_predicted_encoding_text('INVALID FILE')
            page.update()

        def set_result_text(oknk: bool, filename: str, encoding: str, error: str = ''):
            if oknk:
                self.result_text.value = f'File {filename} was successfully encoded in {encoding}'
                self.result_text.color = ft.colors.GREEN
            else:
                self.result_text.value = f'There was error encoding file {filename} in {encoding}\nDetail: {error}'
                self.result_text.color = ft.colors.RED
            page.update()

        def validate_filepath_exists(path: str = None) -> Optional[Path]:
            if not path:
                set_predicted_encoding_text_default()

            path = Path(path)
            if not path.is_file() or not path.exists():
                set_predicted_encoding_text_default()
                path = None
                self.convert_button.disabled = True

            return path

        def handle_filepath_inserted(path: Path):
            """runs when we have a valid path to subtitle"""

            size = path.stat().st_size
            # limit to 100MB
            if size > 100 * 1024 * 1024:
                set_predicted_encoding_text(f'Filesize limit is 10MB', error=True)
                page.update()
                return

            try:
                self.predicted_encoding = predict(path)
            except Exception as e:
                set_predicted_encoding_text(f'{str(e)}', error=True)
                page.update()
                return

            # could not detetect encodig -> apps, music, etc...
            if not self.predicted_encoding:
                set_predicted_encoding_text(f'Could not detect encoding', error=True)
                page.update()
                return

            self.file_path.value = path
            set_predicted_encoding_text(self.predicted_encoding)

            self.convert_button.disabled = False

            page.update()

        def on_file_picker_dialog(e: ft.FilePickerResultEvent):
            """runs if the path is chosen from file explorer"""

            if not e.files:
                set_predicted_encoding_text_default()
                return

            file_info = e.files[0]
            subtitle_file_path = validate_filepath_exists(file_info.path)

            if subtitle_file_path:
                handle_filepath_inserted(subtitle_file_path)

            page.update()

        def on_path_value_change(e: ft.ControlEvent):
            """runs if value in text field changes"""

            subtitle_file_path = validate_filepath_exists(e.data)

            if subtitle_file_path:
                handle_filepath_inserted(subtitle_file_path)

            page.update()

        def on_hint_click(_):
            if predicted_encoding_hint.visible:
                predicted_encoding_hint.visible = False
                page.window_height = page.window_height - 90
            else:
                predicted_encoding_hint.visible = True
                page.window_height = page.window_height + 90
            page.update()

        def set_result_encoding(e: ft.ControlEvent):
            self.result_encoding = e.control.value

        def on_result_button_pressed(e: ft.ControlEvent):
            """runs when convert button is preesed"""

            filepath = Path(self.file_path.value)
            filename = filepath.name

            try:
                convert_file(
                    filepath,
                    self.predicted_encoding,
                    self.result_encoding,
                )
            except Exception as e:
                set_result_text(False, filename, self.result_encoding, str(e))
                return
            finally:
                self.convert_button.disabled = True

            set_result_text(True, filename, self.result_encoding)
            self.file_path.value = ''
            set_predicted_encoding_text('NO FILE CHOOSEN', error=True)


        # MAIN PROC
        page.window_width = 800
        page.window_height = 440

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
        self.predicted_encoding_text = ft.Text(size=16, color=ft.colors.YELLOW)
        set_predicted_encoding_text('NO FILE CHOSEN', error=True)
        predicted_encoding_hint_icon = ft.Container(
            content=ft.Icon(ft.icons.QUESTION_MARK_SHARP, size=20),
            on_hover=on_hint_click
        )

        # HINT
        predicted_encoding_hint_row = ft.Column(controls=[
            ft.Row(controls=[
                ft.Icon(ft.icons.FACT_CHECK),
                ft.Text('Unsupported characters will be removed when converting into ASCII'),
            ]),
            ft.Row(controls=[
                ft.Icon(ft.icons.FACT_CHECK),
                ft.Text('Precition is based on a hundred lines and depends on characters used in the file'),
            ]),
            ft.Row(controls=[
                ft.Icon(ft.icons.ALBUM),
                ft.Text('Globally accepted standard is the "UTF-8"'),
            ]),
            ft.Row(controls=[
                ft.Icon(ft.icons.ALBUM),
                ft.Text('For movie subtitles run on TVs I recommend the "UTF-8-SIG"')
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
            margin=ft.margin.symmetric(0, 25),
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
            on_change=set_result_encoding,
        )
        available_encodings_dropdown.value = 'UTF-8'

        available_encodings_container = ft.Container(
            content=available_encodings_dropdown,
        )

        self.convert_button = ft.ElevatedButton(
            'Convert file',
            disabled=True,
            on_click=on_result_button_pressed
        )

        convert_row2 = ft.Row(controls=[
            available_encodings_container,
            self.convert_button,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        convert_row1 = ft.Row(controls=[
            ft.Text('Choose encoding', size=16)
        ])

        convert_column = ft.Column(controls=[
            ft.Container(
                content=convert_row1,
                margin=ft.margin.only(left=5)
            ),
            convert_row2,
        ])

        convert_container = ft.Container(
            content=convert_column,
            margin=ft.margin.symmetric(0, 20),
            padding=ft.padding.only(top=10),
        )

        self.result_text = ft.Text('', size=16)
        result_container = ft.Container(
            content=self.result_text,
            margin=ft.margin.symmetric(0, 25)
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
            result_container,
        )

    def start(self):
        ft.app(target=self.main_flet)


if __name__ == '__main__':
    main = Main()
    main.start()


