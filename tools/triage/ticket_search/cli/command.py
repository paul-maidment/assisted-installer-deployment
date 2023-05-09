from workflow_data import WorkflowData


class Command:
    def run(self, workflow_data: "WorkflowData"):
        pass

    def get_command_key(self) -> str:
        pass

    def get_friendly_name(self) -> str:
        pass
