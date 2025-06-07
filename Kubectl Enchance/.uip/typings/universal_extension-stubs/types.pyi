from typing import TypedDict


class Credential(TypedDict):
    user: str
    password: str
    keyLocation: str
    passphrase: str
    token: str
    ...


class SapConnection(TypedDict):
    name: str
    description: str
    sap_connection_type: str
    # Specific Application Server
    sap_client: str
    sap_ashost: str
    sap_sysnr: str
    sap_gwhost: str
    sap_gwserv: str
    # Load Balancing
    sap_mshost: str
    sap_r3name: str
    sap_use_symbolic_names: str
    # Common
    sap_mysapsso2: str
    sap_x509cert: str
    sap_saprouter: str
    sap_snc_mode: str
    sap_snc_lib: str
    sap_snc_myname: str
    sap_snc_partnername: str
    sap_snc_qop: str
    sap_snc_sso: str
    ...


class DBConnection(TypedDict):
    name: str
    description: str
    type: str
    url: str
    driver: str
    max_rows: int
    credentials: Credential
    ...


class ExtensionFields(TypedDict):
    jobname: str
    namespace: str
    yaml_file: str
    monitor_job: bool
    fetch_log: bool
    delete_job: bool
    ...


class UipNls(object):
    task_variables: dict
    is_triggered: bool
    trigger_id: str
    instance_id: str
    monitor_id: str
    ...
