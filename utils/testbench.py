#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import base64
import dataclasses
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
import urllib3  # type: ignore
from utils.util import (
    AbstractAction,
)
from utils.config_model import (
    CliReporterConfig,
    Configuration,
)


class Connection:
    def __init__(
        self,
        server_url: str,
        verify: Union[bool, str],
        basicAuth: Optional[str] = None,
        loginname: Optional[str] = None,
        password: Optional[str] = None,
        job_timeout_sec: int = 4 * 60 * 60,
        connection_timeout_sec: Optional[int] = None,
        actions: Optional[List] = None,
        **kwargs,
    ):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.server_url = server_url
        if basicAuth:
            credentials = base64.b64decode(basicAuth.encode()).decode("utf-8")
            self.loginname, self.password = credentials.split(":", 1)
        else:
            self.loginname = loginname or ""
            self.password = password or ""
        self.job_timeout_sec = job_timeout_sec
        self.action_log: List[AbstractAction] = []
        self.actions_to_trigger: List[dict] = actions or []
        self.actions_to_wait_for: List[AbstractAction] = []
        self.actions_to_finish: List[AbstractAction] = []
        self.connection_timeout = connection_timeout_sec
        self.verify_ssl = verify
        self._session = None

    @property
    def session(self):
        self._session = requests.Session()
        self._session.auth = (self.loginname, self.password)
        self._session.headers.update(
            {"Content-Type": "application/vnd.testbench+json; charset=utf-8"}
        )
        self._session.hooks = {
            "response": lambda r, *args, **kwargs: r.raise_for_status()
        }
        self._session.mount("http://", TimeoutHTTPAdapter(self.connection_timeout))
        self._session.mount("https://", TimeoutHTTPAdapter(self.connection_timeout))
        self._session.verify = self.verify_ssl
        return self._session

    def close(self):
        self.session.close()

    def export(self) -> Configuration:
        basic_auth = base64.b64encode(
            f"{self.loginname}:{self.password}".encode()
        ).decode()
        return Configuration(
            server_url=self.server_url,
            verify=bool(self.session.verify),
            basicAuth=basic_auth,
            actions=[
                action.export()
                for action in self.action_log
                if action.export() is not None
            ],
        )

    def add_action(self, action: AbstractAction):
        self.action_log.append(action)

    def check_is_identical(self, other) -> bool:
        return bool(
            self.server_url == other.server_url
            and self.loginname == other.loginname
            and self.password == other.password
        )

    def check_is_working(self) -> bool:
        response = self.session.get(
            f"{self.server_url}projects",
            params={
                "includeTOVs": "false",
                "includeCycles": "false",
            },
        )

        response.json()

        return True

    def get_all_projects(self) -> Dict[str, Any]:
        all_projects = dict(
            self.session.get(
                f"{self.server_url}projects",
                params={"includeTOVs": "true", "includeCycles": "true"},
            ).json()
        )
        all_projects["projects"].sort(key=lambda proj: proj["name"].casefold())
        return all_projects

    def get_all_filters(self) -> List[dict]:
        all_filters = self.session.get(
            f"{self.server_url}filters",
        )

        return all_filters.json()

    def get_exp_job_result(self, job_id):
        report_generation_status = self.get_job_result("job/", job_id)
        if report_generation_status is None:
            return None
        result = report_generation_status["result"]
        if "Right" in result:
            return result["Right"]
        raise AssertionError(result)

    def get_job_result(self, path: str, job_id: str):
        report_generation_status = self.session.get(
            f"{self.server_url}{path}{job_id}",
        )
        return report_generation_status.json()["completion"]

    def get_xml_report_data(self, report_tmp_name: str) -> bytes:
        report = self.session.get(
            f"{self.server_url}xmlReport/{report_tmp_name}",
        )

        return report.content

    def get_all_testers_of_project(self, project_key: str) -> List[dict]:
        return [
            member
            for member in self.get_all_members_of_project(project_key)
            if "Tester" in member["value"]["membership"]["roles"]
        ]

    def get_all_members_of_project(self, project_key: str) -> List[dict]:
        all_project_members = self.session.get(
            f"{self.server_url}project/{project_key}/members",
        )

        return all_project_members.json()

    def get_imp_job_result(self, job_id):
        report_import_status = self.get_job_result(
            "executionResultsImporterJob/", job_id
        )
        if report_import_status is None:
            return None
        result = report_import_status["result"]
        if "Right" in result:
            return result["Right"]
        raise AssertionError(result)

    def get_test_cycle_structure(self, cycle_key: str) -> List[dict]:
        test_cycle_structure = self.session.get(
            f"{self.server_url}cycle/{cycle_key}/structure",
        )
        return test_cycle_structure.json()

    def get_tov_structure(self, tovKey: str) -> List[dict]:
        tov_structure = self.session.get(
            f"{self.server_url}tov/{tovKey}/structure",
        )
        return tov_structure.json()

    def get_test_cases(
        self, test_case_set_structure: Dict[str, Any]
    ) -> Dict[str, Dict]:
        spec_test_cases = self.get_spec_test_cases(
            test_case_set_structure["TestCaseSet_structure"]["key"]["serial"],
            test_case_set_structure["spec"]["Specification_key"]["serial"],
        )
        test_cases = {tc["uniqueID"]: tc for tc in spec_test_cases}
        if not test_case_set_structure.get("exec"):
            return {"spec": test_cases}
        exec_test_cases = self.get_exec_test_cases(
            test_case_set_structure["TestCaseSet_structure"]["key"]["serial"],
            test_case_set_structure["exec"]["Execution_key"]["serial"],
        )
        test_cases_execs = {tc["uniqueID"]: tc for tc in exec_test_cases}
        equal_lists = False not in [
            test_cases.get(uid, {}).get("testCaseSpecificationKey")["serial"]
            == tc["paramCombPK"]["serial"]
            for uid, tc in test_cases_execs.items()
        ]
        return {
            "spec": test_cases,
            "exec": test_cases_execs,
            "equal_lists": equal_lists,
        }

    def get_spec_test_cases(
        self, testCaseSetKey: str, specificationKey: str
    ) -> List[dict]:
        spec_test_cases = self.session.get(
            f"{self.server_url}testCaseSets/"
            f"{testCaseSetKey}/specifications/"
            f"{specificationKey}/testCases",
        )
        return spec_test_cases.json()

    def get_exec_test_cases(self, testCaseSetKey: str, executionKey: str) -> List[dict]:
        exec_test_cases = self.session.get(
            f"{self.server_url}testCaseSets/"
            f"{testCaseSetKey}/executions/"
            f"{executionKey}/testCases",
        )
        return exec_test_cases.json()


def login(server="", login="", pwd="") -> Connection:  # noqa: C901, PLR0912
    if server and login and pwd:
        credentials = {
            "server_url": server,
            "verify": False,
            "loginname": login,
            "password": pwd,
        }
    else:
        credentials = {}

    while True:
        connection = Connection(**credentials)
        try:
            if connection.check_is_working():
                return connection

        except requests.HTTPError:
            print("ERROR")

        except (requests.ConnectionError, requests.exceptions.MissingSchema):
            print("ERROR")

        except requests.exceptions.Timeout:
            print("ERROR")


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, timeout: Optional[int] = 60, *args, **kwargs):
        self.timeout = timeout
        super().__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        kwargs["timeout"] = self.timeout
        return super().send(*args, **kwargs)


class JobTimeout(requests.exceptions.Timeout):
    pass


class ConnectionLog:
    def __init__(self):
        self.connections: List[Connection] = []

    @property
    def len(self) -> int:  # noqa: A003
        return len(self.connections)

    @property
    def active_connection(self) -> Connection:
        return self.connections[-1]

    def next(self):  # noqa: A003
        self.connections = self.connections[1:] + self.connections[:1]

    def remove(self, connection):
        self.connections.remove(connection)

    def add_connection(self, new_connection: Connection):
        self.connections.append(new_connection)

    def export_as_json(self, output_file_path: str):
        print("Generating JSON export")
        export_config = CliReporterConfig(
            configuration=[connection.export() for connection in self.connections]
        )

        with Path(output_file_path).open("w") as output_file:
            json.dump(dataclasses.asdict(export_config), output_file, indent=2)
