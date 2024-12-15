# visualizer.py
import yaml
import subprocess
import os
import argparse
from graphviz import Digraph
import shutil  # Для поиска 'dot'


# --------------------------
# Конфигурация и загрузка
# --------------------------
def load_config(config_path):
    """
    Загружает конфигурацию из YAML-файла.
    Если путь к Graphviz не указан или неверен, пытается найти 'dot' автоматически.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    graphviz_path = config.get('graphviz_path')
    if not graphviz_path or not os.path.isfile(graphviz_path):
        graphviz_path = shutil.which('dot')
        if graphviz_path:
            print(f"Graphviz 'dot' найден по пути: {graphviz_path}.")
            config['graphviz_path'] = graphviz_path
        else:
            print("Graphviz 'dot' не найден. Пожалуйста, установите Graphviz.")
            exit(1)

    return config


# --------------------------
# Работа с Git
# --------------------------
def get_commits(repo_path):
    """
    Возвращает список коммитов с их родительскими коммитами и сообщениями.
    """
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'log', '--pretty=format:%H|%P|%s'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 2)
            if len(parts) < 3:
                print(f"Некорректная строка коммита: {line}")
                continue  # Пропускаем некорректные строки
            commit_hash, parents, message = parts
            parent_hashes = parents.split() if parents else []
            commits.append({
                'hash': commit_hash,
                'parents': parent_hashes,
                'message': message
            })
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении git: {e.stderr}")
        return []
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return []


def build_dependency_graph(commits):
    """
    Строит граф зависимостей из списка коммитов.
    Возвращает словарь, где ключи — хеши коммитов, а значения — словари с родителями и сообщениями.
    """
    graph = {}
    for commit in commits:
        graph[commit['hash']] = {
            'parents': commit['parents'],
            'message': commit['message']
        }
    return graph


# --------------------------
# Генерация графа
# --------------------------
def generate_graphviz(graph):
    """
    Генерирует объект Graphviz Digraph из графа зависимостей.
    """
    dot = Digraph(comment='Dependency Graph', format='png')
    # Добавляем узлы
    for commit_hash, data in graph.items():
        label = f"{commit_hash[:7]}\n{data['message']}"
        dot.node(commit_hash, label)
    # Добавляем ребра
    for commit_hash, data in graph.items():
        for parent in data['parents']:
            dot.edge(commit_hash, parent)
    return dot


# --------------------------
# Главная функция
# --------------------------
def main():
    parser = argparse.ArgumentParser(description='Visualize Git commit dependencies.')
    parser.add_argument('-c', '--config', default='config.yaml', help='Path to config file')
    args = parser.parse_args()

    # Загрузка конфигурации
    config = load_config(args.config)
    graphviz_path = config.get('graphviz_path')
    repo_path = config.get('repo_path')
    output_image = config.get('output_image')

    # Проверка наличия Graphviz (не требуется, так как уже проверено в load_config)

    # Получение коммитов
    commits = get_commits(repo_path)
    if not commits:
        print("No commits found или не удалось получить коммиты.")
        return

    # Построение графа зависимостей
    graph = build_dependency_graph(commits)

    # Генерация Graphviz-диаграммы
    dot = generate_graphviz(graph)

    # Сохранение графа в файл
    try:
        # Указываем путь к исполняемому файлу Graphviz
        dot.engine = 'dot'  # По умолчанию 'dot', можно изменить при необходимости
        dot.render(filename=output_image, cleanup=True)
        print("Граф зависимостей успешно создан и сохранен.")
    except Exception as e:
        print(f"Ошибка при сохранении графа: {e}")


if __name__ == "__main__":
    main()
