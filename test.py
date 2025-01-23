from src.modules import System
from src.modules import SystemService
from src.modules.mplc4_current_project import MPLC4CurrentProject
from src.modules.psql_manager import PSQLManager
from src.modules.arm_report_maker import ArmReportMaker

# print(PSQLManager.get_size())
# print(System.get_diskspace_usage(True))
# print(System.get_dir_size("/opt/mplc4/log"))

ArmReportMaker.dir_size_unit = "GB"
ArmReportMaker.table_width = 50

if __name__ == "__main__":
        tracked_services = "mplc4", "mplc4-cleaner", "postgresql"
        services_states = (
            (service.name, service.state) for service in \
            (SystemService(name) for name in tracked_services)
        )
        disk_usage_summary = System.get_diskspace_usage(True)

        report = ArmReportMaker.make_report(
            services_states = tuple(services_states),
            cpu_usage = System.get_cpu_usage(),
            ram_usage = System.get_ram_usage(),
            disk_usage_detail = disk_usage_summary,
            psql_size = PSQLManager.get_size(),
            mplc4_log_size = System.get_dir_size("/opt/mplc4/log"),
            sys_log_size = System.get_dir_size("/var/log/journal"),
            mplc4_project_info = MPLC4CurrentProject().info,
            host = System.run_cmd("hostname -i").stdout.strip()
        )
        print(report)
