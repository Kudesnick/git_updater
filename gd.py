# -*- coding: utf-8 -*-

from abc import abstractmethod
import gitlab # pip install python-gitlab
from atlassian.bitbucket import Cloud # pip install atlassian-python-api
import yaml # pip install pyyaml
from pathlib import Path
import json
import subprocess
from functools import reduce


class Replacer(dict):
    def __init__(self, val: str = None):
        if val != None:
            super().__init__({tuple(i.split(':',1)) for i in val.split(',')})
        else:
            super().__init__()

    def repl(self, pattern: str):
        return self.get(pattern, pattern)

class Repo(list):
    def __init__(self, args):
        self.__args = args
        self.__repl = Replacer(args.replace_proj)
        super().__init__()

    def append(self, proj: str, name: str, repo: str, desc: str):
        super().append({'Project name': proj, 'Repo name': name, 'Repo url': repo, 'Repo description': desc})

    def json(self) -> str:
        self.sort(key=lambda item: item['Project name'])
        return '[{}]'.format(',\r'.join([json.dumps(i, ensure_ascii = False) for i in self]))

    def yml(self, base: Path):
        def map_func(name):
            return {'name': name, 'expanded': False, 'children': [{'name': i['Repo name'], 'favorite': False, 'git': True, 'path': str(base.joinpath(name).joinpath(i['Repo name'])), 'expanded': False} for i in self if i['Project name'] == name]}

        return list(map(map_func, set([i['Project name'] for i in self])))

    def item_proc(self, addr, group, repo, repo_desc):
        repo_url=f'{addr}/{repo}.git'
        self.append(self.__repl.repl(group), repo, repo_url, repo_desc)
        if self.__args.no_update: return

        proj_path = self.__args.base_path.joinpath(self.__repl.repl(group))
        if not proj_path.is_dir():
            proj_path.mkdir()

        repo_path = proj_path.joinpath(repo)
        if not repo_path.is_dir():
            print(f'cloning "{repo}"', end = ' ', flush = True)
            res = subprocess.call(['git', 'clone', '--recursive', repo_url], cwd = str(proj_path), stderr = subprocess.DEVNULL)
            if res == 0:
                print('complete')
            else:
                print(f'not complete with code {res}')
        else:
            if repo_path.joinpath('.git').is_dir():
                print(f'updating "{repo}"', end = ' ', flush = True)
                res = subprocess.call(['git', 'fetch', '--progress', '--recurse-submodules=yes', 'origin'], cwd = str(repo_path), stderr = subprocess.DEVNULL)
                if res == 0:
                    print('complete')
                else:
                    print(f'not complete with code {res}')
            else:
                print(f'Error!!! Path "{repo}" is found but it is not git repository (.git not found).')

    @abstractmethod
    def repo_iterator(self):
        pass

    def update(self):
        if self.__args.win_cred:
            subprocess.call(['git', 'config', '--global', 'credential.helper', 'wincred'])

        for _ in range(self.__args.try_cnt):
            self.clear()

            try:
                self.repo_iterator()

            except Exception as e:
                print(f'Exception: {str(e)}')
            else:
                if self.__args.json != None:
                    self.__args.json.write(self.json())
                    self.__args.json.close()

                if self.__args.yml != None:
                    yml = None
                    with open(self.__args.yml, 'r') as f:
                        yml = yaml.safe_load(f)
                    if yml != None:
                        yml['structure'].append({'name': self.__args.yml_group, 'expanded': False, 'children': self.yml(self.__args.base_path)})
                        with open(self.__args.yml, 'w') as f:
                            yaml.dump(yml, f)

                print('Complete.')

                break
        else:
            print('Not complete. Too many exceptions.')

class RepoBB(Repo):
    def __init__(self, args):
        self.__cloud = Cloud(url='https://api.bitbucket.org', username = args.username, password = args.app_key)
        super().__init__(args)

    def repo_iterator(self):
        for wspace in self.__cloud.workspaces.each():
            print(f'Workspace name "{wspace.name}" has {len(list(wspace.projects.each()))} projects')
            for proj in wspace.projects.each():
                for repo in proj.repositories.each():
                    self.item_proc(f'https://bitbucket.org/{wspace.slug}',
                        proj.name,
                        repo.slug,
                        repo.description)

class RepoGL(Repo):
    def __init__(self, args):
        self.__cloud = gitlab.Gitlab(args.server_url, args.token)
        super().__init__(args)
    
    def repo_iterator(self):
        for repo in self.__cloud.projects.list(all = True):
            self.item_proc(f"{args.server_url}/{repo.namespace['path']}",
                repo.namespace['path'],
                repo.path,
                repo.description)

if __name__ == "__main__":
    from argparse import ArgumentParser, FileType, ArgumentTypeError
    import sys

    parser = ArgumentParser(prog='Git updater',
        description='''Клонирует на локальную машину все доступные из аккаунта пользователя
репозитории, формирует json список репозиториев, отсортированный по проектам, загружает список
репозиториев в дерево конфигурации smartgit с сортировкой по проектам.''')

    parser.add_argument(
        '--json',
        type = FileType('w', encoding = 'utf-8'),
        default = None, metavar = '<filename.json>',
        help = '''Сформировать и записать в файл json информацию обо всех найденных репозиториях.
Каждый элемнт списка включает в себя: название проекта, название репозитория, путь к репозиторию на
сервере, описание репозитория.''')

    parser.add_argument(
        '--yml',
        type = Path,
        default = None,
        metavar = '<c:\\Users\\<username>\\AppData\\Roaming\\syntevo\\SmartGit\\21.1\\repository-grouping.yml>',
        help = '''Путь к файлу конфигурации Smartgit. Файл, в котором будут созданы группы
(по имени проекта), содержащие найденные репозитории. Все созданные группы будут помещены в
родительскую группу.''')

    parser.add_argument(
        '--yml-group',
        required = '--yml' in sys.argv, type = str,
        default = None, metavar = '<groupname>',
        help = '''Название родительской группы репозиториев в файле конфигурации Smartgit.''')

    parser.add_argument(
        '--base-path',
        required = '--yml' in sys.argv or '--no-update' not in sys.argv, type = Path,
        metavar = '<dirname>',
        help = '''Прописываем абсолютный путь к папке, в которую будут клонированы найденные
репозитории. В этой папке будут созданы подпапки по именам проектов и в них будут находиться папки
с репозиториями. Если репозитории там уже есть, то они будут обновлены с сервера.''')

    subparsers = parser.add_subparsers()

    # bitbucket cloud ->
    parser_bb_cloud = subparsers.add_parser('bitbucket-cloud',
        help = 'Работаем с облачным сервером Bitbucket.')

    parser_bb_cloud.add_argument(
        '--username',
        required = True, type = str,
        metavar = '<username>',
        help = '''Логин (не почтовый адрес).''')

    parser_bb_cloud.add_argument(
    '--app-key',
    required = True, type = str,
    metavar = '<keyvalue>',
    help = '''Персональный ключ доступа (access token). Для создания ключа зайдите в аккаунт
Bitbucket по адресу: https://bitbucket.org/account/settings/app-passwords/new. Установите для ключа
разрешения на чтения Accounts, Workspace membership, Projects, Repositories. Подробнее про
авторизацию по ключу см. справку Atlassian:
https://support.atlassian.com/bitbucket-cloud/docs/app-passwords''')

    def bb_update(args):
        repo_list = RepoBB(args)
        repo_list.update()

    parser_bb_cloud.set_defaults(func = bb_update)
    # bitbucket cloud <-

    # gitlab server ->
    parser_gl_server = subparsers.add_parser('gitlab-server', help = 'Работаем с сервером Gitlab.')

    parser_gl_server.add_argument(
        '--server-url',
        required = True, type = str,
        metavar = '<http://<servername>>',
        help = '''Путь к серверу, с которого запрашиваем репозитории.''')

    parser_gl_server.add_argument(
        '--token',
        required = True, type = str,
        help = '''Указываем персональный ключ доступа (access token). Для создания ключа зайдите в
аккаунт Gitlab по адресу https://<servername>/-/profile/personal_access_tokens. Установите для ключа
разрешения read_api и read_repository.''')

    def gl_update(args):
        repo_list = RepoGL(args)
        repo_list.update()

    parser_gl_server.set_defaults(func = gl_update)
    # gitlab server <-

    parser.add_argument(
        '--no-update',
        action='store_true',
        help = '''Не обновляем репозитории. Только получаем список репозиториев и сохраняем его в
json файл или конфигурацию Smartgit.''')

    parser.add_argument(
        '--win-cred',
        action='store_false',
        help = '''Изменить хранилище паролей git на системный менеджер учетных записей Windows.
Выполняет команду "git config --global credential.helper wincred". Это позволяет избежать запроса
логина и пароля при обновлении каждого репозитория, если авторизация в git была настроена
некорректно.''')

    parser.add_argument(
        '--try-cnt',
        default = 50, type = int,
        metavar = '<int>',
        help = '''Количество попыток успешного завершения скрипта. Актуально при большом количестве
репозиториев или плохой связи.'''
    )

    def replace_proj(val: str):
        for i in val.split(','):
            if len(i.split(':',1)) < 2:
                raise ArgumentTypeError(f'Неверный синтаксис --replace-proj "{val}". Ожидается строка вида:  "orig-name1:alias1,orig-name2:alias".')
        return val

    parser.add_argument(
        '--replace-proj',
        type = replace_proj,
        metavar = '<First origin name:alias1,Second name:alias2>',
        help = '''Список имен проектов, которые будут переименованы в локальной версии. Синтаксис:
"orig-name1:alias1,Untitled project:noproject". Оригинальные и новые значения разделены между собой
двоеточием (без пробелов), пары значений отделены друг от друга запятыми (без пробелов). Позволяет
избежать проблем в случаях, когда имена проектов содержат недопустимые символы
(пробелы, например).''')

    args = parser.parse_args()
    args.func(args)
