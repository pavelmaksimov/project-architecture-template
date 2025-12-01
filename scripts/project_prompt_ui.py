from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Set

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static, Tree


class FileTree(Tree[Path]):
    """Дерево файлов с интерактивными чекбоксами."""

    def __init__(self, **kwargs) -> None:
        super().__init__("Выберите директорию", **kwargs)
        self.selected_paths: Set[Path] = set()
        self.path_to_node: Dict[Path, Tree.Node[Path]] = {}

    def load_directory(self, path: Path) -> None:
        """Загружает структуру директории в дерево."""
        self.clear()
        self.selected_paths.clear()
        self.path_to_node.clear()

        if not path.is_dir():
            return

        self.root.expand()
        self.root.label = f"📁 {path.name}"
        self.root.data = path

        self._add_directory(self.root, path)

    def _add_directory(self, parent_node: Tree.Node[Path], directory: Path) -> None:
        """Рекурсивно добавляет файлы и директории в дерево."""
        try:
            # Сортируем: сначала директории, потом файлы
            entries = sorted(
                directory.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )

            for entry in entries:
                # Пропускаем скрытые системные файлы
                if entry.name.startswith('.') or entry.name == '__pycache__':
                    continue

                if entry.is_dir():
                    node = parent_node.add(f"📁 {entry.name}", data=entry)
                    self.path_to_node[entry] = node
                    self._add_directory(node, entry)
                else:
                    # Показываем только текстовые файлы
                    if self._is_text_file(entry):
                        node = parent_node.add(f"📄 {entry.name}", data=entry)
                        self.path_to_node[entry] = node
        except PermissionError:
            parent_node.add("🔒 Нет доступа", data=directory)
        except Exception as e:
            parent_node.add(f"❌ Ошибка: {e}", data=directory)

    def _is_text_file(self, path: Path) -> bool:
        """Проверяет, является ли файл текстовым."""
        # Проверка по расширению
        text_extensions = {
            '.txt', '.py', '.md', '.json', '.yaml', '.yml', '.xml', '.html',
            '.css', '.js', '.ts', '.sh', '.ini', '.cfg', '.conf', '.log',
            '.cpp', '.c', '.h', '.hpp', '.java', '.php', '.rb', '.go', '.rs'
        }

        if path.suffix.lower() in text_extensions:
            return True

        # Проверка по содержимому
        try:
            with open(path, 'rb') as f:
                chunk = f.read(8192)
                if b'\x00' in chunk:
                    return False
                printable = sum(1 for b in chunk if 32 <= b <= 126 or b in (9, 10, 13))
                return printable / len(chunk) > 0.9 if chunk else True
        except:
            return False

    def toggle_node(self, node: Tree.Node[Path]) -> None:
        """Переключает состояние выбора узла (Enter)."""
        if node.data is None:
            return

        path = node.data

        # Переключаем текущий узел
        if path in self.selected_paths:
            self.selected_paths.remove(path)
        else:
            self.selected_paths.add(path)

        self.refresh_node(node)

        # Если директория — обновляем всех детей рекурсивно
        if path.is_dir():
            self._update_children(node, path in self.selected_paths)

    def _update_children(self, node: Tree.Node[Path], selected: bool) -> None:
        """Рекурсивно обновляет состояние дочерних узлов."""
        for child in node.children:
            if child.data is None:
                continue

            path = child.data
            if selected:
                self.selected_paths.add(path)
            else:
                self.selected_paths.discard(path)

            self.refresh_node(child)

            if path.is_dir():
                self._update_children(child, selected)

    def refresh_node(self, node: Tree.Node[Path]) -> None:
        """Обновляет визуальное отображение узла (галочка)."""
        if node.data is None:
            return

        path = node.data
        is_selected = path in self.selected_paths

        prefix = "✅ " if is_selected else "⬜ "
        original_label = node.label.plain

        # Убираем старый префикс
        if original_label.startswith(('✅ ', '⬜ ')):
            original_label = original_label[2:]

        node.label = prefix + original_label

    def get_selected_files(self) -> List[Path]:
        """Возвращает список выбранных файлов (исключая директории)."""
        return [p for p in self.selected_paths if p.is_file()]


class FileCollectorScreen(Screen):
    """Главный экран приложения."""

    BINDINGS = [
        Binding("q", "quit", "Выход"),
        Binding("ctrl+d", "select_directory", "Выбрать директорию"),
        Binding("ctrl+s", "collect_files", "Собрать файлы"),
        Binding("enter", "toggle_node", "Выбрать/Отменить"),
        Binding("space", "toggle_expand", "Раскрыть/Свернуть"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.current_directory: Optional[Path] = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Horizontal(
                Button("📂 Выбрать директорию", id="select_dir", variant="primary"),
                Button("📦 Собрать файлы", id="collect", variant="success"),
                classes="button-bar"
            ),
            Static("Директория не выбрана", id="current_dir"),
            FileTree(id="file_tree"),
            VerticalScroll(
                Static("Готово к работе", id="status"),
                classes="status-panel"
            ),
            classes="main-container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Инициализация после монтирования."""
        self.query_one(FileTree).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Обработка нажатий кнопок мыши."""
        if event.button.id == "select_dir":
            self.action_select_directory()
        elif event.button.id == "collect":
            self.action_collect_files()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Обработка клика по узлу дерева."""
        tree = self.query_one(FileTree)
        tree.toggle_node(event.node)
        self.update_status()

    def action_toggle_node(self) -> None:
        """Действие: переключить узел под курсором (Enter)."""
        tree = self.query_one(FileTree)
        node = tree.cursor_node
        if node:
            tree.toggle_node(node)
            self.update_status()

    def action_toggle_expand(self) -> None:
        """Действие: раскрыть/свернуть узел (Space)."""
        tree = self.query_one(FileTree)
        node = tree.cursor_node
        if node:
            node.toggle()

    def action_quit(self) -> None:  # <-- ДОБАВЛЕН ЭТОТ МЕТОД
        """Выход из приложения."""
        self.app.exit()  # или self.app.quit() - оба работают

    def update_status(self) -> None:
        """Обновляет статус с количеством выбранных файлов."""
        tree = self.query_one(FileTree)
        selected_files = tree.get_selected_files()
        count = len(selected_files)

        status = f"📊 Выбрано файлов: {count}"
        if count > 0:
            total_size = sum(f.stat().st_size for f in selected_files)
            status += f" (размер: {total_size / 1024:.1f} KB)"

        self.query_one("#status", Static).update(status)

    def action_select_directory(self) -> None:
        """Действие: выбрать директорию."""
        # Для простоты загружаем текущую директорию
        # В продакшене добавьте textual-input-filepath
        self.load_directory(Path.cwd())

    def load_directory(self, path: Path) -> None:
        """Загружает директорию и обновляет интерфейс."""
        if not path.is_dir():
            self.show_error(f"Не является директорией: {path}")
            return

        try:
            tree = self.query_one(FileTree)
            tree.load_directory(path)
            self.current_directory = path.absolute()
            self.query_one("#current_dir", Static).update(
                f"📂 Текущая директория: {self.current_directory}"
            )
            self.update_status()
        except Exception as e:
            self.show_error(f"Ошибка загрузки: {e}")

    def action_collect_files(self) -> None:
        """Действие: собрать выбранные файлы в один."""
        if not self.current_directory:
            self.show_error("❌ Сначала выберите директорию")
            return

        tree = self.query_one(FileTree)
        selected_files = tree.get_selected_files()

        if not selected_files:
            self.show_error("❌ Не выбраны файлы для сборки")
            return

        # Генерируем уникальное имя выходного файла
        timestamp = os.urandom(4).hex()
        output_path = self.current_directory / f"collected_{timestamp}.txt"

        try:
            self.collect_files_to_single_file(selected_files, output_path)
            self.show_success(
                f"✅ Собрано {len(selected_files)} файлов → {output_path.name}\n"
                f"   Полный путь: {output_path}"
            )
        except Exception as e:
            self.show_error(f"❌ Ошибка сборки: {e}")

    def collect_files_to_single_file(
        self, files: List[Path], output_path: Path
    ) -> None:
        """Собирает содержимое файлов в один с разделителями."""
        with open(output_path, 'w', encoding='utf-8') as outfile:
            # Заголовок
            outfile.write("=" * 80 + "\n")
            outfile.write("📦 СОБРАННЫЙ ФАЙЛ\n")
            outfile.write("=" * 80 + "\n")
            outfile.write(f"📂 Источник: {self.current_directory}\n")
            outfile.write(f"📊 Файлов: {len(files)}\n")
            outfile.write("=" * 80 + "\n\n")

            # Содержимое файлов
            for file_path in sorted(files):
                try:
                    relative_path = file_path.relative_to(self.current_directory)
                    outfile.write(f"\n{'=' * 80}\n")
                    outfile.write(f"📄 {relative_path}\n")
                    outfile.write(f"{'=' * 80}\n")

                    # Читаем и пишем содержимое
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)

                    outfile.write("\n")

                except Exception as e:
                    outfile.write(f"\n❌ Ошибка чтения {file_path}: {e}\n")

    def show_error(self, message: str) -> None:
        """Показывает сообщение об ошибке."""
        self.query_one("#status", Static).update(message)

    def show_success(self, message: str) -> None:
        """Показывает сообщение об успехе."""
        self.query_one("#status", Static).update(message)


class FileCollectorApp(App):
    """Главное приложение."""

    BINDINGS = [  # <-- ДОБАВЛЕНЫ ГЛОБАЛЬНЫЕ ПРИВЯЗКИ
        Binding("q", "quit", "Выход", show=True),
    ]

    CSS = """
    .main-container {
        height: 100vh;
    }

    .button-bar {
        height: auto;
        dock: top;
        padding: 1;
        background: $surface;
        align: center middle;
    }

    .button-bar Button {
        margin-right: 2;
    }

    #current_dir {
        height: auto;
        padding: 1 2;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    FileTree {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    .status-panel {
        height: auto;
        max-height: 6;
        border: solid $success;
        padding: 1 2;
        background: $surface;
    }

    Static {
        color: $text;
    }

    /* Стили для узлов дерева */
    Tree > .tree--label {
        padding: 0 1;
    }

    Tree > .tree--cursor {
        background: $primary;
        color: $text;
    }
    """

    def __init__(self) -> None:
        super().__init__()

    def on_mount(self) -> None:
        """Запускает главный экран."""
        self.push_screen(FileCollectorScreen())

    def action_quit(self) -> None:  # <-- ДОБАВЛЕН ГЛОБАЛЬНЫЙ МЕТОД
        """Выход из приложения."""
        self.exit()


if __name__ == "__main__":
    app = FileCollectorApp()
    app.run()