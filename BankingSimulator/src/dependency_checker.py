import json
import os

class DependencyChecker:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_params = self.load_config_txt()
        self.directory_path = self.config_params.get('directory_path', './configs/')
        self.processes = {}
        self.errors = []
        self.warnings = []

    def load_config_txt(self):
        config_params = {}
        with open(self.config_path, 'r') as file:  # Corrected variable name here
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split('=')
                config_params[key] = value
        return config_params

    def load_json_file(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def load_all_processes(self):
        for filename in os.listdir(self.directory_path):
            if filename.endswith(".json"):
                file_path = os.path.join(self.directory_path, filename)
                data = self.load_json_file(file_path)
                for process in data.get('processes', []):
                    self.processes[process['process_id']] = {
                        "process": process,
                        "file": filename
                    }

    def check_dependencies(self):
        for process_id, data in self.processes.items():
            process = data["process"]
            # Check for unmet dependencies
            for dependency in process.get('dependencies', []):
                if dependency not in self.processes:
                    self.errors.append(
                        f"Process '{process_id}' in file '{data['file']}' has unmet dependency: '{dependency}'"
                    )
            # Check for processes with both dependencies and a schedule_time
            if process.get('dependencies') and process.get('schedule_time'):
                self.warnings.append(
                    f"Process '{process_id}' in file '{data['file']}' has both dependencies and a schedule_time: '{process['schedule_time']}'"
                )

    def report_issues(self):
        if not self.errors and not self.warnings:
            print("All dependencies are satisfied and no schedule_time conflicts.")
        else:
            if self.errors:
                print("Dependency Errors:")
                for error in self.errors:
                    print(error)
            if self.warnings:
                print("\nSchedule Time Warnings:")
                for warning in self.warnings:
                    print(warning)

    def run_check(self):
        self.load_all_processes()
        self.check_dependencies()
        self.report_issues()

# Usage
if __name__ == "__main__":
    config_txt_path = "./config.txt"
    checker = DependencyChecker(config_txt_path)
    checker.run_check()
