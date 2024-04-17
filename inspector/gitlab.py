import fnmatch
import os
import re

import gitlab

GITLAB_API_BASE_URL = "https://gitlab.com"
ACCESS_TOKEN = os.environ.get("GITLAB_ACCESS_TOKEN", 'glpat-nxSrwBgumZ9RDwz9BwmD')

PYTHON_VERSION_FILES_LIST = os.environ.get("PYTHON_VERSION_FILES_LIST", {r".*Dockerfile.*", "Jenkinsfile", "pipeline.groovy"})
CDK_VERSION_FILES_LIST = os.environ.get("CDK_VERSION_FILES_LIST", {"package.json"})

PYTHON_NODE_VERSION_PATTERN = os.environ.get("PYTHON_NODE_VERSION_PATTERN", r'python-\d+(\.\d+)?_node-\d+(\.\d+)?')
CDK_VERSION_1_PATTERN = os.environ.get("CDK_VERSION_1_PATTERN", r'.*@aws-cdk.*')

# https://python-gitlab.readthedocs.io/en/stable/api-usage.html
gi = gitlab.Gitlab()
gl = gitlab.Gitlab('https://gitlab.com', private_token=ACCESS_TOKEN)


class GitlabInspector:

    def __init__(self):
        try:
            gl.auth()
        except gitlab.exceptions.GitlabAuthenticationError as e:
            print(f'Authentication error : {e}')

    #### Shared methods ####
    @staticmethod
    def get_software_name(value):
        if 'python' in value or 'node' in value:
            return "python-node"
        elif 'aws' in value:
            return 'aws-cdk'
        else:
            return None

    def check_version_of_software(self, matched_files, pattern=''):
        version_data = []

        for mfile in matched_files:
            try:
                with open(mfile, 'r') as file:
                    contents = file.read()
                    matches = re.search(pattern, contents)
                    if matches:
                        version_data.append(VersionData(file.name, self.get_software_name(pattern), matches.group(0)))
            except IOError as e:
                print(f"Error: {e}")
                return None

        return version_data

    def check_remote_version_of_software(self, project_id, matched_files, pattern=''):
        version_data = []

        for mfile in matched_files:
            try:
                raw_content = GitlabInspector.get_remote_raw_file_content(gl.projects.get(project_id), mfile)
                matches = re.search(pattern, raw_content.decode('utf-8'))
                if matches:
                    version_data.append(VersionData(mfile, self.get_software_name(pattern), matches.group(0)))
            except Exception as e:
                print(f"Error: {e}")
                return None

        return version_data

    @staticmethod
    def append_version_data_to_file(version_data, file_path):
        try:
            with open(file_path, 'a') as file:
                if version_data is not None:
                    for data in version_data:
                        file.write(f"{data}")
            print(f"Dictionary contents appended to '{file_path}' successfully.")
        except IOError as e:
            print(f"Error: {e}")

    @staticmethod
    def get_patterns(software_type):
        file_pattern = ''
        version_pattern = ''
        if software_type == 'python_node':
            file_pattern = PYTHON_VERSION_FILES_LIST
            version_pattern = PYTHON_NODE_VERSION_PATTERN
        elif software_type == 'cdk':
            file_pattern = CDK_VERSION_FILES_LIST
            version_pattern = CDK_VERSION_1_PATTERN
        return file_pattern, version_pattern

        #### Remote queries ####

    @staticmethod
    def get_remote_raw_file_content(project, file_path):
        return project.files.raw(file_path, ref='main')

    @staticmethod
    def get_remote_projects():
        projects = gl.projects.list(all=False)
        return [prj for prj in projects]

    @staticmethod
    def get_remote_project_ids(projects):
        return [prj.id for prj in projects]

    @staticmethod
    def filter_remote_files_on_pattern(project_id, file_pattern, query='search_query'):
        files = gl.projects.get(project_id).repository_tree(path='', recursive=False, search=query)
        matched_files = [file['name'] for file in files for pattern in file_pattern if re.match(pattern, file.get('name'))]

        return matched_files

    def record_versions_in_all_remote_project_repos(self, software_type, output_file, query_project=False, project_ids=None):
        if query_project:
            project_ids = GitlabInspector.get_remote_project_ids(GitlabInspector.get_remote_projects())
        else:
            print(f'Query for the project_ids: {project_ids}')

        file_pattern, version_pattern = self.get_patterns(software_type)

        for prj_id in project_ids:
            matched_files = GitlabInspector.filter_remote_files_on_pattern(prj_id, file_pattern)
            software_versions = self.check_remote_version_of_software(prj_id, matched_files, version_pattern)
            self.append_version_data_to_file(software_versions, output_file)
            print(f'Versions({version_pattern}) have successfully been recorded for project_id: {id}')

    #### Local queries - project has been cloned locally ####
    @staticmethod
    def find_matched_files_in_local_project(project_path, file_patterns):
        matched_files = []

        for root, dirs, files in os.walk(project_path):
            for pattern in file_patterns:
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        matched_files.append(os.path.join(root, filename))

        return matched_files

    def record_versions_in_local_project_repos(self, project, software_type, output_file):
        file_pattern, version_pattern = self.get_patterns(software_type)

        matched_files = self.find_matched_files_in_local_project(project, file_pattern)
        software_versions = self.check_version_of_software(matched_files, version_pattern)
        self.append_version_data_to_file(software_versions, output_file)

        print(f'Versions({version_pattern}) have successfully been recorded for: {project}')


class VersionData:
    def __init__(self, filename, software, version):
        self.filename = filename
        self.software = software
        self.version = version

    def __repr__(self):
        return f"VersionData(filename={self.filename}, software={self.software}, version={self.version})"
