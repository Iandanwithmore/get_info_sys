from datetime import datetime

# equipo
import socket
import getpass
import subprocess
import platform
import psutil
import uuid

# show dialog
import tkinter as tk


def get_device_data():
    # Get the system information
    system = platform.uname()

    # Obtener la dirección IP del host local
    ip_address = socket.gethostbyname(socket.gethostname())

    # Obtener el nombre del host
    host_name = socket.gethostname()

    # Obtener el dominio del host
    domain_name = socket.getfqdn()

    # Obtener el usuario actualmente conectado
    user_name = getpass.getuser()

    # Obtener la dirección MAC de la interfaz de red
    mac_address = ":".join(
        [
            uuid.UUID(int=uuid.getnode()).hex[-12:].upper()[i : i + 2]
            for i in range(0, 12, 2)
        ]
    )

    # Obtener el espacio libre y utilizado del disco duro
    disk = psutil.disk_usage("/")
    disk_total = round(disk.total / (1024.0**3), 2)
    disk_used = round(disk.used / (1024.0**3), 2)

    # Obtener la cantidad de memoria RAM
    # ram = round(psutil.virtual_memory().total / (1024.0**3), 2)
    memory = psutil.virtual_memory()
    return (
        "###Dirección IP\n"
        f">{ip_address}\n"
        "###Nombre del host\n"
        f">{host_name}\n"
        "###Dominio\n"
        f">{domain_name}"
        "###Usuario\n"
        f">{user_name}"
        "###Dirección MAC\n"
        f">{mac_address}\n"
        "###System\n"
        f">{system.system}\n"
        "###Node Name\n"
        f">{system.node}\n"
        "###Release\n"
        f">{system.release}\n"
        "###Version\n"
        f">{system.version}\n"
        "###Machine\n"
        f">{system.machine}\n"
        "###Processor\n"
        f">{system.processor}\n"
        "###Espacio total en disco\n"
        f">{disk_total}\n"
        "###Espacio utilizado en disco\n"
        f">{disk_used}\n"
        "###Memoria RAM\n"
        f">{memory.total}/{memory.available}/{memory.percent}/{memory.used}/{memory.free}"
    )


def get_network_data():
    # Obtener la versión del sistema operativo
    os_version = platform.system()

    if os_version == "Windows":
        # Para Windows, usar el comando ipconfig /all
        dhcp_config = subprocess.check_output("ipconfig /all", shell=True)
        dhcp_config = dhcp_config.strip().decode("cp1252")
        os_version += platform.release()
    elif os_version == "Linux":
        # Para Linux, usar el comando ifconfig
        dhcp_config = subprocess.check_output("ifconfig", shell=True)
        dhcp_config = dhcp_config.strip().decode("utf-8")
        os_version += platform.version()
    elif os_version == "Darwin":
        # Para Mac, usar el comando ifconfig
        dhcp_config = subprocess.check_output("ifconfig", shell=True)
        dhcp_config = dhcp_config.strip().decode("utf-8")
        os_version += platform.version()
    else:
        dhcp_config = (
            "No se puede obtener la configuración de red en este sistema operativo."
        )
    dhcp_config.replace("   ", ">")
    return f"###Sistema operativo\n{os_version}\n###Configuración DHCP\n{dhcp_config}"


def get_services_and_ports():
    services_and_ports = {}
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["pid", "name", "connections"])
            pname = pinfo["name"]
            if pname.endswith(".exe"):
                pname = pname[:-4]
            for conn in pinfo["connections"]:
                if conn.status == psutil.CONN_LISTEN:
                    laddr = conn.laddr
                    if laddr.ip == "0.0.0.0":
                        ip = "localhost"
                    else:
                        ip = laddr.ip
                    if pname not in services_and_ports:
                        services_and_ports[pname] = []
                    services_and_ports[pname].append((laddr.ip, laddr.port))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    data_services = str()
    for service in services_and_ports:
        data_services += f"###{service}\n"
        for ip, port in services_and_ports[service]:
            data_services += f"{ip}:{port}\n"
    return data_services


def get_installed_programs():
    programs = {}
    if psutil.WINDOWS:
        cmd = 'reg query "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall" /s /f "DisplayName" /t REG_SZ /d /e'
        output = subprocess.check_output(cmd, shell=True, text=True)
        for line in output.split("\n"):
            if "DisplayName" in line:
                program_name = line.split("    ")[-1]
                programs[program_name] = ""
            elif "DisplayVersion" in line:
                program_version = line.split("    ")[-1]
                programs[program_name] = program_version
    elif psutil.LINUX:
        cmd = "dpkg-query -W -f='${Package}\t${Version}\n'"
        output = subprocess.check_output(cmd, shell=True, text=True)
        for line in output.split("\n"):
            if line:
                fields = line.split()
                program_name = fields[0]
                program_version = fields[1]
                programs[program_name] = program_version
    return "".join(
        [
            f"###{program_name}\n{program_version}\n"
            for program_name, program_version in programs.items()
        ]
    )


def show_popup():
    popup = tk.Tk()
    popup.wm_title("Tarea completada")
    label = tk.Label(
        popup, text="Se a creado el archivo SYSTEM_CONFIG en el directorio actual."
    )
    label.pack(side="top", fill="x", pady=10)
    button = tk.Button(popup, text="Cerrar", command=popup.destroy)
    button.pack()
    popup.mainloop()


def main():
    host_name = socket.gethostname()
    timestamp = datetime.now()
    device = get_device_data()
    network = get_network_data()
    services = get_services_and_ports()
    ptograms = get_installed_programs()
    system_file = open(host_name + ".txt", "w")
    system_file.writelines(
        f"#Timestamp:{timestamp}\n{device}\n{network}\n{services}\n{ptograms}"
    )
    system_file.close()
    show_popup()


if __name__ == "__main__":
    main()
