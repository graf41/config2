# test_visualizer.py
import unittest
from unittest.mock import patch
import visualizer
from graphviz import Digraph
import subprocess  # Добавлен импорт subprocess

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
        self.assertIn('digraph {', dot.source)
        self.assertIn('commit1', dot.source)
        self.assertIn('commit2', dot.source)
        self.assertIn('commit2 -> commit1', dot.source)  # Исправлено на 'commit2 -> commit1'

    @patch('visualizer.load_config')
    @patch('visualizer.get_commits')
    @patch('visualizer.build_dependency_graph')
    @patch('visualizer.generate_graphviz')
    @patch('visualizer.os.path.isfile')
    def test_main_success(self, mock_isfile, mock_generate_graphviz, mock_build_dependency_graph, mock_get_commits, mock_load_config):
        # Настраиваем моки
        mock_load_config.return_value = {
            'graphviz_path': '/opt/homebrew/bin/dot',  # Обновите путь согласно вашей системе
            'repo_path': '/fake/repo/path',
            'output_image': 'dependency_graph.png'
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
            # Запускаем main
            with patch('builtins.print') as mock_print:
                visualizer.main()
                # Проверяем, что print вызван с успешным сообщением
                mock_print.assert_any_call("Граф зависимостей успешно создан и сохранен.")
                # Проверяем, что render был вызван с правильными аргументами
                mock_render.assert_called_once_with(filename='dependency_graph.png', cleanup=True)

    @patch('visualizer.subprocess.run')
    def test_get_commits_git_error(self, mock_run):
        # Мокаем ошибку при выполнении git команды
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd='git log', stderr='fatal: not a git repository')

        commits = visualizer.get_commits('/fake/repo/path')
        self.assertEqual(commits, [])

if __name__ == '__main__':
    unittest.main()
