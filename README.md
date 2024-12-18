# Инструмент командной строки для визуализации графа зависимостей Git-репозитория

# Описание проекта
## Задание №2:
**Разработан инструмент командной строки для построения графа зависимостей коммитов Git-репозитория с учетом транзитивных зависимостей. Визуализация выполняется с помощью Graphviz. Результат сохраняется в виде PNG-файла, а успешное выполнение сопровождается сообщением.**

## Основные возможности

Построение графа зависимостей коммитов с отображением сообщений коммитов в узлах.

Поддержка транзитивных зависимостей.

Настройка через YAML-конфигурационный файл.

Результат сохраняется в формате PNG.

Полное покрытие функциональности модульными тестами.

## Требования

Конфигурационный файл имеет формат yaml и содержит:

•Путь к программе для визуализации графов.

•Путь к анализируемому репозиторию.

•Путь к файлу с изображением графа зависимостей.

**Конфигурационный файл должен быть в формате YAML и содержать следующие параметры:**
```
# config.yaml
graphviz_path: "/usr/local/bin/dot"  # Путь к исполняемому файлу Graphviz (dot)
repo_path: "/Users/egor/Desktop/ВУЗ/2 курс/конфиг/config2"  # Путь к анализируемому Git-репозиторию
output_image: "dependency_graph.png"  # Путь к файлу для сохранения графа
```
## Реализация функций
### **Функция load_config(config_path)**

Загружает конфигурацию из YAML-файла, проверяет путь к Graphviz и, если путь не указан, ищет исполняемый файл dot в системе.
```
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)
```
Загружает YAML-файл и сохраняет его как словарь config.
```
graphviz_path = config.get('graphviz_path')
if not graphviz_path or not os.path.isfile(graphviz_path):
    graphviz_path = shutil.which('dot')
```
Проверяет, указан ли путь к Graphviz (graphviz_path). Если нет, использует shutil.which для поиска программы dot в системе.
```
if graphviz_path:
    print(f"Graphviz 'dot' найден по пути: {graphviz_path}.")
    config['graphviz_path'] = graphviz_path
else:
    print("Graphviz 'dot' не найден. Пожалуйста, установите Graphviz.")
    exit(1)
```
Если Graphviz найден, обновляет конфигурацию. Если нет, выводит сообщение об ошибке и завершает программу.

### **Функция get_commits(repo_path)**

Получает список коммитов из Git-репозитория с их хешами, родителями и сообщениями.
```
result = subprocess.run(
    ['git', '-C', repo_path, 'log', '--pretty=format:%H|%P|%s'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    check=True
)
```
Выполняет команду git log для получения коммитов в формате:
```
хеш_коммита | родители | сообщение
```
Результат сохраняется в result.stdout.
```
for line in result.stdout.strip().split('\n'):
    parts = line.split('|', 2)
```
Каждая строка результата делится на три части: хеш, родительские коммиты и сообщение.
```
parent_hashes = parents.split() if parents else []
commits.append({
    'hash': commit_hash,
    'parents': parent_hashes,
    'message': message
})
```
Сохраняет данные коммита (хеш, родители, сообщение) в список commits.


### **Функция build_dependency_graph(commits)**

Создает граф зависимостей, связывая каждый коммит с его родителями.
```
for commit in commits:
    graph[commit['hash']] = {
        'parents': commit['parents'],
        'message': commit['message']
    }
```
Строит словарь, где:
Ключ — хеш коммита.
Значение — словарь с родительскими коммитами (parents) и сообщением (message).
Результат функции:
Возвращает словарь графа зависимостей.

### **Функция generate_graphviz(graph)**

Генерирует граф зависимостей в формате Graphviz (диаграммы).
```
dot = Digraph(comment='Dependency Graph', format='png')
```
Создает объект Graphviz Digraph для построения графа.
```
for commit_hash, data in graph.items():
    label = f"{commit_hash[:7]}\n{data['message']}"
    dot.node(commit_hash, label)
```
Для каждого коммита добавляет узел с коротким хешем и сообщением коммита.
```
for commit_hash, data in graph.items():
    for parent in data['parents']:
        dot.edge(commit_hash, parent)
```
Добавляет ребра между коммитом и его родителями.

### **Функция main()**

Оркестрирует выполнение программы: загружает конфигурацию, получает коммиты, строит граф зависимостей и сохраняет изображение.
```
parser = argparse.ArgumentParser(description='Visualize Git commit dependencies.')
parser.add_argument('-c', '--config', default='config.yaml', help='Path to config file')
args = parser.parse_args()
```
Обрабатывает аргументы командной строки.

```
config = load_config(args.config)
```
Загружает конфигурацию.

```
commits = get_commits(repo_path)
if not commits:
    print("No commits found или не удалось получить коммиты.")
    return
```
Получает коммиты из репозитория и проверяет, что они найдены.
```
graph = build_dependency_graph(commits)
dot = generate_graphviz(graph)
dot.render(filename=output_image, cleanup=True)
```
Строит граф зависимостей и сохраняет его как изображение.
```
print("Граф зависимостей успешно создан и сохранен.")
```
### Пример последовательности работы программы:

Загружается конфигурация из файла config.yaml.

Проверяется путь к программе Graphviz.

Получаются коммиты из Git-репозитория.

Строится граф зависимостей на основе коммитов.

Генерируется изображение графа с использованием Graphviz и сохраняется в формате png.

Выводится сообщение об успешном выполнении.

### Команда для запуска

Запуск выполняется через командную строку:
```
python visualizer.py --config config.yaml
```

<img width="679" alt="image" src="https://github.com/user-attachments/assets/e8c71788-cedd-4631-b1ec-d74e129925d7" />

### Результат
В директории  egor@MacBook-Pro--Egor config2 будет создан файл .png с визуализацией графа зависимостей коммитов.
В терминале появится сообщение:
```
...Граф зависимостей успешно создан и сохранен.
```
Граф зависимостей успешно построен и сохранен в 'egor@MacBook-Pro--Egor config2'.

## Архитектура проекта

**Основные файлы**
**visualizer.py: основной файл с логикой построения графа зависимостей.**
**test_vizualizer.py: основной файл покрытия тестами**
**config.yaml: пример конфигурационного файла.**

### Покрытие тестами
```
import unittest
from unittest.mock import patch
import visualizer
from graphviz import Digraph

class TestGitDependencyVisualizer(unittest.TestCase):
    @patch('visualizer.subprocess.run')
    def test_get_commits(self, mock_run):
        # Мокаем вывод команды git log
        mock_run.return_value.stdout = "commit1||Initial commit\ncommit2|commit1|Second commit"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0

        commits = visualizer.get_commits('/fake/repo/path')
        expected = [
            {'hash': 'commit1', 'parents': [], 'message': 'Initial commit'},
            {'hash': 'commit2', 'parents': ['commit1'], 'message': 'Second commit'}
        ]
        self.assertEqual(commits, expected)

    def test_build_dependency_graph(self):
        commits = [
            {'hash': 'commit1', 'parents': [], 'message': 'Initial commit'},
            {'hash': 'commit2', 'parents': ['commit1'], 'message': 'Second commit'}
        ]
        graph = visualizer.build_dependency_graph(commits)
        expected = {
            'commit1': {'parents': [], 'message': 'Initial commit'},
            'commit2': {'parents': ['commit1'], 'message': 'Second commit'}
        }
        self.assertEqual(graph, expected)

    def test_generate_graphviz(self):
        graph = {
            'commit1': {'parents': [], 'message': 'Initial commit'},
            'commit2': {'parents': ['commit1'], 'message': 'Second commit'}
        }
        dot = visualizer.generate_graphviz(graph)
        self.assertIsInstance(dot, Digraph)
        self.assertIn('commit2 -> commit1', dot.source)

    @patch('visualizer.load_config')
    @patch('visualizer.get_commits')
    @patch('visualizer.build_dependency_graph')
    @patch('visualizer.generate_graphviz')
    @patch('visualizer.os.path.isfile')
    def test_main_success(self, mock_isfile, mock_generate_graphviz, mock_build_dependency_graph, mock_get_commits, mock_load_config):
        # Настраиваем моки
        mock_load_config.return_value = {
            'graphviz_path': '/usr/local/bin/dot',
            'repo_path': '/fake/repo/path',
            'output_image': 'test_dependency_graph.png'
        }
        mock_isfile.return_value = True
        mock_get_commits.return_value = [
            {'hash': 'commit1', 'parents': [], 'message': 'Initial commit'},
            {'hash': 'commit2', 'parents': ['commit1'], 'message': 'Second commit'}
        ]
        mock_build_dependency_graph.return_value = {
            'commit1': {'parents': [], 'message': 'Initial commit'},
            'commit2': {'parents': ['commit1'], 'message': 'Second commit'}
        }
        mock_generate_graphviz.return_value = Digraph()

        with patch('visualizer.Digraph.render') as mock_render:
            visualizer.main()
            mock_render.assert_called_once_with(filename='test_dependency_graph.png', cleanup=True)

if __name__ == '__main__':
    unittest.main()

```
Проект содержит тесты для всех функций:

Тесты парсинга Git-репозитория.

Тесты построения графа зависимостей.

Тесты сохранения графа в формате PNG.

<img width="635" alt="Снимок экрана 2024-12-18 в 11 05 41" src="https://github.com/user-attachments/assets/cff35ce2-4c3b-4798-92c5-c2979da82e21" />

Запуск тестов выполняется с помощью unittest:
```
python test_visualizer.py
```

<img width="679" alt="image" src="https://github.com/user-attachments/assets/6d6dd2ac-668f-40a0-aa3d-28e54b3142d0" />


Заключение

Все функции протестированы, а результат сохраняется в удобном формате PNG для последующего анализа.
