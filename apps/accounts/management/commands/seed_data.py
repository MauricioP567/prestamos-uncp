from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from apps.equipos.models import Equipo, Laboratorio
from apps.prestamos.models import Prestamo

User = get_user_model()


class Command(BaseCommand):
    help = "Pobla la BD con datos de prueba: 10+ equipos, 5 usuarios, 15+ préstamos."

    def handle(self, *args, **kwargs):
        self.stdout.write("→ Creando laboratorios...")
        labs = []
        for nombre, ubic in [
            ("Laboratorio A", "Pabellón I - 2do piso"),
            ("Laboratorio B", "Pabellón I - 3er piso"),
            ("Laboratorio C", "Pabellón II - 1er piso"),
            ("Laboratorio D", "Pabellón II - 2do piso"),
            ("Laboratorio E", "Pabellón III - 1er piso"),
        ]:
            obj, _ = Laboratorio.objects.get_or_create(nombre=nombre, defaults={"ubicacion": ubic})
            labs.append(obj)

        self.stdout.write("→ Creando usuarios...")
        usuarios = []
        datos = [
            ("admin", "Admin", "Sistema", "admin@uncp.edu.pe", "U0001", "12345678", "admin"),
            ("docente1", "Juan", "Pérez", "jperez@uncp.edu.pe", "U0002", "23456789", "docente"),
            ("docente2", "María", "García", "mgarcia@uncp.edu.pe", "U0003", "34567890", "docente"),
            ("asistente1", "Luis", "Torres", "ltorres@uncp.edu.pe", "U0004", "45678901", "asistente"),
            ("asistente2", "Ana", "Rojas", "arojas@uncp.edu.pe", "U0005", "56789012", "asistente"),
        ]
        for username, first, last, email, codigo, dni, rol in datos:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first, "last_name": last, "email": email,
                    "codigo_uncp": codigo, "dni": dni, "rol": rol,
                },
            )
            if created:
                user.set_password(f"{rol}12345" if rol != "admin" else "admin12345")
                if rol == "admin":
                    user.is_staff = True
                    user.is_superuser = True
                user.save()
            usuarios.append(user)

        self.stdout.write("→ Creando equipos...")
        equipos_data = [
            ("UNCP-0001", "Laptop HP ProBook", "HP", "450 G9", "Laptop", "operativo", 0, 5),
            ("UNCP-0002", "Laptop Lenovo ThinkPad", "Lenovo", "E14", "Laptop", "operativo", 1, 4),
            ("UNCP-0003", "Proyector Epson", "Epson", "PowerLite X49", "Proyector", "operativo", 2, 3),
            ("UNCP-0004", "Cámara Sony Alpha", "Sony", "A6400", "Cámara", "operativo", 3, 2),
            ("UNCP-0005", "Kit Arduino UNO", "Arduino", "R3", "Kit desarrollo", "operativo", 0, 10),
            ("UNCP-0006", "Router Cisco", "Cisco", "RV340", "Router", "operativo", 1, 6),
            ("UNCP-0007", "Switch TP-Link", "TP-Link", "TL-SG108", "Switch", "mantenimiento", 2, 4),
            ("UNCP-0008", "Laptop Dell Latitude", "Dell", "5420", "Laptop", "operativo", 3, 3),
            ("UNCP-0009", "Proyector BenQ", "BenQ", "MS560", "Proyector", "baja", 0, 1),
            ("UNCP-0010", "Kit Raspberry Pi 4", "Raspberry", "Pi 4B", "Kit desarrollo", "operativo", 1, 8),
            ("UNCP-0011", "Cámara Canon EOS", "Canon", "Rebel T7", "Cámara", "operativo", 4, 2),
            ("UNCP-0012", "Switch Cisco Catalyst", "Cisco", "C1000", "Switch", "operativo", 2, 5),
        ]
        for codigo, nombre, marca, modelo, cat, estado, idx_lab, stock in equipos_data:
            Equipo.objects.get_or_create(
                codigo_patrimonial=codigo,
                defaults={
                    "nombre": nombre, "marca": marca, "modelo": modelo,
                    "categoria": cat, "estado": estado, "laboratorio": labs[idx_lab],
                    "stock_total": stock,
                    "ultimo_mantenimiento": timezone.localdate() - timedelta(days=random.randint(10, 200)),
                },
            )

        self.stdout.write("→ Creando préstamos...")
        docentes = [u for u in usuarios if u.rol == "docente"]
        eqs = list(Equipo.objects.filter(estado="operativo"))
        for i in range(15):
            docente = random.choice(docentes)
            equipo = random.choice(eqs)
            f_prestamo = timezone.localdate() - timedelta(days=random.randint(1, 40))
            f_devolucion = f_prestamo + timedelta(days=random.randint(5, 20))
            estado = random.choices(
                ["activo", "devuelto", "vencido"], weights=[5, 7, 3]
            )[0]
            Prestamo.objects.get_or_create(
                docente=docente, equipo=equipo, fecha_prestamo=f_prestamo,
                defaults={
                    "cantidad": random.randint(1, 2),
                    "fecha_devolucion": f_devolucion,
                    "estado": estado,
                    "observaciones": "Generado por seed_data.",
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f"✓ Listo. Equipos: {Equipo.objects.count()} | "
            f"Usuarios: {User.objects.count()} | "
            f"Préstamos: {Prestamo.objects.count()}"
        ))
        self.stdout.write(self.style.NOTICE(
            "Credenciales: admin/admin12345 · docente1/docente12345 · asistente1/asistente12345"
        ))