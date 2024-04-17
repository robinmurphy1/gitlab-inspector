from unittest import TestCase

from inspector.gitlab import GitlabInspector
from inspector.gitlab import VersionData


class Test(TestCase):

    def test_check_version_of_software_python(self):
        inspector = GitlabInspector()
        matched_files = {'/home/robin/Projects/ppl-code/upgrades/account-service/Jenkinsfile',
                         '/home/robin/Projects/ppl-code/upgrades/account-service/python.Dockerfile',
                         '/home/robin/Projects/ppl-code/upgrades/account-service/account_service/Dockerfile'}

        versions = inspector.check_version_of_software(matched_files, r"python-\d+(\.\d+)?_node-\d+(\.\d+)?")
        print(versions)

    def test_check_version_of_software_cdk(self):
        inspector = GitlabInspector()
        matched_files = {'/home/robin/Projects/ppl-code/upgrades/account-service/package.json',
                         '/home/robin/Projects/ppl-code/upgrades/account-service/cdk/package.json',
                         '/home/robin/Projects/ppl-code/upgrades/account-service/openapi-spec/package.json'}

        versions = inspector.check_version_of_software(matched_files, r".*@aws-cdk.*")
        print(versions)

    def test_append_dict_to_file(self):
        inspector = GitlabInspector()

        version_data = {VersionData('/home/robin/Projects/ppl-code/upgrades/account-service/python.Dockerfile', 'python-node', 'version=python-3.11_node-18'),
                        VersionData('/home/robin/Projects/ppl-code/upgrades/account-service/account_service/Dockerfile', 'python-node',
                                    'version=python-3.11_node-18')}
        inspector.append_version_data_to_file(version_data, './version_data.txt')

    def test_get_remote_projects(self):
        inspector = GitlabInspector()
        print(inspector.get_remote_projects())
        # self.fail()

    def test_get_remote_project_ids(self):
        inspector = GitlabInspector()
        print(inspector.get_remote_project_ids(inspector.get_remote_projects()))

    def test_filter_remote_files_on_pattern(self):
        inspector = GitlabInspector()
        print(inspector.filter_remote_files_on_pattern('56750708', r".*Dockerfile.*", 'search_query'))

    def test_record_versions_in_all_remote_project_repos(self):
        inspector = GitlabInspector()
        inspector.record_versions_in_all_remote_project_repos('python_node', './remote-versions.txt', query_project=False, project_ids=[56750708])

    def test_get_software_name(self):
        inspector = GitlabInspector()
        print(inspector.get_software_name("aws-\d+(\.\d+)?-\d+(\.\d+)?"))

    def test_find_matched_files_in_local_project_python(self):
        inspector = GitlabInspector()
        file_patterns = {r"*Dockerfile*", "Jenkinsfile", "pipeline.groovy"}
        print(inspector.find_matched_files_in_local_project('/home/robin/Projects/ppl-code/upgrades/account-service', file_patterns))
        # self.fail()

    def test_find_matched_files_in_local_project_cdk(self):
        inspector = GitlabInspector()
        file_patterns = {r"package.json"}
        print(inspector.find_matched_files_in_local_project('/home/robin/Projects/ppl-code/upgrades/account-service', file_patterns))
        # self.fail()

    def test_report_versions_in_local_project_repos_python(self):
        inspector = GitlabInspector()
        inspector.record_versions_in_local_project_repos('/home/robin/Projects/ppl-code/upgrades/account-service', 'python_node', './version_data.txt')

    def test_report_versions_in_local_project_repos_cdk(self):
        inspector = GitlabInspector()
        inspector.record_versions_in_local_project_repos('/home/robin/Projects/ppl-code/upgrades/account-service', 'cdk', './version_data.txt')
