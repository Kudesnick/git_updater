# gb.py

��������� �� ��������� ������ ��� ��������� �� �������� ������������ �����������, ��������� json ������ ������������, ��������������� �� ��������, ��������� ������ ������������ � ������ ������������ smartgit � ����������� �� ��������. ����� �������� � ��������� Bitbucket � Gitlab.

# �� �����

1. �������� � ������������� �� ssh.

# ��������� ������ �����������

## Bitbucket cloud api key

����� � ��������� �������� Bitbucket �� ������ https://bitbucket.org/account/settings/app-passwords/new � ������� ����, �������� ����� ��������� �������:

![image](bitbucket_app_key.png)

## Gitlab server api key

����� � ��������� �������� Gitlab �� ������ https://<����� �������>/profile/personal_access_tokens � ������� ����, �������� ����� ��������� �������:

![image](gitlab_app_key.png)

# ������� �������������

���������� ������������ � Bitbucket:

~~~
python gd.py --json bb_list.json --yml c:\Users\<winuser>\AppData\Roaming\syntevo\SmartGit\21.1\repository-grouping.yml --yml-group <groupname> --base-path C:\git\bb --replace-proj "Untitled project:noproj,test:test" bitbucket-cloud --username <username> --app-key <applicationkey>
~~~

���������� ������������ � Gitlab:

~~~
python gd.py --json gl_list.json --yml c:\Users\<winuser>\AppData\Roaming\syntevo\SmartGit\21.1\repository-grouping.yml --yml-group <groupname> --base-path C:\git\gl gitlab-server --server-url https://<servername> --token <applicationkey>
~~~

# �������������� �������

~~~
usage: Git updater [-h] [--json <filename.json>] [--yml <c:\Users\<username>\AppData\Roaming\syntevo\SmartGit\21.1\repository-grouping.yml>] [--yml-group <groupname>] --base-path <dirname> [--no-update] [--win-cred]
                   [--try-cnt <int>] [--replace-proj <First origin name:alias1,Second name:alias2>]
                   {bitbucket-cloud,gitlab-server} ...

��������� �� ��������� ������ ��� ��������� �� �������� ������������ �����������, ��������� json ������ ������������, ��������������� �� ��������, ��������� ������ ������������ � ������ ������������ smartgit � ����������� �� ��������.

positional arguments:
  {bitbucket-cloud,gitlab-server}
    bitbucket-cloud     �������� � �������� �������� Bitbucket.
    gitlab-server       �������� � �������� Gitlab.

optional arguments:
  -h, --help            show this help message and exit
  --json <filename.json>
                        ������������ � �������� � ���� json ���������� ��� ���� ��������� ������������. ������ ������ ������ �������� � ����: �������� �������, �������� �����������, ���� � ����������� �� �������, �������� �����������.
  --yml <c:\Users\<username>\AppData\Roaming\syntevo\SmartGit\21.1\repository-grouping.yml>
                        ���� � ����� ������������ Smartgit. ����, � ������� ����� ������� ������ (�� ����� �������), ���������� ��������� �����������. ��� ��������� ������ ����� �������� � ������������ ������.
  --yml-group <groupname>
                        �������� ������������ ������ ������������ � ����� ������������ Smartgit.
  --base-path <dirname>
                        ����������� ���������� ���� � �����, � ������� ����� ����������� ��������� �����������. � ���� ����� ����� ������� �������� �� ������ �������� � � ��� ����� ���������� ����� � �������������. ���� ����������� ��� ��� ����, �� ��� ����� ��������� � �������.
  --no-update           �� ��������� �����������. ������ �������� ������ ������������ � ��������� ��� � json ���� ��� ������������ Smartgit.
  --win-cred            �������� ��������� ������� git �� ��������� �������� ������� ������� Windows. ��������� ������� "git config --global credential.helper wincred". ��� ��������� �������� ������� ������ � ������ ��� ���������� ������� �����������, ���� ����������� � git ���� ��������� �����������.
  --try-cnt <int>       ���������� ������� ��������� ���������� �������. ��������� ��� ������� ���������� ������������ ��� ������ �����.
  --replace-proj <First origin name:alias1,Second name:alias2>
                        ������ ���� ��������, ������� ����� ������������� � ��������� ������. ���������: "orig-name1:alias1,Untitled project:noproject". ������������ � ����� �������� ��������� ����� ����� ���������� (��� ��������), ���� �������� �������� ���� �� ����� �������� (��� ��������). ��������� �������� ������� � �������, ����� ����� �������� �������� ������������ ������� (�������, ��������).
~~~
